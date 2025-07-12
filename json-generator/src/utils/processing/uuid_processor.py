"""
UUID Processor

This module handles UUID generation in code rather than through LLM generation.
It identifies UUID fields in the generated data and replaces them with properly
generated UUIDs using Python's uuid library.

Features:
- Automatic UUID field detection
- Multiple UUID formats support (standard, short, prefixed)
- Context-aware UUID generation (user, account, transaction, etc.)
- Consistent UUID patterns within the same generation session
- Validation and replacement of malformed UUIDs
"""

import uuid
import re
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

class UUIDFormat(Enum):
    """UUID format types"""
    STANDARD = "standard"        # 550e8400-e29b-41d4-a716-446655440000
    SHORT = "short"             # 550e8400e29b41d4a716446655440000
    PREFIXED = "prefixed"       # acc_550e8400e29b41d4a716446655440000
    UPPERCASE = "uppercase"     # 550E8400-E29B-41D4-A716-446655440000

class UUIDContext(Enum):
    """UUID context types for prefixed UUIDs"""
    USER = "user"
    ACCOUNT = "acc"
    TRANSACTION = "txn"
    PRODUCT = "prod"
    SESSION = "sess"
    ORDER = "ord"
    PAYMENT = "pay"
    INVOICE = "inv"
    TICKET = "tkt"
    MESSAGE = "msg"

@dataclass
class UUIDConfig:
    """Configuration for UUID generation"""
    format_type: UUIDFormat = UUIDFormat.STANDARD
    context: Optional[UUIDContext] = None
    preserve_existing: bool = True  # Keep valid UUIDs that already exist
    use_deterministic: bool = False  # Use deterministic UUIDs for testing

class UUIDProcessor:
    """Processes and generates UUIDs in JSON data"""
    
    def __init__(self):
        self.uuid_patterns = self._compile_uuid_patterns()
        self.field_context_mapping = self._build_field_context_mapping()
        self.generated_uuids = {}  # Cache for consistent UUIDs within session
        
    def _compile_uuid_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for UUID detection"""
        return {
            'standard': re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE),
            'short': re.compile(r'^[0-9a-f]{32}$', re.IGNORECASE),
            'prefixed': re.compile(r'^[a-z]+_[0-9a-f]{8}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{12}$', re.IGNORECASE),
            'partial': re.compile(r'[0-9a-f]{8}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{4}-?[0-9a-f]{12}', re.IGNORECASE),
        }
    
    def _build_field_context_mapping(self) -> Dict[str, UUIDContext]:
        """Build mapping of field name patterns to UUID contexts"""
        return {
            # User-related fields
            'user_id': UUIDContext.USER,
            'user': UUIDContext.USER,
            'customer_id': UUIDContext.USER,
            'member_id': UUIDContext.USER,
            'person_id': UUIDContext.USER,
            
            # Account-related fields
            'account_id': UUIDContext.ACCOUNT,
            'account': UUIDContext.ACCOUNT,
            'profile_id': UUIDContext.ACCOUNT,
            
            # Transaction-related fields
            'transaction_id': UUIDContext.TRANSACTION,
            'txn_id': UUIDContext.TRANSACTION,
            'transfer_id': UUIDContext.TRANSACTION,
            
            # Product-related fields
            'product_id': UUIDContext.PRODUCT,
            'item_id': UUIDContext.PRODUCT,
            'sku_id': UUIDContext.PRODUCT,
            
            # Session-related fields
            'session_id': UUIDContext.SESSION,
            'token_id': UUIDContext.SESSION,
            
            # Order-related fields
            'order_id': UUIDContext.ORDER,
            'purchase_id': UUIDContext.ORDER,
            
            # Payment-related fields
            'payment_id': UUIDContext.PAYMENT,
            'charge_id': UUIDContext.PAYMENT,
            
            # Invoice-related fields
            'invoice_id': UUIDContext.INVOICE,
            'bill_id': UUIDContext.INVOICE,
            
            # Ticket-related fields
            'ticket_id': UUIDContext.TICKET,
            'support_id': UUIDContext.TICKET,
            
            # Message-related fields
            'message_id': UUIDContext.MESSAGE,
            'notification_id': UUIDContext.MESSAGE,
        }
    
    def detect_uuid_fields(self, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> List[str]:
        """Detect fields that should contain UUIDs"""
        uuid_fields = set()
        
        def analyze_object(obj: Dict[str, Any], prefix: str = ""):
            for key, value in obj.items():
                full_key = f"{prefix}.{key}" if prefix else key
                
                if isinstance(value, dict):
                    analyze_object(value, full_key)
                elif isinstance(value, list) and value and isinstance(value[0], dict):
                    analyze_object(value[0], full_key)
                elif isinstance(value, str):
                    # Check if field name suggests UUID
                    if self._is_uuid_field_name(key):
                        uuid_fields.add(full_key)
                    # Check if value looks like a UUID
                    elif self._looks_like_uuid(value):
                        uuid_fields.add(full_key)
        
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    analyze_object(item)
        else:
            analyze_object(data)
        
        return list(uuid_fields)
    
    def _is_uuid_field_name(self, field_name: str) -> bool:
        """Check if field name suggests it should contain a UUID"""
        field_lower = field_name.lower()
        
        # Direct matches
        if field_lower == 'id':
            return True
        
        # Pattern matches
        uuid_indicators = [
            '_id', 'id_', 'uuid', 'guid', 'identifier'
        ]
        
        return any(indicator in field_lower for indicator in uuid_indicators)
    
    def _looks_like_uuid(self, value: str) -> bool:
        """Check if a string value looks like a UUID"""
        if not isinstance(value, str):
            return False
        
        # Check against all UUID patterns
        return any(pattern.match(value) for pattern in self.uuid_patterns.values())
    
    def _get_field_context(self, field_name: str) -> Optional[UUIDContext]:
        """Get UUID context for a field name"""
        field_lower = field_name.lower()
        
        # Direct mapping
        if field_lower in self.field_context_mapping:
            return self.field_context_mapping[field_lower]
        
        # Pattern matching
        for pattern, context in self.field_context_mapping.items():
            if pattern in field_lower:
                return context
        
        return None
    
    def _determine_uuid_format(self, existing_value: str, field_name: str) -> UUIDConfig:
        """Determine the appropriate UUID format based on existing value and field name"""
        if not existing_value:
            # Default format for new UUIDs
            context = self._get_field_context(field_name)
            return UUIDConfig(
                format_type=UUIDFormat.PREFIXED if context else UUIDFormat.STANDARD,
                context=context
            )
        
        # Analyze existing value to determine format
        if self.uuid_patterns['prefixed'].match(existing_value):
            # Extract prefix to determine context
            prefix = existing_value.split('_')[0]
            context = None
            for ctx in UUIDContext:
                if ctx.value == prefix:
                    context = ctx
                    break
            return UUIDConfig(format_type=UUIDFormat.PREFIXED, context=context)
        
        elif self.uuid_patterns['short'].match(existing_value):
            return UUIDConfig(format_type=UUIDFormat.SHORT)
        
        elif existing_value.isupper():
            return UUIDConfig(format_type=UUIDFormat.UPPERCASE)
        
        else:
            return UUIDConfig(format_type=UUIDFormat.STANDARD)
    
    def generate_uuid(self, config: UUIDConfig, field_name: str = "") -> str:
        """Generate a UUID according to the specified configuration"""
        # Check cache for consistent UUIDs
        cache_key = f"{field_name}_{config.format_type.value}_{config.context.value if config.context else 'none'}"
        
        if config.use_deterministic and cache_key in self.generated_uuids:
            return self.generated_uuids[cache_key]
        
        # Generate new UUID
        new_uuid = uuid.uuid4()
        
        if config.format_type == UUIDFormat.STANDARD:
            result = str(new_uuid)
        elif config.format_type == UUIDFormat.SHORT:
            result = str(new_uuid).replace('-', '')
        elif config.format_type == UUIDFormat.UPPERCASE:
            result = str(new_uuid).upper()
        elif config.format_type == UUIDFormat.PREFIXED:
            prefix = config.context.value if config.context else "id"
            result = f"{prefix}_{str(new_uuid)}"
        else:
            result = str(new_uuid)
        
        # Cache for consistency
        if config.use_deterministic:
            self.generated_uuids[cache_key] = result
        
        return result
    
    def process_data(self, data: Union[Dict[str, Any], List[Dict[str, Any]]], config: Optional[UUIDConfig] = None) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Process data and replace UUID fields with generated UUIDs"""
        if config is None:
            config = UUIDConfig()
        
        def process_object(obj: Dict[str, Any]) -> Dict[str, Any]:
            result = {}
            
            for key, value in obj.items():
                if isinstance(value, dict):
                    result[key] = process_object(value)
                elif isinstance(value, list):
                    result[key] = [process_object(item) if isinstance(item, dict) else item for item in value]
                elif isinstance(value, str) and self._should_replace_uuid(key, value, config):
                    # Generate new UUID for this field
                    field_config = self._determine_uuid_format(value, key)
                    result[key] = self.generate_uuid(field_config, key)
                else:
                    result[key] = value
            
            return result
        
        if isinstance(data, list):
            return [process_object(item) if isinstance(item, dict) else item for item in data]
        else:
            return process_object(data)
    
    def _should_replace_uuid(self, field_name: str, value: str, config: UUIDConfig) -> bool:
        """Determine if a UUID field should be replaced"""
        # Always replace if it's a UUID field name
        if self._is_uuid_field_name(field_name):
            return True
        
        # Replace if value looks like a malformed UUID
        if self._looks_like_uuid(value):
            # Check if it's a valid UUID
            try:
                uuid.UUID(value.replace('_', '').split('_')[-1])
                return not config.preserve_existing  # Replace valid UUIDs only if not preserving
            except ValueError:
                return True  # Replace invalid UUIDs
        
        return False
    
    def validate_uuids(self, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Dict[str, List[str]]:
        """Validate all UUIDs in the data and return validation results"""
        results = {
            'valid': [],
            'invalid': [],
            'missing': []
        }
        
        def validate_object(obj: Dict[str, Any], prefix: str = ""):
            for key, value in obj.items():
                full_key = f"{prefix}.{key}" if prefix else key
                
                if isinstance(value, dict):
                    validate_object(value, full_key)
                elif isinstance(value, list) and value and isinstance(value[0], dict):
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            validate_object(item, f"{full_key}[{i}]")
                elif isinstance(value, str):
                    if self._is_uuid_field_name(key):
                        if self._looks_like_uuid(value):
                            try:
                                # Validate UUID
                                clean_value = value.replace('_', '').split('_')[-1]
                                uuid.UUID(clean_value)
                                results['valid'].append(f"{full_key}: {value}")
                            except ValueError:
                                results['invalid'].append(f"{full_key}: {value}")
                        else:
                            results['missing'].append(f"{full_key}: {value}")
        
        if isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, dict):
                    validate_object(item, f"[{i}]")
        else:
            validate_object(data)
        
        return results
    
    def get_uuid_instructions(self) -> str:
        """Get instructions for LLM to avoid generating UUIDs"""
        return """
IMPORTANT UUID INSTRUCTIONS:
- Do NOT generate UUIDs, GUIDs, or any ID values
- For any field ending with '_id' or named 'id', use placeholder values like "UUID_PLACEHOLDER"
- The system will automatically generate proper UUIDs after your response
- Focus on generating realistic data for non-ID fields
- Examples of fields to use placeholders for:
  * id, user_id, account_id, transaction_id, product_id
  * session_id, order_id, payment_id, invoice_id
  * Any field that should contain a unique identifier

Use "UUID_PLACEHOLDER" for all ID fields - they will be replaced with proper UUIDs.
"""
    
    def replace_placeholders(self, data: Union[Dict[str, Any], List[Dict[str, Any]]], placeholder: str = "UUID_PLACEHOLDER") -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Replace UUID placeholders with generated UUIDs"""
        def process_object(obj: Dict[str, Any]) -> Dict[str, Any]:
            result = {}
            
            for key, value in obj.items():
                if isinstance(value, dict):
                    result[key] = process_object(value)
                elif isinstance(value, list):
                    result[key] = [process_object(item) if isinstance(item, dict) else item for item in value]
                elif isinstance(value, str) and value == placeholder:
                    # Replace placeholder with generated UUID
                    field_config = self._determine_uuid_format("", key)
                    result[key] = self.generate_uuid(field_config, key)
                else:
                    result[key] = value
            
            return result
        
        if isinstance(data, list):
            return [process_object(item) if isinstance(item, dict) else item for item in data]
        else:
            return process_object(data)

# Global UUID processor instance
uuid_processor = UUIDProcessor()

# Convenience functions
def process_uuids(data: Union[Dict[str, Any], List[Dict[str, Any]]], preserve_existing: bool = True) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """Process and generate UUIDs in data"""
    config = UUIDConfig(preserve_existing=preserve_existing)
    return uuid_processor.process_data(data, config)

def replace_uuid_placeholders(data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """Replace UUID placeholders with generated UUIDs"""
    return uuid_processor.replace_placeholders(data)

def get_uuid_instructions() -> str:
    """Get UUID instructions for LLM"""
    return uuid_processor.get_uuid_instructions()

def validate_uuids(data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Dict[str, List[str]]:
    """Validate UUIDs in data"""
    return uuid_processor.validate_uuids(data)

def detect_uuid_fields(data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> List[str]:
    """Detect UUID fields in data"""
    return uuid_processor.detect_uuid_fields(data)

# Example usage
if __name__ == "__main__":
    # Example data with various UUID formats
    test_data = [
        {
            "id": "invalid-uuid-123",
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "account_id": "acc_invalid_uuid",
            "name": "John Doe",
            "email": "john@example.com",
            "profile": {
                "profile_id": "UUID_PLACEHOLDER",
                "settings": {
                    "session_id": "sess_550e8400e29b41d4a716446655440001"
                }
            }
        }
    ]
    
    print("Original data:")
    print(test_data)
    
    print("\nDetected UUID fields:")
    uuid_fields = detect_uuid_fields(test_data)
    print(uuid_fields)
    
    print("\nProcessed data:")
    processed = process_uuids(test_data, preserve_existing=False)
    print(processed)
    
    print("\nValidation results:")
    validation = validate_uuids(processed)
    for category, items in validation.items():
        print(f"{category}: {len(items)} items")
        for item in items[:3]:  # Show first 3 items
            print(f"  {item}")
    
    print("\nUUID Instructions for LLM:")
    print(get_uuid_instructions()) 