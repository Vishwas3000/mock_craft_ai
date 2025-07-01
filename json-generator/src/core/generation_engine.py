# src/core/generation_engine.py
"""Core JSON Generation Engine"""

import json
import asyncio
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import logging
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .schema_analyzer import SchemaAnalyzer, SchemaAnalysis
from .prompt_engineer import PromptEngineer, PromptStrategy
from .output_parser import OutputParser, OutputValidator, ValidationLevel, ValidationResult
from .llm_manager import LLMManager
from .base_llm import GenerationConfig

logger = logging.getLogger(__name__)
console = Console()

class GenerationMode(Enum):
    """Generation modes"""
    SINGLE = "single"          # Generate one record at a time
    BATCH = "batch"            # Generate multiple records at once
    PROGRESSIVE = "progressive" # Generate and refine iteratively

@dataclass
class GenerationRequest:
    """Request for JSON generation"""
    schema: Dict[str, Any]
    context: str
    count: int = 10
    mode: GenerationMode = GenerationMode.BATCH
    strategy: PromptStrategy = PromptStrategy.CHAIN_OF_THOUGHT
    use_multi_strategy: bool = False  # New field for multi-strategy
    validation_level: ValidationLevel = ValidationLevel.MODERATE
    model: Optional[str] = None
    include_examples: bool = True
    max_retries: int = 3

@dataclass
class GenerationResult:
    """Result of JSON generation"""
    success: bool
    data: Optional[List[Dict]]
    validation_result: Optional[ValidationResult]
    metadata: Dict[str, Any]
    errors: List[str]

class JSONGenerationEngine:
    """Main engine for JSON data generation"""
    
    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager
        self.schema_analyzer = SchemaAnalyzer()
        self.prompt_engineer = PromptEngineer()
        self.output_parser = OutputParser()
        self.validators = {}  # Cache validators for schemas
        
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """Generate JSON data based on request"""
        logger.info(f"Starting generation: {request.count} records for {request.context}")
        
        try:
            # Step 1: Analyze schema
            with console.status("[bold blue]Analyzing schema..."):
                analysis = self.schema_analyzer.analyze(request.schema, request.context)
                console.print(f"[green]✓[/green] Schema analyzed: {analysis.total_fields} fields, "
                            f"complexity: {analysis.complexity_score:.2f}")
            
            # Step 2: Build prompt
            with console.status("[bold blue]Building optimized prompt..."):
                # Determine if we should use multi-strategy based on complexity
                use_multi = request.use_multi_strategy or (
                    analysis.complexity_score > 0.5 and request.count > 5
                )
                
                prompt = self.prompt_engineer.build_prompt(
                    schema=request.schema,
                    analysis=analysis,
                    context=request.context,
                    count=request.count,
                    strategy=request.strategy,
                    include_examples=request.include_examples,
                    use_multi_strategy=use_multi
                )
                
                # Optimize for selected model
                model_type = request.model or self.llm_manager.default_model
                prompt = self.prompt_engineer.optimize_for_model(prompt, model_type)
                
                strategy_desc = "multi-strategy" if use_multi else request.strategy.value
                console.print(f"[green]✓[/green] Prompt optimized for {model_type} using {strategy_desc}")
            
            # Step 3: Generate data
            generated_data = await self._generate_with_mode(
                prompt=prompt,
                request=request,
                analysis=analysis
            )
            
            if not generated_data:
                return GenerationResult(
                    success=False,
                    data=None,
                    validation_result=None,
                    metadata={"mode": request.mode.value},
                    errors=["Generation failed"]
                )
            
            # Step 4: Parse output
            with console.status("[bold blue]Parsing generated data..."):
                parse_result = self.output_parser.parse(generated_data, request.count)
                
                if not parse_result.success:
                    console.print(f"[yellow]⚠[/yellow] Parsing failed, attempting recovery...")
                    
                    # Try with different prompt strategy if multi-strategy enabled
                    if request.use_multi_strategy and request.max_retries > 0:
                        request.max_retries -= 1
                        request.strategy = PromptStrategy.STRUCTURED  # Try more explicit
                        return await self.generate(request)
                    
                    return GenerationResult(
                        success=False,
                        data=None,
                        validation_result=None,
                        metadata={
                            "mode": request.mode.value,
                            "parse_errors": parse_result.errors
                        },
                        errors=parse_result.errors
                    )
                
                console.print(f"[green]✓[/green] Successfully parsed {len(parse_result.data) if isinstance(parse_result.data, list) else 1} records")
            
            # Step 5: Validate data
            validator = self._get_validator(analysis)
            validation_result = validator.validate(parse_result.data, request.validation_level)
            
            if not validation_result.is_valid and request.validation_level != ValidationLevel.LENIENT:
                console.print(f"[yellow]⚠[/yellow] Validation issues found, attempting to fix...")
                
                # Try to fix common issues
                fixed_data = validator.fix_common_issues(parse_result.data)
                re_validation = validator.validate(fixed_data, request.validation_level)
                
                if re_validation.is_valid:
                    console.print("[green]✓[/green] Fixed validation issues")
                    parse_result.data = fixed_data
                    validation_result = re_validation
                elif request.use_multi_strategy and request.max_retries > 0:
                    # Retry with different strategy
                    console.print("[yellow]Retrying with different strategy...[/yellow]")
                    request.max_retries -= 1
                    request.strategy = PromptStrategy.FEW_SHOT  # Try with examples
                    return await self.generate(request)
            
            # Prepare final result
            data = parse_result.data if isinstance(parse_result.data, list) else [parse_result.data]
            
            return GenerationResult(
                success=validation_result.score > 0.5,
                data=data,
                validation_result=validation_result,
                metadata={
                    "mode": request.mode.value,
                    "model_used": request.model or self.llm_manager.default_model,
                    "strategy_used": "multi-strategy" if request.use_multi_strategy else request.strategy.value,
                    "extraction_method": parse_result.extraction_method,
                    "complexity_score": analysis.complexity_score,
                    "validation_score": validation_result.score
                },
                errors=validation_result.errors
            )
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return GenerationResult(
                success=False,
                data=None,
                validation_result=None,
                metadata={"error": str(e)},
                errors=[str(e)]
            )
    
    async def _generate_with_mode(
        self,
        prompt: str,
        request: GenerationRequest,
        analysis: SchemaAnalysis
    ) -> Optional[str]:
        """Generate data based on mode"""
        config = GenerationConfig(
            temperature=0.7 if analysis.complexity_score > 0.5 else 0.5,
            max_tokens=min(2000 * request.count, 8000),
            response_format="json" if request.model == "openai" else None
        )
        
        try:
            if request.mode == GenerationMode.SINGLE:
                # Generate one at a time
                results = []
                for i in range(request.count):
                    console.print(f"[cyan]Generating record {i+1}/{request.count}...[/cyan]")
                    response = await self.llm_manager.generate(
                        prompt.replace(f"{request.count} records", "1 record"),
                        model=request.model,
                        config=config
                    )
                    results.append(response.content)
                return "[" + ",".join(results) + "]"
                
            elif request.mode == GenerationMode.BATCH:
                # Generate all at once
                console.print(f"[cyan]Generating {request.count} records in batch...[/cyan]")
                response = await self.llm_manager.generate(
                    prompt,
                    model=request.model,
                    config=config
                )
                return response.content
                
            elif request.mode == GenerationMode.PROGRESSIVE:
                # Generate and refine
                console.print("[cyan]Progressive generation...[/cyan]")
                
                # First pass
                initial_response = await self.llm_manager.generate(
                    prompt,
                    model=request.model,
                    config=config
                )
                
                # Parse and validate
                parse_result = self.output_parser.parse(initial_response.content, request.count)
                if not parse_result.success:
                    return initial_response.content
                
                # Refine if needed
                validator = self._get_validator(analysis)
                validation = validator.validate(parse_result.data, ValidationLevel.LENIENT)
                
                if validation.score < 0.8:
                    console.print("[cyan]Refining output...[/cyan]")
                    refinement_prompt = self._build_refinement_prompt(
                        parse_result.data,
                        validation,
                        request.schema
                    )
                    
                    refined_response = await self.llm_manager.generate(
                        refinement_prompt,
                        model=request.model,
                        config=config
                    )
                    return refined_response.content
                
                return initial_response.content
                
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return None
    
    def _get_validator(self, analysis: SchemaAnalysis) -> OutputValidator:
        """Get or create validator for schema"""
        # Cache validators by schema hash
        schema_hash = hash(json.dumps(analysis.fields, sort_keys=True, default=str))
        
        if schema_hash not in self.validators:
            self.validators[schema_hash] = OutputValidator(analysis)
            
        return self.validators[schema_hash]
    
    def _build_refinement_prompt(
        self,
        data: Union[Dict, List[Dict]],
        validation: ValidationResult,
        schema: Dict
    ) -> str:
        """Build prompt to refine generated data"""
        issues = "\n".join(f"- {error}" for error in validation.errors[:5])
        
        return f"""The following generated data has some issues that need correction:

```json
{json.dumps(data, indent=2)}
```

Issues found:
{issues}

Please fix these issues while maintaining the overall structure and realism of the data.
The corrected data should follow this schema:
```json
{json.dumps(schema, indent=2)}
```

Return only the corrected JSON data."""
    
    async def generate_adaptive(
        self,
        request: GenerationRequest,
        max_attempts: int = 3
    ) -> GenerationResult:
        """Generate with adaptive strategy selection"""
        request.use_multi_strategy = True
        attempts = []
        
        for attempt in range(max_attempts):
            console.print(f"\n[bold]Attempt {attempt + 1}/{max_attempts}[/bold]")
            
            # Adjust request based on previous attempts
            if attempts:
                last_attempt = attempts[-1]
                if last_attempt.validation_result:
                    # Adjust strategy based on validation score
                    if last_attempt.validation_result.score < 0.3:
                        request.strategy = PromptStrategy.STRUCTURED
                    elif last_attempt.validation_result.score < 0.6:
                        request.strategy = PromptStrategy.FEW_SHOT
                    else:
                        request.strategy = PromptStrategy.CHAIN_OF_THOUGHT
            
            result = await self.generate(request)
            attempts.append(result)
            
            if result.success and result.validation_result.score > 0.8:
                console.print(f"[green]✓ Success with score: {result.validation_result.score:.2f}[/green]")
                return result
            
            console.print(f"[yellow]Score: {result.validation_result.score:.2f}, retrying...[/yellow]")
        
        # Return best attempt
        best_attempt = max(attempts, key=lambda x: x.validation_result.score if x.validation_result else 0)
        return best_attempt