# src/core/prompt_engineer.py
"""Advanced Prompt Engineering for JSON Generation"""

import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from langchain.prompts import PromptTemplate, FewShotPromptTemplate
from langchain.prompts.example_selector import SemanticSimilarityExampleSelector
from langchain.embeddings import OpenAIEmbeddings

from .schema_analyzer import SchemaAnalysis, FieldAnalysis, DataType, PatternType
from src.utils.processing.uuid_processor import get_uuid_instructions, detect_uuid_fields

class PromptStrategy(Enum):
    """Different prompt strategies for generation"""
    ZERO_SHOT = "zero_shot"
    FEW_SHOT = "few_shot"
    CHAIN_OF_THOUGHT = "chain_of_thought"
    STRUCTURED = "structured"
    CONVERSATIONAL = "conversational"

@dataclass
class PromptComponents:
    """Components of a prompt"""
    system_instruction: str
    context_description: str
    schema_description: str
    constraints: List[str]
    examples: List[Dict[str, Any]]
    output_format: str
    additional_instructions: List[str]

class PromptEngineer:
    """Advanced prompt engineering for optimal JSON generation"""
    
    def __init__(self, embedding_model=None):
        self.embedding_model = embedding_model
        self.example_library = self._load_example_library()
        self.pattern_templates = self._init_pattern_templates()
        self.strategy_templates = self._init_strategy_templates()
        self.multi_strategy_templates = self._init_multi_strategy_templates()
        
    def _load_example_library(self) -> Dict[str, List[Dict]]:
        """Load library of examples for different domains"""
        return {
            "e-commerce": [
                {
                    "productId": "PROD-12345",
                    "name": "Wireless Bluetooth Headphones",
                    "price": 79.99,
                    "category": "Electronics",
                    "inStock": True,
                    "ratings": {"average": 4.5, "count": 324}
                },
                {
                    "orderId": "ORD-67890",
                    "customerId": "CUST-11111",
                    "items": [
                        {"productId": "PROD-12345", "quantity": 2, "price": 79.99}
                    ],
                    "total": 159.98,
                    "status": "shipped"
                }
            ],
            "healthcare": [
                {
                    "patientId": "PT000123",
                    "firstName": "John",
                    "lastName": "Doe",
                    "dateOfBirth": "1980-05-15",
                    "conditions": ["hypertension", "diabetes"],
                    "medications": [
                        {"name": "Metformin", "dosage": "500mg", "frequency": "twice daily"}
                    ]
                }
            ],
            "finance": [
                {
                    "accountNumber": "1234567890",
                    "accountType": "savings",
                    "balance": 5432.10,
                    "transactions": [
                        {
                            "date": "2024-01-15",
                            "type": "deposit",
                            "amount": 1000.00,
                            "description": "Salary"
                        }
                    ]
                }
            ],
            "general": [
                {"id": "550e8400-e29b-41d4-a716-446655440000", "name": "Example", "value": 100, "active": True}
            ]
        }
    
    def _init_pattern_templates(self) -> Dict[PatternType, str]:
        """Initialize templates for different pattern types"""
        return {
            PatternType.EMAIL: "realistic email addresses in format: firstname.lastname@domain.com",
            PatternType.PHONE: "phone numbers in format: +1-555-123-4567",
            PatternType.URL: "valid URLs starting with https://",
            PatternType.DATE: "dates in ISO format: YYYY-MM-DD",
            PatternType.DATETIME: "datetime in ISO format: YYYY-MM-DDTHH:MM:SSZ",
            PatternType.UUID: "valid UUID v4 format (e.g., 550e8400-e29b-41d4-a716-446655440000)",
            PatternType.CURRENCY: "currency values with 2 decimal places",
            PatternType.PERCENTAGE: "percentage values between 0 and 100",
            PatternType.NAME: "realistic person names",
            PatternType.ADDRESS: "realistic street addresses"
        }
    
    def _init_strategy_templates(self) -> Dict[PromptStrategy, PromptTemplate]:
        """Initialize prompt templates for different strategies"""
        templates = {}
        
        # Zero-shot template
        templates[PromptStrategy.ZERO_SHOT] = PromptTemplate(
            input_variables=["context", "schema", "count", "constraints"],
            template="""Generate {count} realistic JSON records for {context}.

Schema structure:
{schema}

Requirements:
{constraints}

Generate diverse, realistic data that follows the schema exactly."""
        )
        
        # Chain-of-thought template
        templates[PromptStrategy.CHAIN_OF_THOUGHT] = PromptTemplate(
            input_variables=["context", "schema", "count", "analysis"],
            template="""Let's generate {count} JSON records for {context} step by step.

First, let me understand the schema:
{schema}

Schema analysis:
{analysis}

Now I'll generate realistic data by:
1. Identifying the domain and typical values
2. Ensuring all required fields are present
3. Using appropriate patterns for each field
4. Maintaining consistency across records
5. Adding realistic variations

Generated records:"""
        )
        
        # Structured template
        templates[PromptStrategy.STRUCTURED] = PromptTemplate(
            input_variables=["context", "schema", "count", "field_specs"],
            template="""Generate {count} JSON records for {context}.

Schema: {schema}

Field specifications:
{field_specs}

Output format: JSON array of objects
Ensure: Valid JSON, diverse values, realistic data"""
        )
        
        return templates
    
    def _init_multi_strategy_templates(self) -> Dict[str, str]:
        """Initialize templates for combining multiple strategies"""
        return {
            "cot_few_shot": """Let me analyze this step by step.

First, I'll examine the schema and context:
{cot_analysis}

Here are relevant examples to guide the generation:
{few_shot_examples}

Now, I'll generate {count} records that follow the pattern:
{generation_instructions}

Generated data:""",
            
            "structured_cot": """I'll generate the data using a structured approach.

## Schema Analysis
{cot_analysis}

## Field Specifications
{structured_specs}

## Generation Process
1. I'll ensure each field matches its specification
2. I'll maintain consistency across records
3. I'll use realistic values appropriate for {context}

Generated JSON:""",
            
            "few_shot_structured": """Based on these examples:
{few_shot_examples}

And these field specifications:
{structured_specs}

I'll generate {count} similar records:""",
            
            "all_three": """I'll use a comprehensive approach to generate the data.

## Understanding (Chain of Thought)
{cot_analysis}

## Examples (Few-Shot Learning)
{few_shot_examples}

## Specifications (Structured Format)
{structured_specs}

## Generated Data
Following all the above guidelines:"""
        }
    
    def build_prompt(
        self,
        schema: Dict[str, Any],
        analysis: SchemaAnalysis,
        context: str,
        count: int = 10,
        strategy: PromptStrategy = PromptStrategy.CHAIN_OF_THOUGHT,
        include_examples: bool = True,
        use_multi_strategy: bool = False
    ) -> str:
        """Build optimized prompt for JSON generation
        
        Args:
            schema: The JSON schema to generate
            analysis: Schema analysis results
            context: Domain context
            count: Number of records to generate
            strategy: Single strategy to use (if not multi-strategy)
            include_examples: Whether to include examples
            use_multi_strategy: Whether to use multiple strategies
        """
        
        # Get components
        components = self._analyze_requirements(schema, analysis, context, count)
        
        # Check if we should use multi-strategy
        if use_multi_strategy:
            return self._build_multi_strategy_prompt(
                components, schema, analysis, context, count
            )
        
        # Otherwise use single strategy (backward compatible)
        if strategy == PromptStrategy.FEW_SHOT and include_examples:
            return self._build_few_shot_prompt(components, schema, context, count)
        elif strategy == PromptStrategy.CHAIN_OF_THOUGHT:
            return self._build_cot_prompt(components, schema, analysis, context, count)
        elif strategy == PromptStrategy.STRUCTURED:
            return self._build_structured_prompt(components, schema, analysis, context, count)
        else:
            return self._build_zero_shot_prompt(components, schema, context, count)
    
    def _analyze_requirements(
        self,
        schema: Dict[str, Any],
        analysis: SchemaAnalysis,
        context: str,
        count: int
    ) -> PromptComponents:
        """Analyze requirements and build prompt components"""
        
        # Build system instruction
        system_instruction = self._build_system_instruction(analysis.complexity_score)
        
        # Build context description
        context_description = self._enhance_context_description(context, analysis)
        
        # Build schema description
        schema_description = self._build_schema_description(schema, analysis)
        
        # Build constraints
        constraints = self._build_constraints(analysis)
        
        # Select examples
        examples = self._select_relevant_examples(context, schema)
        
        # Determine output format
        output_format = self._determine_output_format(count)
        
        # Additional instructions
        additional_instructions = self._build_additional_instructions(analysis)
        
        return PromptComponents(
            system_instruction=system_instruction,
            context_description=context_description,
            schema_description=schema_description,
            constraints=constraints,
            examples=examples,
            output_format=output_format,
            additional_instructions=additional_instructions
        )
    
    def _build_system_instruction(self, complexity_score: float) -> str:
        """Build system instruction based on complexity"""
        if complexity_score > 0.7:
            return "You are an expert data generator specializing in complex, realistic JSON structures. Pay careful attention to relationships and constraints."
        elif complexity_score > 0.3:
            return "You are a data generator creating realistic JSON records. Ensure consistency and appropriate values."
        else:
            return "You are a JSON data generator. Create simple, valid records."
    
    def _enhance_context_description(self, context: str, analysis: SchemaAnalysis) -> str:
        """Enhance context with analysis insights"""
        base = f"Domain: {context}"
        
        hints = analysis.get_generation_hints()
        if hints['special_patterns']:
            base += f"\nSpecial patterns detected: {', '.join(hints['special_patterns'].keys())}"
        
        if analysis.relationships:
            base += f"\nRelationships: {len(analysis.relationships)} detected"
            
        return base
    
    def _build_schema_description(self, schema: Dict, analysis: SchemaAnalysis) -> str:
        """Build detailed schema description"""
        lines = ["Schema structure with field details:"]
        
        for field_name, field_analysis in analysis.fields.items():
            line = f"- {field_name}: {field_analysis.data_type.value}"
            
            if field_analysis.pattern_type:
                pattern_desc = self.pattern_templates.get(
                    field_analysis.pattern_type,
                    field_analysis.pattern_type.value
                )
                line += f" ({pattern_desc})"
            
            if field_analysis.constraints.enum_values:
                line += f" [options: {', '.join(map(str, field_analysis.constraints.enum_values))}]"
            
            if field_analysis.data_type == DataType.ARRAY:
                line += f" of {field_analysis.array_item_type.value if field_analysis.array_item_type else 'items'}"
                
            lines.append(line)
        
        return "\n".join(lines)
    
    def _build_constraints(self, analysis: SchemaAnalysis) -> List[str]:
        """Build constraint list"""
        constraints = [
            "All fields must match the exact schema structure",
            "Use realistic, diverse values",
            "Maintain consistency within each record"
        ]
        
        # Add UUID-specific constraints
        uuid_instructions = get_uuid_instructions()
        if uuid_instructions.strip():
            constraints.append(uuid_instructions.strip())
        
        # Add specific constraints
        for field_name, field_analysis in analysis.fields.items():
            if field_analysis.constraints.min_value is not None:
                constraints.append(
                    f"{field_name}: minimum value {field_analysis.constraints.min_value}"
                )
            if field_analysis.constraints.max_value is not None:
                constraints.append(
                    f"{field_name}: maximum value {field_analysis.constraints.max_value}"
                )
            if field_analysis.constraints.pattern:
                constraints.append(
                    f"{field_name}: must match pattern {field_analysis.constraints.pattern}"
                )
        
        if analysis.relationships:
            constraints.append("Maintain referential integrity for related fields")
            
        return constraints
    
    def _select_relevant_examples(self, context: str, schema: Dict) -> List[Dict]:
        """Select relevant examples from library"""
        # Find best matching domain
        context_lower = context.lower()
        
        for domain, examples in self.example_library.items():
            if domain in context_lower:
                return examples[:2]  # Return up to 2 examples
        
        # Default to general examples
        return self.example_library["general"]
    
    def _determine_output_format(self, count: int) -> str:
        """Determine output format instructions"""
        if count == 1:
            return "Output a single JSON object"
        else:
            return f"Output a JSON array containing exactly {count} objects"
    
    def _build_additional_instructions(self, analysis: SchemaAnalysis) -> List[str]:
        """Build additional instructions based on analysis"""
        instructions = []
        
        if analysis.has_arrays:
            instructions.append("For array fields, include 2-5 items with varied content")
        
        if analysis.has_nested_objects:
            instructions.append("Ensure nested objects are complete and valid")
        
        if any(f.pattern_type == PatternType.EMAIL for f in analysis.fields.values()):
            instructions.append("Use realistic email addresses with common domains")
        
        if any(f.pattern_type == PatternType.NAME for f in analysis.fields.values()):
            instructions.append("Use diverse, culturally appropriate names")
        
        # UUID instructions are handled in constraints section
        
        return instructions
    
    def _build_few_shot_prompt(
        self,
        components: PromptComponents,
        schema: Dict,
        context: str,
        count: int
    ) -> str:
        """Build few-shot prompt with examples"""
        example_text = "Here are some examples:\n\n"
        
        for i, example in enumerate(components.examples[:2], 1):
            example_text += f"Example {i}:\n```json\n{json.dumps(example, indent=2)}\n```\n\n"
        
        prompt = f"""{components.system_instruction}

{components.context_description}

{example_text}Now generate {count} similar records following this schema:
```json
{json.dumps(schema, indent=2)}
```

{components.schema_description}

Requirements:
{chr(10).join(f'- {c}' for c in components.constraints)}

{components.output_format}
"""
        
        if components.additional_instructions:
            prompt += f"\n\nAdditional notes:\n"
            prompt += "\n".join(f"- {inst}" for inst in components.additional_instructions)
        
        return prompt
    
    def _build_cot_prompt(
        self,
        components: PromptComponents,
        schema: Dict,
        analysis: SchemaAnalysis,
        context: str,
        count: int
    ) -> str:
        """Build chain-of-thought prompt"""
        template = self.strategy_templates[PromptStrategy.CHAIN_OF_THOUGHT]
        
        analysis_summary = f"""- Complexity: {analysis.complexity_score:.2f}
- Total fields: {analysis.total_fields}
- Special patterns: {len([f for f in analysis.fields.values() if f.pattern_type])}
- Arrays: {'Yes' if analysis.has_arrays else 'No'}
- Nested objects: {'Yes' if analysis.has_nested_objects else 'No'}"""
        
        return template.format(
            context=context,
            schema=json.dumps(schema, indent=2),
            count=count,
            analysis=analysis_summary
        )
    
    def _build_structured_prompt(
        self,
        components: PromptComponents,
        schema: Dict,
        analysis: SchemaAnalysis,
        context: str,
        count: int
    ) -> str:
        """Build structured prompt with field specifications"""
        field_specs = []
        
        for field_name, field_analysis in analysis.fields.items():
            spec = f"{field_name}:"
            spec += f"\n  Type: {field_analysis.data_type.value}"
            
            if field_analysis.pattern_type:
                spec += f"\n  Pattern: {self.pattern_templates.get(field_analysis.pattern_type, 'custom')}"
            
            if field_analysis.constraints.min_value is not None:
                spec += f"\n  Min: {field_analysis.constraints.min_value}"
            if field_analysis.constraints.max_value is not None:
                spec += f"\n  Max: {field_analysis.constraints.max_value}"
            
            if field_analysis.example_value is not None:
                spec += f"\n  Example: {field_analysis.example_value}"
                
            field_specs.append(spec)
        
        template = self.strategy_templates[PromptStrategy.STRUCTURED]
        return template.format(
            context=context,
            schema=json.dumps(schema, indent=2),
            count=count,
            field_specs="\n\n".join(field_specs)
        )
    
    def _build_zero_shot_prompt(
        self,
        components: PromptComponents,
        schema: Dict,
        context: str,
        count: int
    ) -> str:
        """Build zero-shot prompt"""
        template = self.strategy_templates[PromptStrategy.ZERO_SHOT]
        
        constraints_text = "\n".join(f"- {c}" for c in components.constraints)
        
        return template.format(
            context=context,
            schema=json.dumps(schema, indent=2),
            count=count,
            constraints=constraints_text
        )
    
    def optimize_for_model(self, prompt: str, model_type: str) -> str:
        """Optimize prompt for specific model type"""
        if model_type == "openai":
            # OpenAI models work well with structured instructions
            return prompt
        elif model_type == "anthropic":
            # Claude prefers conversational style
            return f"I need your help generating JSON data.\n\n{prompt}\n\nPlease ensure the output is valid JSON."
        elif model_type == "llama":
            # Llama models need clear delimiters
            return f"### Instruction:\n{prompt}\n\n### Response:\n"
        else:
            return prompt
    
    def create_validation_prompt(self, generated_data: List[Dict], schema: Dict) -> str:
        """Create prompt to validate generated data"""
        return f"""Please validate this generated JSON data against the schema:

Schema:
```json
{json.dumps(schema, indent=2)}
```

Generated data:
```json
{json.dumps(generated_data, indent=2)}
```

Check for:
1. Schema compliance
2. Data realism
3. Pattern consistency
4. Value appropriateness

Provide a validation report with any issues found."""
    
    def _build_multi_strategy_prompt(
        self,
        components: PromptComponents,
        schema: Dict[str, Any],
        analysis: SchemaAnalysis,
        context: str,
        count: int
    ) -> str:
        """Build a prompt using multiple strategies automatically selected"""
        
        # Select optimal strategies based on complexity and context
        strategies = self._select_optimal_strategies(analysis, context, count)
        
        # Build strategy components with defaults for missing ones
        strategy_components = {
            "cot_analysis": "No detailed analysis available.",
            "few_shot_examples": "No specific examples available.",
            "structured_specs": "No structured specifications available."
        }
        
        if PromptStrategy.CHAIN_OF_THOUGHT in strategies:
            strategy_components["cot_analysis"] = self._build_cot_analysis_component(
                analysis, context
            )
        
        if PromptStrategy.FEW_SHOT in strategies:
            strategy_components["few_shot_examples"] = self._build_few_shot_component(
                components.examples
            )
        
        if PromptStrategy.STRUCTURED in strategies:
            strategy_components["structured_specs"] = self._build_structured_component(
                analysis
            )
        
        # Determine which template to use
        template_key = self._get_multi_strategy_template_key(strategies)
        template = self.multi_strategy_templates.get(template_key, self.multi_strategy_templates["all_three"])
        
        # Format the template
        return template.format(
            context=context,
            count=count,
            generation_instructions=f"Generate {count} unique, realistic records for {context}",
            **strategy_components
        )
    
    def _select_optimal_strategies(
        self,
        analysis: SchemaAnalysis,
        context: str,
        count: int
    ) -> List[PromptStrategy]:
        """Select optimal combination of strategies based on analysis"""
        strategies = []
        
        # Always use Chain-of-Thought for complex schemas
        if analysis.complexity_score > 0.5:
            strategies.append(PromptStrategy.CHAIN_OF_THOUGHT)
        
        # Use Few-Shot if we have good examples or generating many records
        if count > 5 or any(domain in context.lower() for domain in self.example_library.keys()):
            strategies.append(PromptStrategy.FEW_SHOT)
        
        # Use Structured for schemas with special patterns or constraints
        if any(f.pattern_type for f in analysis.fields.values()) or analysis.complexity_score > 0.3:
            strategies.append(PromptStrategy.STRUCTURED)
        
        # Fallback to at least one strategy
        if not strategies:
            strategies.append(PromptStrategy.CHAIN_OF_THOUGHT)
        
        return strategies
    
    def _build_cot_analysis_component(self, analysis: SchemaAnalysis, context: str) -> str:
        """Build the Chain-of-Thought analysis component"""
        lines = [
            f"The schema represents {context} data with {analysis.total_fields} fields.",
            f"Complexity level: {'High' if analysis.complexity_score > 0.7 else 'Moderate' if analysis.complexity_score > 0.3 else 'Simple'}",
            ""
        ]
        
        # Add pattern analysis
        patterns = [(f, fa.pattern_type) for f, fa in analysis.fields.items() if fa.pattern_type]
        if patterns:
            lines.append("Key patterns to follow:")
            for field, pattern in patterns:
                lines.append(f"- {field}: {pattern.value}")
            lines.append("")
        
        # Add relationship analysis
        if analysis.relationships:
            lines.append("Relationships to maintain:")
            for rel in analysis.relationships:
                lines.append(f"- {rel[0]} relates to {rel[1]}")
        
        return "\n".join(lines)
    
    def _build_few_shot_component(self, examples: List[Dict]) -> str:
        """Build the few-shot examples component"""
        if not examples:
            return "No specific examples available, follow the schema structure."
        
        lines = []
        for i, example in enumerate(examples[:2], 1):
            lines.append(f"Example {i}:")
            lines.append("```json")
            lines.append(json.dumps(example, indent=2))
            lines.append("```")
            lines.append("")
        
        return "\n".join(lines)
    
    def _build_structured_component(self, analysis: SchemaAnalysis) -> str:
        """Build the structured specifications component"""
        lines = []
        
        for field_name, field_analysis in analysis.fields.items():
            lines.append(f"**{field_name}**:")
            lines.append(f"  - Type: {field_analysis.data_type.value}")
            
            if field_analysis.pattern_type:
                pattern_desc = self.pattern_templates.get(field_analysis.pattern_type, "custom pattern")
                lines.append(f"  - Pattern: {pattern_desc}")
            
            if field_analysis.constraints.min_value is not None:
                lines.append(f"  - Min: {field_analysis.constraints.min_value}")
            if field_analysis.constraints.max_value is not None:
                lines.append(f"  - Max: {field_analysis.constraints.max_value}")
            
            lines.append("")
        
        return "\n".join(lines)
    
    def _get_multi_strategy_template_key(self, strategies: List[PromptStrategy]) -> str:
        """Get the appropriate template key for the strategy combination"""
        strategy_set = set(strategies)
        
        if strategy_set == {PromptStrategy.CHAIN_OF_THOUGHT, PromptStrategy.FEW_SHOT}:
            return "cot_few_shot"
        elif strategy_set == {PromptStrategy.STRUCTURED, PromptStrategy.CHAIN_OF_THOUGHT}:
            return "structured_cot"
        elif strategy_set == {PromptStrategy.FEW_SHOT, PromptStrategy.STRUCTURED}:
            return "few_shot_structured"
        else:
            return "all_three"