"""Advanced Schema Analysis for JSON Generation"""

import json
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import re
from collections import defaultdict

class DataType(Enum):
    """Supported data types"""
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    NULL = "null"
    UNKNOWN = "unknown"

class PatternType(Enum):
    """Common data patterns"""
    EMAIL = "email"
    PHONE = "phone"
    URL = "url"
    DATE = "date"
    DATETIME = "datetime"
    UUID = "uuid"
    IP_ADDRESS = "ip_address"
    POSTAL_CODE = "postal_code"
    CURRENCY = "currency"
    PERCENTAGE = "percentage"
    NAME = "name"
    ADDRESS = "address"
    CUSTOM = "custom"

@dataclass
class FieldConstraints:
    """Constraints for a field"""
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    enum_values: List[Any] = field(default_factory=list)
    required: bool = True
    unique: bool = False
    nullable: bool = False

@dataclass
class FieldAnalysis:
    """Analysis result for a single field"""
    field_name: str
    data_type: DataType
    pattern_type: Optional[PatternType] = None
    constraints: FieldConstraints = field(default_factory=FieldConstraints)
    example_value: Any = None
    nested_schema: Optional[Dict] = None
    array_item_type: Optional[DataType] = None
    array_item_analysis: Optional['FieldAnalysis'] = None
    description: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation"""
        result = {
            "field_name": self.field_name,
            "data_type": self.data_type.value,
            "pattern_type": self.pattern_type.value if self.pattern_type else None,
            "example_value": self.example_value,
            "constraints": {
                "required": self.constraints.required,
                "nullable": self.constraints.nullable
            }
        }
        
        # Add constraints if present
        if self.constraints.min_value is not None:
            result["constraints"]["min_value"] = self.constraints.min_value
        if self.constraints.max_value is not None:
            result["constraints"]["max_value"] = self.constraints.max_value
        if self.constraints.enum_values:
            result["constraints"]["enum"] = self.constraints.enum_values
            
        return result

@dataclass
class SchemaAnalysis:
    """Complete schema analysis result"""
    fields: Dict[str, FieldAnalysis]
    complexity_score: float
    depth: int
    total_fields: int
    has_arrays: bool
    has_nested_objects: bool
    relationships: List[Tuple[str, str]]  # Field relationships
    suggested_patterns: Dict[str, str]  # Field -> suggested pattern
    
    def get_generation_hints(self) -> Dict[str, Any]:
        """Get hints for generation"""
        return {
            "total_fields": self.total_fields,
            "complexity": "high" if self.complexity_score > 0.7 else "medium" if self.complexity_score > 0.3 else "low",
            "special_patterns": {
                field: analysis.pattern_type.value 
                for field, analysis in self.fields.items() 
                if analysis.pattern_type
            },
            "arrays": [
                field for field, analysis in self.fields.items()
                if analysis.data_type == DataType.ARRAY
            ],
            "nested_objects": [
                field for field, analysis in self.fields.items()
                if analysis.data_type == DataType.OBJECT and analysis.nested_schema
            ]
        }

class SchemaAnalyzer:
    """Analyzes JSON schemas to understand structure and patterns"""
    
    def __init__(self):
        self.pattern_matchers = self._init_pattern_matchers()
        self.type_inference_rules = self._init_type_inference()
        
    def _init_pattern_matchers(self) -> Dict[PatternType, re.Pattern]:
        """Initialize regex patterns for common data types"""
        return {
            PatternType.EMAIL: re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
            PatternType.PHONE: re.compile(r'^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{4,6}$'),
            PatternType.URL: re.compile(r'^https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b'),
            PatternType.DATE: re.compile(r'^\d{4}-\d{2}-\d{2}$'),
            PatternType.DATETIME: re.compile(r'^\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}'),
            PatternType.UUID: re.compile(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'),
            PatternType.IP_ADDRESS: re.compile(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'),
            PatternType.POSTAL_CODE: re.compile(r'^\d{5}(-\d{4})?$'),
        }
    
    def _init_type_inference(self) -> Dict[str, PatternType]:
        """Initialize type inference based on field names"""
        return {
            'email': PatternType.EMAIL,
            'mail': PatternType.EMAIL,
            'phone': PatternType.PHONE,
            'telephone': PatternType.PHONE,
            'mobile': PatternType.PHONE,
            'url': PatternType.URL,
            'website': PatternType.URL,
            'link': PatternType.URL,
            'date': PatternType.DATE,
            'datetime': PatternType.DATETIME,
            'timestamp': PatternType.DATETIME,
            'created_at': PatternType.DATETIME,
            'updated_at': PatternType.DATETIME,
            'uuid': PatternType.UUID,
            'id': PatternType.UUID,
            'guid': PatternType.UUID,
            'ip': PatternType.IP_ADDRESS,
            'ip_address': PatternType.IP_ADDRESS,
            'postal_code': PatternType.POSTAL_CODE,
            'zip': PatternType.POSTAL_CODE,
            'zipcode': PatternType.POSTAL_CODE,
            'price': PatternType.CURRENCY,
            'cost': PatternType.CURRENCY,
            'amount': PatternType.CURRENCY,
            'percentage': PatternType.PERCENTAGE,
            'percent': PatternType.PERCENTAGE,
            'rate': PatternType.PERCENTAGE,
            'name': PatternType.NAME,
            'first_name': PatternType.NAME,
            'last_name': PatternType.NAME,
            'full_name': PatternType.NAME,
            'address': PatternType.ADDRESS,
            'street': PatternType.ADDRESS,
            'city': PatternType.ADDRESS,
            'country': PatternType.ADDRESS,
        }
    
    def analyze(self, schema: Dict[str, Any], context: Optional[str] = None) -> SchemaAnalysis:
        """Analyze a JSON schema or example"""
        fields = {}
        relationships = []
        
        # Analyze each field
        for field_name, field_value in schema.items():
            field_analysis = self._analyze_field(field_name, field_value, context)
            fields[field_name] = field_analysis
        
        # Detect relationships
        relationships = self._detect_relationships(fields)
        
        # Calculate metrics
        complexity_score = self._calculate_complexity(fields)
        depth = self._calculate_depth(schema)
        
        return SchemaAnalysis(
            fields=fields,
            complexity_score=complexity_score,
            depth=depth,
            total_fields=len(fields),
            has_arrays=any(f.data_type == DataType.ARRAY for f in fields.values()),
            has_nested_objects=any(f.data_type == DataType.OBJECT and f.nested_schema for f in fields.values()),
            relationships=relationships,
            suggested_patterns=self._suggest_patterns(fields, context)
        )
    
    def _analyze_field(self, field_name: str, field_value: Any, context: Optional[str] = None) -> FieldAnalysis:
        """Analyze a single field"""
        # Determine data type
        data_type = self._infer_data_type(field_value)
        
        # Initialize field analysis
        field_analysis = FieldAnalysis(
            field_name=field_name,
            data_type=data_type,
            example_value=field_value
        )
        
        # Analyze based on type
        if data_type == DataType.STRING:
            field_analysis.pattern_type = self._detect_pattern(field_name, field_value)
            field_analysis.constraints.min_length = 1
            field_analysis.constraints.max_length = 1000  # Default max
            
            # Adjust constraints based on pattern
            if field_analysis.pattern_type == PatternType.EMAIL:
                field_analysis.constraints.max_length = 254
            elif field_analysis.pattern_type == PatternType.UUID:
                field_analysis.constraints.min_length = 36
                field_analysis.constraints.max_length = 36
                
        elif data_type == DataType.NUMBER or data_type == DataType.INTEGER:
            field_analysis.constraints.min_value = self._infer_min_value(field_name, field_value)
            field_analysis.constraints.max_value = self._infer_max_value(field_name, field_value)
            
        elif data_type == DataType.ARRAY:
            if field_value:  # Non-empty array
                # Analyze array items
                item_type = self._infer_data_type(field_value[0])
                field_analysis.array_item_type = item_type
                
                if item_type == DataType.OBJECT:
                    # Analyze nested object structure
                    field_analysis.array_item_analysis = self._analyze_field(
                        f"{field_name}[0]", field_value[0], context
                    )
                    
        elif data_type == DataType.OBJECT:
            # Analyze nested object
            field_analysis.nested_schema = self._analyze_nested_object(field_value)
            
        # Add context-based enhancements
        if context:
            field_analysis = self._enhance_with_context(field_analysis, context)
            
        return field_analysis
    
    def _infer_data_type(self, value: Any) -> DataType:
        """Infer data type from value"""
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
    
    def _detect_pattern(self, field_name: str, value: str) -> Optional[PatternType]:
        """Detect pattern from field name and value"""
        if not isinstance(value, str):
            return None
            
        # First, try to infer from field name
        field_lower = field_name.lower()
        for key, pattern in self.type_inference_rules.items():
            if key in field_lower:
                return pattern
        
        # Then, try regex matching on value
        for pattern_type, regex in self.pattern_matchers.items():
            if regex.match(value):
                return pattern_type
                
        return None
    
    def _detect_relationships(self, fields: Dict[str, FieldAnalysis]) -> List[Tuple[str, str]]:
        """Detect relationships between fields"""
        relationships = []
        
        # Look for ID references
        id_fields = [f for f in fields if 'id' in f.lower()]
        for field_name in fields:
            if field_name.endswith('_id') or field_name.endswith('Id'):
                # This might reference another entity
                referenced_entity = field_name[:-3] if field_name.endswith('_id') else field_name[:-2]
                relationships.append((field_name, referenced_entity))
                
        # Look for parent-child relationships
        for field_name, analysis in fields.items():
            if analysis.data_type == DataType.ARRAY and analysis.array_item_type == DataType.OBJECT:
                relationships.append((field_name, "parent-child"))
                
        return relationships
    
    def _calculate_complexity(self, fields: Dict[str, FieldAnalysis]) -> float:
        """Calculate schema complexity score (0-1)"""
        factors = {
            'field_count': min(len(fields) / 20, 1.0) * 0.2,
            'nested_objects': sum(1 for f in fields.values() if f.nested_schema) / max(len(fields), 1) * 0.3,
            'arrays': sum(1 for f in fields.values() if f.data_type == DataType.ARRAY) / max(len(fields), 1) * 0.2,
            'special_patterns': sum(1 for f in fields.values() if f.pattern_type) / max(len(fields), 1) * 0.2,
            'relationships': min(len(self._detect_relationships(fields)) / 5, 1.0) * 0.1
        }
        
        return sum(factors.values())
    
    def _calculate_depth(self, obj: Any, current_depth: int = 0) -> int:
        """Calculate maximum depth of nested objects"""
        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(self._calculate_depth(v, current_depth + 1) for v in obj.values())
        elif isinstance(obj, list) and obj:
            return max(self._calculate_depth(item, current_depth) for item in obj)
        else:
            return current_depth
    
    def _analyze_nested_object(self, obj: Dict) -> Dict:
        """Analyze nested object structure"""
        return {k: self._infer_data_type(v).value for k, v in obj.items()}
    
    def _infer_min_value(self, field_name: str, value: float) -> float:
        """Infer minimum value based on field name and value"""
        field_lower = field_name.lower()
        
        if any(word in field_lower for word in ['age', 'count', 'quantity', 'amount']):
            return 0
        elif 'price' in field_lower or 'cost' in field_lower:
            return 0.01
        elif 'percentage' in field_lower or 'percent' in field_lower:
            return 0
        elif 'year' in field_lower:
            return 1900
        else:
            # Default: 10% below example value
            return value * 0.9 if value > 0 else value * 1.1
    
    def _infer_max_value(self, field_name: str, value: float) -> float:
        """Infer maximum value based on field name and value"""
        field_lower = field_name.lower()
        
        if 'age' in field_lower:
            return 150
        elif 'percentage' in field_lower or 'percent' in field_lower:
            return 100
        elif 'year' in field_lower:
            return 2100
        elif 'price' in field_lower:
            return value * 100  # Allow up to 100x example
        else:
            # Default: 10% above example value
            return value * 1.1 if value > 0 else value * 0.9
    
    def _enhance_with_context(self, field_analysis: FieldAnalysis, context: str) -> FieldAnalysis:
        """Enhance field analysis with context information"""
        context_lower = context.lower()
        field_lower = field_analysis.field_name.lower()
        
        # E-commerce context
        if 'commerce' in context_lower or 'shop' in context_lower:
            if 'price' in field_lower:
                field_analysis.pattern_type = PatternType.CURRENCY
                field_analysis.constraints.min_value = 0.01
                field_analysis.constraints.max_value = 999999.99
            elif 'sku' in field_lower:
                field_analysis.constraints.pattern = r'^[A-Z]{3}\d{3,6}$'
            elif 'quantity' in field_lower:
                field_analysis.constraints.min_value = 1
                field_analysis.constraints.max_value = 9999
                
        # Healthcare context  
        elif 'health' in context_lower or 'medical' in context_lower:
            if 'patient' in field_lower and 'id' in field_lower:
                field_analysis.constraints.pattern = r'^PT\d{6,10}$'
            elif 'diagnosis' in field_lower:
                field_analysis.description = "ICD-10 diagnosis code"
                
        # Financial context
        elif 'finance' in context_lower or 'bank' in context_lower:
            if 'account' in field_lower:
                field_analysis.constraints.pattern = r'^\d{10,16}$'
            elif 'routing' in field_lower:
                field_analysis.constraints.pattern = r'^\d{9}$'
                
        return field_analysis
    
    def _suggest_patterns(self, fields: Dict[str, FieldAnalysis], context: Optional[str]) -> Dict[str, str]:
        """Suggest patterns for fields that don't have them"""
        suggestions = {}
        
        for field_name, analysis in fields.items():
            if analysis.data_type == DataType.STRING and not analysis.pattern_type:
                # Suggest based on field name
                field_lower = field_name.lower()
                
                if 'code' in field_lower:
                    suggestions[field_name] = "alphanumeric code pattern"
                elif 'number' in field_lower:
                    suggestions[field_name] = "numeric identifier pattern"
                elif 'status' in field_lower:
                    suggestions[field_name] = "enum values (active, inactive, pending)"
                    
        return suggestions
    
    def generate_schema_summary(self, analysis: SchemaAnalysis) -> str:
        """Generate human-readable summary of schema analysis"""
        lines = [
            f"Schema Analysis Summary:",
            f"- Total Fields: {analysis.total_fields}",
            f"- Complexity: {analysis.complexity_score:.2f} ({'Complex' if analysis.complexity_score > 0.7 else 'Moderate' if analysis.complexity_score > 0.3 else 'Simple'})",
            f"- Maximum Depth: {analysis.depth}",
            f"- Has Arrays: {'Yes' if analysis.has_arrays else 'No'}",
            f"- Has Nested Objects: {'Yes' if analysis.has_nested_objects else 'No'}",
            "",
            "Field Details:"
        ]
        
        for field_name, field_analysis in analysis.fields.items():
            line = f"  - {field_name}: {field_analysis.data_type.value}"
            if field_analysis.pattern_type:
                line += f" ({field_analysis.pattern_type.value})"
            lines.append(line)
            
        if analysis.relationships:
            lines.extend(["", "Detected Relationships:"])
            for rel in analysis.relationships:
                lines.append(f"  - {rel[0]} -> {rel[1]}")
                
        return "\n".join(lines) 