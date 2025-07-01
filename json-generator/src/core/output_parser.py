"""Output parsing and validation for generated JSON"""

import json
import re
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import jsonschema
from jsonschema import validate, ValidationError
import logging

from .schema_analyzer import SchemaAnalysis, DataType, PatternType

logger = logging.getLogger(__name__)

class ValidationLevel(Enum):
    """Validation strictness levels"""
    STRICT = "strict"      # All constraints must be met
    MODERATE = "moderate"  # Most constraints, some flexibility
    LENIENT = "lenient"    # Basic structure validation only

@dataclass
class ValidationResult:
    """Result of validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    score: float  # 0-1 score of how well it matches
    fixed_data: Optional[Any] = None

@dataclass
class ParseResult:
    """Result of parsing LLM output"""
    success: bool
    data: Optional[Union[Dict, List[Dict]]]
    raw_text: str
    errors: List[str]
    extraction_method: str

class OutputParser:
    """Parse and validate LLM outputs"""
    
    def __init__(self):
        self.json_extractors = [
            self._extract_json_block,
            self._extract_json_code_block,
            self._extract_raw_json,
            self._extract_with_regex,
            self._extract_with_repairs
        ]
        
    def parse(self, llm_output: str, expected_count: int = 1) -> ParseResult:
        """Parse LLM output to extract JSON data"""
        errors = []
        
        # Try each extraction method
        for extractor in self.json_extractors:
            try:
                data = extractor(llm_output)
                if data is not None:
                    # Verify we got the expected structure
                    if expected_count == 1 and isinstance(data, dict):
                        return ParseResult(
                            success=True,
                            data=data,
                            raw_text=llm_output,
                            errors=[],
                            extraction_method=extractor.__name__
                        )
                    elif expected_count > 1 and isinstance(data, list):
                        if len(data) == expected_count:
                            return ParseResult(
                                success=True,
                                data=data,
                                raw_text=llm_output,
                                errors=[],
                                extraction_method=extractor.__name__
                            )
                        else:
                            errors.append(f"Expected {expected_count} items, got {len(data)}")
                    elif expected_count > 1 and isinstance(data, dict):
                        # Single object when multiple expected - wrap in array
                        return ParseResult(
                            success=True,
                            data=[data],
                            raw_text=llm_output,
                            errors=["Wrapped single object in array"],
                            extraction_method=extractor.__name__
                        )
                        
            except Exception as e:
                errors.append(f"{extractor.__name__}: {str(e)}")
                continue
        
        # All methods failed
        return ParseResult(
            success=False,
            data=None,
            raw_text=llm_output,
            errors=errors,
            extraction_method="none"
        )
    
    def _extract_json_block(self, text: str) -> Optional[Union[Dict, List]]:
        """Extract JSON from ```json blocks"""
        pattern = r'```json\s*([\s\S]*?)\s*```'
        matches = re.findall(pattern, text, re.IGNORECASE)
        
        for match in matches:
            try:
                return json.loads(match)
            except:
                continue
        return None
    
    def _extract_json_code_block(self, text: str) -> Optional[Union[Dict, List]]:
        """Extract JSON from generic code blocks"""
        pattern = r'```\s*([\s\S]*?)\s*```'
        matches = re.findall(pattern, text)
        
        for match in matches:
            try:
                return json.loads(match)
            except:
                continue
        return None
    
    def _extract_raw_json(self, text: str) -> Optional[Union[Dict, List]]:
        """Try to parse the entire text as JSON"""
        try:
            return json.loads(text.strip())
        except:
            return None
    
    def _extract_with_regex(self, text: str) -> Optional[Union[Dict, List]]:
        """Extract JSON using regex patterns"""
        # Try to find JSON array
        array_pattern = r'\[\s*\{[^}]+\}(?:\s*,\s*\{[^}]+\})*\s*\]'
        array_matches = re.findall(array_pattern, text, re.DOTALL)
        
        for match in array_matches:
            try:
                return json.loads(match)
            except:
                continue
        
        # Try to find JSON object
        object_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        object_matches = re.findall(object_pattern, text)
        
        for match in object_matches:
            try:
                return json.loads(match)
            except:
                continue
                
        return None
    
    def _extract_with_repairs(self, text: str) -> Optional[Union[Dict, List]]:
        """Try to repair and extract JSON"""
        # Remove common LLM artifacts
        cleaned = text.strip()
        
        # Remove trailing commas
        cleaned = re.sub(r',\s*}', '}', cleaned)
        cleaned = re.sub(r',\s*]', ']', cleaned)
        
        # Fix single quotes to double quotes
        cleaned = re.sub(r"'([^']*)'", r'"\1"', cleaned)
        
        # Remove comments
        cleaned = re.sub(r'//.*$', '', cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r'/\*.*?\*/', '', cleaned, flags=re.DOTALL)
        
        # Try to find JSON structure
        start_idx = cleaned.find('[')
        if start_idx == -1:
            start_idx = cleaned.find('{')
        
        if start_idx != -1:
            # Find matching closing bracket
            bracket_count = 0
            in_string = False
            escape_next = False
            
            for i in range(start_idx, len(cleaned)):
                char = cleaned[i]
                
                if escape_next:
                    escape_next = False
                    continue
                    
                if char == '\\':
                    escape_next = True
                    continue
                    
                if char == '"' and not escape_next:
                    in_string = not in_string
                    continue
                    
                if not in_string:
                    if char in '[{':
                        bracket_count += 1
                    elif char in ']}':
                        bracket_count -= 1
                        
                    if bracket_count == 0:
                        try:
                            return json.loads(cleaned[start_idx:i+1])
                        except:
                            break
                            
        return None

class OutputValidator:
    """Validate generated JSON against schema and constraints"""
    
    def __init__(self, schema_analysis: SchemaAnalysis):
        self.schema_analysis = schema_analysis
        self.pattern_validators = self._init_pattern_validators()
        
    def _init_pattern_validators(self) -> Dict[PatternType, re.Pattern]:
        """Initialize regex validators for patterns"""
        return {
            PatternType.EMAIL: re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
            PatternType.PHONE: re.compile(r'^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{4,6}$'),
            PatternType.URL: re.compile(r'^https?://'),
            PatternType.DATE: re.compile(r'^\d{4}-\d{2}-\d{2}$'),
            PatternType.UUID: re.compile(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'),
            PatternType.POSTAL_CODE: re.compile(r'^\d{5}(-\d{4})?$')
        }
    
    def validate(
        self,
        data: Union[Dict, List[Dict]],
        level: ValidationLevel = ValidationLevel.MODERATE
    ) -> ValidationResult:
        """Validate generated data"""
        errors = []
        warnings = []
        score = 1.0
        
        # Ensure data is a list
        records = data if isinstance(data, list) else [data]
        
        for i, record in enumerate(records):
            record_errors, record_warnings, record_score = self._validate_record(
                record, i, level
            )
            errors.extend(record_errors)
            warnings.extend(record_warnings)
            score = min(score, record_score)
        
        # Calculate overall score
        if errors:
            score *= 0.5 ** len(errors)  # Exponential penalty for errors
        if warnings:
            score *= 0.9 ** len(warnings)  # Smaller penalty for warnings
            
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            score=max(0, score)
        )
    
    def _validate_record(
        self,
        record: Dict,
        index: int,
        level: ValidationLevel
    ) -> Tuple[List[str], List[str], float]:
        """Validate a single record"""
        errors = []
        warnings = []
        score = 1.0
        
        # Check required fields
        for field_name, field_analysis in self.schema_analysis.fields.items():
            if field_analysis.constraints.required and field_name not in record:
                errors.append(f"Record {index}: Missing required field '{field_name}'")
                score *= 0.8
        
        # Validate each field
        for field_name, value in record.items():
            if field_name not in self.schema_analysis.fields:
                if level == ValidationLevel.STRICT:
                    errors.append(f"Record {index}: Unknown field '{field_name}'")
                else:
                    warnings.append(f"Record {index}: Unknown field '{field_name}'")
                continue
                
            field_analysis = self.schema_analysis.fields[field_name]
            field_errors, field_warnings, field_score = self._validate_field(
                field_name, value, field_analysis, index, level
            )
            
            errors.extend(field_errors)
            warnings.extend(field_warnings)
            score *= field_score
            
        return errors, warnings, score
    
    def _validate_field(
        self,
        field_name: str,
        value: Any,
        field_analysis: 'FieldAnalysis',
        record_index: int,
        level: ValidationLevel
    ) -> Tuple[List[str], List[str], float]:
        """Validate a single field"""
        errors = []
        warnings = []
        score = 1.0
        
        # Type validation
        actual_type = self._get_actual_type(value)
        if actual_type != field_analysis.data_type:
            if level == ValidationLevel.STRICT:
                errors.append(
                    f"Record {record_index}: Field '{field_name}' type mismatch. "
                    f"Expected {field_analysis.data_type.value}, got {actual_type.value}"
                )
                score *= 0.7
            else:
                # Try type coercion in moderate/lenient mode
                coerced = self._try_coerce_type(value, field_analysis.data_type)
                if coerced is None:
                    errors.append(
                        f"Record {record_index}: Field '{field_name}' type cannot be coerced"
                    )
                    score *= 0.7
        
        # Pattern validation
        if field_analysis.pattern_type and isinstance(value, str):
            pattern = self.pattern_validators.get(field_analysis.pattern_type)
            if pattern and not pattern.match(value):
                if level != ValidationLevel.LENIENT:
                    errors.append(
                        f"Record {record_index}: Field '{field_name}' doesn't match "
                        f"pattern {field_analysis.pattern_type.value}"
                    )
                    score *= 0.8
        
        # Constraint validation
        if field_analysis.constraints:
            constraint_errors, constraint_score = self._validate_constraints(
                field_name, value, field_analysis.constraints, record_index, level
            )
            errors.extend(constraint_errors)
            score *= constraint_score
            
        return errors, warnings, score
    
    def _get_actual_type(self, value: Any) -> DataType:
        """Get the actual data type of a value"""
        if value is None:
            return DataType.NULL
        elif isinstance(value, bool):
            return DataType.BOOLEAN
        elif isinstance(value, int):
            return DataType.INTEGER
        elif isinstance(value, float):
            return DataType.NUMBER
        elif isinstance(value, str):
            return DataType.STRING
        elif isinstance(value, list):
            return DataType.ARRAY
        elif isinstance(value, dict):
            return DataType.OBJECT
        else:
            return DataType.UNKNOWN
    
    def _try_coerce_type(self, value: Any, target_type: DataType) -> Optional[Any]:
        """Try to coerce value to target type"""
        try:
            if target_type == DataType.STRING:
                return str(value)
            elif target_type == DataType.INTEGER:
                return int(value)
            elif target_type == DataType.NUMBER:
                return float(value)
            elif target_type == DataType.BOOLEAN:
                if isinstance(value, str):
                    return value.lower() in ('true', '1', 'yes')
                return bool(value)
            else:
                return None
        except:
            return None
    
    def _validate_constraints(
        self,
        field_name: str,
        value: Any,
        constraints: 'FieldConstraints',
        record_index: int,
        level: ValidationLevel
    ) -> Tuple[List[str], float]:
        """Validate field constraints"""
        errors = []
        score = 1.0
        
        # Numeric constraints
        if isinstance(value, (int, float)):
            if constraints.min_value is not None and value < constraints.min_value:
                errors.append(
                    f"Record {record_index}: Field '{field_name}' value {value} "
                    f"is below minimum {constraints.min_value}"
                )
                score *= 0.8
                
            if constraints.max_value is not None and value > constraints.max_value:
                errors.append(
                    f"Record {record_index}: Field '{field_name}' value {value} "
                    f"exceeds maximum {constraints.max_value}"
                )
                score *= 0.8
        
        # String constraints
        if isinstance(value, str):
            if constraints.min_length is not None and len(value) < constraints.min_length:
                errors.append(
                    f"Record {record_index}: Field '{field_name}' length {len(value)} "
                    f"is below minimum {constraints.min_length}"
                )
                score *= 0.9
                
            if constraints.max_length is not None and len(value) > constraints.max_length:
                errors.append(
                    f"Record {record_index}: Field '{field_name}' length {len(value)} "
                    f"exceeds maximum {constraints.max_length}"
                )
                score *= 0.9
        
        # Enum constraints
        if constraints.enum_values and value not in constraints.enum_values:
            if level != ValidationLevel.LENIENT:
                errors.append(
                    f"Record {record_index}: Field '{field_name}' value '{value}' "
                    f"not in allowed values: {constraints.enum_values}"
                )
                score *= 0.7
                
        return errors, score
    
    def fix_common_issues(self, data: Union[Dict, List[Dict]]) -> Union[Dict, List[Dict]]:
        """Attempt to fix common validation issues"""
        records = data if isinstance(data, list) else [data]
        fixed_records = []
        
        for record in records:
            fixed_record = {}
            
            for field_name, field_analysis in self.schema_analysis.fields.items():
                if field_name in record:
                    value = record[field_name]
                    
                    # Fix type issues
                    actual_type = self._get_actual_type(value)
                    if actual_type != field_analysis.data_type:
                        coerced = self._try_coerce_type(value, field_analysis.data_type)
                        if coerced is not None:
                            value = coerced
                    
                    # Fix pattern issues
                    if field_analysis.pattern_type == PatternType.EMAIL and isinstance(value, str):
                        if '@' not in value:
                            value = f"{value.replace(' ', '.')}@example.com"
                    
                    fixed_record[field_name] = value
                    
                elif field_analysis.constraints.required:
                    # Add missing required fields with default values
                    fixed_record[field_name] = self._get_default_value(field_analysis)
            
            fixed_records.append(fixed_record)
        
        return fixed_records if isinstance(data, list) else fixed_records[0]
    
    def _get_default_value(self, field_analysis: 'FieldAnalysis') -> Any:
        """Get default value for a field type"""
        if field_analysis.example_value is not None:
            return field_analysis.example_value
            
        defaults = {
            DataType.STRING: "default",
            DataType.INTEGER: 0,
            DataType.NUMBER: 0.0,
            DataType.BOOLEAN: False,
            DataType.ARRAY: [],
            DataType.OBJECT: {},
            DataType.NULL: None
        }
        
        return defaults.get(field_analysis.data_type, None) 