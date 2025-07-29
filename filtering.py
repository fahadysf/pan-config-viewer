"""
Comprehensive filtering system for pan-config-viewer API endpoints.

This module provides a flexible filtering framework that supports:
- Multiple filter conditions with AND logic
- Various matching types (exact, contains, case-insensitive)
- Type-aware filtering for different data types
- Integration with existing pagination
"""

from typing import List, Dict, Any, Optional, Union, Callable
from enum import Enum
import re
from fastapi import Query


class FilterOperator(str, Enum):
    """Supported filter operators"""
    EQUALS = "eq"
    NOT_EQUALS = "ne"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IN = "in"
    NOT_IN = "not_in"
    GREATER_THAN = "gt"
    LESS_THAN = "lt"
    GREATER_THAN_OR_EQUAL = "gte"
    LESS_THAN_OR_EQUAL = "lte"
    REGEX = "regex"


class FilterConfig:
    """Configuration for a filter field"""
    def __init__(
        self,
        field_path: str,
        operators: List[FilterOperator] = None,
        case_sensitive: bool = False,
        type_: type = str,
        custom_getter: Optional[Callable] = None
    ):
        self.field_path = field_path
        self.operators = operators or [
            FilterOperator.EQUALS,
            FilterOperator.CONTAINS,
            FilterOperator.STARTS_WITH,
            FilterOperator.ENDS_WITH
        ]
        self.case_sensitive = case_sensitive
        self.type = type_
        self.custom_getter = custom_getter


class FilterDefinition:
    """Defines available filters for an endpoint"""
    def __init__(self, filters: Dict[str, FilterConfig]):
        self.filters = filters
    
    def get_filter_params(self) -> Dict[str, Any]:
        """Generate FastAPI query parameters for filters"""
        params = {}
        for field_name, config in self.filters.items():
            # Support both simple filter[field]=value and filter[field][op]=value formats
            params[f"filter_{field_name}"] = Query(
                None, 
                alias=f"filter[{field_name}]",
                description=f"Filter by {field_name.replace('_', ' ')}"
            )
            
            # Also support operator-specific filters
            for op in config.operators:
                params[f"filter_{field_name}_{op.value}"] = Query(
                    None,
                    alias=f"filter[{field_name}][{op.value}]",
                    description=f"Filter by {field_name.replace('_', ' ')} ({op.value})"
                )
        
        return params


class FilterProcessor:
    """Processes filter conditions against objects"""
    
    @staticmethod
    def get_nested_value(obj: Any, path: str) -> Any:
        """Get value from object using dot-notation path"""
        if not path:
            return obj
            
        parts = path.split('.')
        value = obj
        
        for part in parts:
            if value is None:
                return None
                
            # Handle list indices
            if '[' in part and ']' in part:
                field_name = part[:part.index('[')]
                index = int(part[part.index('[') + 1:part.index(']')])
                value = getattr(value, field_name, None)
                if isinstance(value, list) and len(value) > index:
                    value = value[index]
                else:
                    return None
            else:
                # Handle regular attributes
                value = getattr(value, part, None)
        
        return value
    
    @staticmethod
    def apply_operator(
        value: Any,
        filter_value: Any,
        operator: FilterOperator,
        case_sensitive: bool = False
    ) -> bool:
        """Apply filter operator to compare values"""
        # Handle None values
        if value is None:
            return operator == FilterOperator.NOT_EQUALS and filter_value is not None
        
        # Convert to string for string operations
        if operator in [
            FilterOperator.CONTAINS,
            FilterOperator.NOT_CONTAINS,
            FilterOperator.STARTS_WITH,
            FilterOperator.ENDS_WITH,
            FilterOperator.REGEX
        ]:
            value_str = str(value)
            filter_str = str(filter_value)
            
            if not case_sensitive:
                value_str = value_str.lower()
                filter_str = filter_str.lower()
            
            if operator == FilterOperator.CONTAINS:
                return filter_str in value_str
            elif operator == FilterOperator.NOT_CONTAINS:
                return filter_str not in value_str
            elif operator == FilterOperator.STARTS_WITH:
                return value_str.startswith(filter_str)
            elif operator == FilterOperator.ENDS_WITH:
                return value_str.endswith(filter_str)
            elif operator == FilterOperator.REGEX:
                try:
                    pattern = re.compile(filter_str, re.IGNORECASE if not case_sensitive else 0)
                    return bool(pattern.search(value_str))
                except re.error:
                    return False
        
        # Handle list operations
        elif operator in [FilterOperator.IN, FilterOperator.NOT_IN]:
            if isinstance(value, list):
                # Check if filter_value is in the list
                if not case_sensitive and isinstance(filter_value, str):
                    value_list = [str(v).lower() for v in value]
                    filter_value = filter_value.lower()
                else:
                    value_list = value
                
                if operator == FilterOperator.IN:
                    return filter_value in value_list
                else:
                    return filter_value not in value_list
            else:
                # Check if value is in filter_value list
                filter_list = filter_value.split(',') if isinstance(filter_value, str) else filter_value
                if not case_sensitive:
                    value_str = str(value).lower()
                    filter_list = [str(f).lower() for f in filter_list]
                else:
                    value_str = str(value)
                
                if operator == FilterOperator.IN:
                    return value_str in filter_list
                else:
                    return value_str not in filter_list
        
        # Handle comparison operations
        else:
            # Try to convert to appropriate types for comparison
            try:
                if isinstance(filter_value, str) and filter_value.isdigit():
                    filter_value = int(filter_value)
                if isinstance(value, str) and value.isdigit():
                    value = int(value)
            except:
                pass
            
            if not case_sensitive and isinstance(value, str) and isinstance(filter_value, str):
                value = value.lower()
                filter_value = filter_value.lower()
            
            if operator == FilterOperator.EQUALS:
                return value == filter_value
            elif operator == FilterOperator.NOT_EQUALS:
                return value != filter_value
            elif operator == FilterOperator.GREATER_THAN:
                return value > filter_value
            elif operator == FilterOperator.LESS_THAN:
                return value < filter_value
            elif operator == FilterOperator.GREATER_THAN_OR_EQUAL:
                return value >= filter_value
            elif operator == FilterOperator.LESS_THAN_OR_EQUAL:
                return value <= filter_value
        
        return False
    
    @staticmethod
    def matches_filters(
        obj: Any,
        filters: Dict[str, Any],
        filter_definition: FilterDefinition
    ) -> bool:
        """Check if object matches all filter conditions (AND logic)"""
        for field_name, filter_value in filters.items():
            if filter_value is None:
                continue
            
            # Parse field name to extract operator if present
            parts = field_name.split('_')
            if len(parts) > 1 and parts[-1] in [op.value for op in FilterOperator]:
                operator = FilterOperator(parts[-1])
                base_field_name = '_'.join(parts[:-1])
            else:
                operator = FilterOperator.CONTAINS  # Default operator
                base_field_name = field_name
            
            # Skip if field not in filter definition
            if base_field_name not in filter_definition.filters:
                continue
            
            config = filter_definition.filters[base_field_name]
            
            # Get value from object
            if config.custom_getter:
                value = config.custom_getter(obj)
            else:
                value = FilterProcessor.get_nested_value(obj, config.field_path)
            
            # Apply filter
            if not FilterProcessor.apply_operator(
                value,
                filter_value,
                operator,
                config.case_sensitive
            ):
                return False
        
        return True


def apply_filters(
    items: List[Any],
    filter_params: Dict[str, Any],
    filter_definition: FilterDefinition
) -> List[Any]:
    """Apply filters to a list of items"""
    # Extract non-None filter parameters
    active_filters = {
        k.replace('filter_', ''): v
        for k, v in filter_params.items()
        if k.startswith('filter_') and v is not None
    }
    
    if not active_filters:
        return items
    
    # Filter items
    filtered_items = []
    for item in items:
        if FilterProcessor.matches_filters(item, active_filters, filter_definition):
            filtered_items.append(item)
    
    return filtered_items


# Pre-defined filter configurations for common object types

# Address object filters
ADDRESS_FILTERS = FilterDefinition({
    "name": FilterConfig("name"),
    "ip": FilterConfig("ip_netmask", operators=[
        FilterOperator.EQUALS,
        FilterOperator.CONTAINS,
        FilterOperator.STARTS_WITH
    ]),
    "ip_range": FilterConfig("ip_range"),
    "fqdn": FilterConfig("fqdn"),
    "description": FilterConfig("description"),
    "tag": FilterConfig("tag", operators=[
        FilterOperator.IN,
        FilterOperator.NOT_IN,
        FilterOperator.CONTAINS
    ], type_=list),
    "location": FilterConfig(
        "parent_device_group",
        custom_getter=lambda obj: (
            "shared" if not any([obj.parent_device_group, obj.parent_template, obj.parent_vsys])
            else obj.parent_device_group or obj.parent_template or obj.parent_vsys
        )
    )
})

# Service object filters
SERVICE_FILTERS = FilterDefinition({
    "name": FilterConfig("name"),
    "protocol": FilterConfig(
        "protocol",
        custom_getter=lambda obj: (
            "tcp" if obj.protocol.tcp else "udp" if obj.protocol.udp else None
        )
    ),
    "port": FilterConfig(
        "protocol",
        custom_getter=lambda obj: (
            obj.protocol.tcp.get("port", "") if obj.protocol.tcp
            else obj.protocol.udp.get("port", "") if obj.protocol.udp
            else ""
        )
    ),
    "description": FilterConfig("description"),
    "tag": FilterConfig("tag", operators=[
        FilterOperator.IN,
        FilterOperator.NOT_IN,
        FilterOperator.CONTAINS
    ], type_=list)
})

# Security rule filters
SECURITY_RULE_FILTERS = FilterDefinition({
    "name": FilterConfig("name"),
    "source": FilterConfig("source", operators=[
        FilterOperator.IN,
        FilterOperator.CONTAINS
    ], type_=list),
    "destination": FilterConfig("destination", operators=[
        FilterOperator.IN,
        FilterOperator.CONTAINS
    ], type_=list),
    "source_zone": FilterConfig("from_", operators=[
        FilterOperator.IN,
        FilterOperator.CONTAINS
    ], type_=list),
    "destination_zone": FilterConfig("to", operators=[
        FilterOperator.IN,
        FilterOperator.CONTAINS
    ], type_=list),
    "service": FilterConfig("service", operators=[
        FilterOperator.IN,
        FilterOperator.CONTAINS
    ], type_=list),
    "application": FilterConfig("application", operators=[
        FilterOperator.IN,
        FilterOperator.CONTAINS
    ], type_=list),
    "action": FilterConfig("action"),
    "disabled": FilterConfig("disabled", type_=bool),
    "description": FilterConfig("description"),
    "tag": FilterConfig("tag", operators=[
        FilterOperator.IN,
        FilterOperator.NOT_IN,
        FilterOperator.CONTAINS
    ], type_=list)
})

# Device group filters
DEVICE_GROUP_FILTERS = FilterDefinition({
    "name": FilterConfig("name"),
    "parent": FilterConfig("parent_dg"),
    "description": FilterConfig("description")
})

# Address/Service group filters
GROUP_FILTERS = FilterDefinition({
    "name": FilterConfig("name"),
    "description": FilterConfig("description"),
    "member": FilterConfig(
        "members",
        custom_getter=lambda obj: (
            obj.static if hasattr(obj, 'static') and obj.static
            else obj.members if hasattr(obj, 'members')
            else []
        ),
        operators=[
            FilterOperator.IN,
            FilterOperator.CONTAINS
        ],
        type_=list
    ),
    "tag": FilterConfig("tag", operators=[
        FilterOperator.IN,
        FilterOperator.NOT_IN,
        FilterOperator.CONTAINS
    ], type_=list)
})

# Security profile filters
PROFILE_FILTERS = FilterDefinition({
    "name": FilterConfig("name"),
    "description": FilterConfig("description")
})