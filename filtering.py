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
from functools import lru_cache


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
    
    # Cache for field name normalization
    _field_name_cache: Dict[str, str] = {}
    
    @staticmethod
    @lru_cache(maxsize=1024)
    def normalize_field_name(field_name: str) -> str:
        """Normalize field names to handle both snake_case and hyphenated formats
        
        Examples:
            ip_netmask -> ip-netmask
            parent_device_group -> parent-device-group
        """
        # Check cache first
        if field_name in FilterProcessor._field_name_cache:
            return FilterProcessor._field_name_cache[field_name]
        
        # Convert snake_case to hyphenated for attribute lookup
        normalized = field_name.replace('_', '-')
        FilterProcessor._field_name_cache[field_name] = normalized
        return normalized
    
    @staticmethod
    def get_nested_value(obj: Any, path: str) -> Any:
        """Get value from object using dot-notation path with performance optimizations"""
        if not path:
            return obj
            
        # Cache split operation
        parts = path.split('.')
        value = obj
        
        for part in parts:
            if value is None:
                return None
                
            # Handle list indices
            if '[' in part and ']' in part:
                bracket_idx = part.index('[')
                field_name = part[:bracket_idx]
                # Pre-calculate indices to avoid multiple indexOf calls
                close_bracket_idx = part.index(']', bracket_idx)
                index = int(part[bracket_idx + 1:close_bracket_idx])
                
                # Use try-except for better performance in success case
                try:
                    value = getattr(value, field_name)
                    if isinstance(value, list) and len(value) > index:
                        value = value[index]
                    else:
                        return None
                except AttributeError:
                    return None
            else:
                # Handle regular attributes - using getattr with default is faster
                value = getattr(value, part, None)
        
        return value
    
    # Pre-compile common regex patterns for performance
    _regex_cache: Dict[str, re.Pattern] = {}
    
    # Index for frequently filtered fields (built on demand)
    _field_indexes: Dict[str, Dict[str, List[Any]]] = {}
    
    @staticmethod
    def apply_operator(
        value: Any,
        filter_value: Any,
        operator: FilterOperator,
        case_sensitive: bool = False
    ) -> bool:
        """Apply filter operator to compare values with performance optimizations"""
        # Handle None values
        if value is None:
            if filter_value is None:
                # Both are None
                return operator == FilterOperator.EQUALS or operator == FilterOperator.LESS_THAN_OR_EQUAL or operator == FilterOperator.GREATER_THAN_OR_EQUAL
            else:
                # value is None but filter_value is not
                return operator == FilterOperator.NOT_EQUALS
        
        # Handle enum values - convert to their string representation
        from enum import Enum
        if isinstance(value, Enum):
            value = value.value
        
        # Pre-define string operators set for faster lookup
        STRING_OPERATORS = {
            FilterOperator.CONTAINS,
            FilterOperator.NOT_CONTAINS,
            FilterOperator.STARTS_WITH,
            FilterOperator.ENDS_WITH,
            FilterOperator.REGEX
        }
        
        # Convert to string for string operations
        if operator in STRING_OPERATORS:
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
                    # Cache compiled regex patterns for performance
                    cache_key = f"{filter_str}_{case_sensitive}"
                    if cache_key not in FilterProcessor._regex_cache:
                        FilterProcessor._regex_cache[cache_key] = re.compile(
                            filter_str, 
                            re.IGNORECASE if not case_sensitive else 0
                        )
                    pattern = FilterProcessor._regex_cache[cache_key]
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
            elif operator in [FilterOperator.GREATER_THAN, FilterOperator.LESS_THAN, 
                            FilterOperator.GREATER_THAN_OR_EQUAL, FilterOperator.LESS_THAN_OR_EQUAL]:
                # For comparison operators, ensure both values are comparable
                try:
                    # If types are different and one is numeric while other is non-numeric string, 
                    # the comparison should return False
                    if type(value) != type(filter_value):
                        # Try to convert both to float for numeric comparison
                        value_num = float(value) if isinstance(value, (int, str)) else None
                        filter_num = float(filter_value) if isinstance(filter_value, (int, str)) else None
                        
                        if value_num is not None and filter_num is not None:
                            if operator == FilterOperator.GREATER_THAN:
                                return value_num > filter_num
                            elif operator == FilterOperator.LESS_THAN:
                                return value_num < filter_num
                            elif operator == FilterOperator.GREATER_THAN_OR_EQUAL:
                                return value_num >= filter_num
                            elif operator == FilterOperator.LESS_THAN_OR_EQUAL:
                                return value_num <= filter_num
                        else:
                            # Can't compare - return False for safety
                            return False
                    else:
                        # Same types, direct comparison
                        if operator == FilterOperator.GREATER_THAN:
                            return value > filter_value
                        elif operator == FilterOperator.LESS_THAN:
                            return value < filter_value
                        elif operator == FilterOperator.GREATER_THAN_OR_EQUAL:
                            return value >= filter_value
                        elif operator == FilterOperator.LESS_THAN_OR_EQUAL:
                            return value <= filter_value
                except (ValueError, TypeError):
                    # If comparison fails, return False
                    return False
        
        return False
    
    @staticmethod
    def matches_filters(
        obj: Any,
        filters: Dict[str, Any],
        filter_definition: FilterDefinition
    ) -> bool:
        """Check if object matches all filter conditions (AND logic) with early exit optimization"""
        # Early exit if no filters
        if not filters:
            return True
            
        for field_name, filter_value in filters.items():
            # Only skip None filter values if they're not part of explicit equality/inequality operations
            # This allows filtering for None values when using operators like _eq or _ne
            if filter_value is None and not (field_name.endswith('_eq') or field_name.endswith('_ne')):
                continue
            
            # Parse field name to extract operator if present
            # First, try to find the longest matching operator at the end
            operator = None
            base_field_name = field_name
            
            # Check for operator suffixes from longest to shortest
            # Sort operators by length (descending) to match longest first
            sorted_operators = sorted(FilterOperator, key=lambda x: len(x.value), reverse=True)
            for op in sorted_operators:
                suffix = f"_{op.value}"
                if field_name.endswith(suffix):
                    operator = op
                    base_field_name = field_name[:-len(suffix)]
                    break
            
            # If no operator found, use default
            if operator is None:
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
    """Apply filters to a list of items with optimizations for large datasets"""
    # The filter_params are already parsed, no need to extract
    # Don't filter out None values here - let matches_filters handle them
    active_filters = filter_params
    
    if not active_filters:
        return items
    
    # Early exit if no items
    if not items:
        return items
    
    # Use generator expression with list comprehension for better performance
    # This is more memory efficient for large datasets
    return [item for item in items if FilterProcessor.matches_filters(item, active_filters, filter_definition)]


def apply_filters_parallel(
    items_dict: Dict[str, List[Any]],
    filter_params: Dict[str, Any],
    filter_definitions: Dict[str, FilterDefinition]
) -> Dict[str, List[Any]]:
    """Apply filters to multiple lists in parallel for better performance
    
    Args:
        items_dict: Dictionary mapping object type to list of items
        filter_params: Filter parameters to apply
        filter_definitions: Dictionary mapping object type to filter definition
    
    Returns:
        Dictionary with filtered results for each object type
    """
    # The filter_params are already parsed
    active_filters = {
        k: v for k, v in filter_params.items() if v is not None
    }
    
    if not active_filters:
        return items_dict
    
    results = {}
    for obj_type, items in items_dict.items():
        if obj_type in filter_definitions:
            results[obj_type] = apply_filters(items, active_filters, filter_definitions[obj_type])
        else:
            results[obj_type] = items
    
    return results


def create_filter_with_aliases(base_filters: Dict[str, FilterConfig]) -> Dict[str, FilterConfig]:
    """Create filter definitions with both snake_case and hyphenated aliases
    
    This helper function automatically creates hyphenated aliases for snake_case field names
    to support both formats in API requests.
    """
    result = base_filters.copy()
    
    # Add hyphenated aliases for snake_case fields
    for field_name, config in list(base_filters.items()):
        if '_' in field_name:
            # Create hyphenated alias
            hyphenated_name = field_name.replace('_', '-')
            if hyphenated_name not in result:
                result[hyphenated_name] = config
    
    return result


# Pre-defined filter configurations for common object types

# Address object filters - comprehensive filtering for all properties
ADDRESS_FILTERS = FilterDefinition(create_filter_with_aliases({
    "name": FilterConfig("name", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS,
        FilterOperator.STARTS_WITH,
        FilterOperator.ENDS_WITH
    ]),
    # Note: 'value' field checks ip_netmask, ip_range, or fqdn
    "value": FilterConfig(
        "value",
        custom_getter=lambda obj: (
            getattr(obj, 'ip_netmask', None) or 
            getattr(obj, 'ip_range', None) or 
            getattr(obj, 'fqdn', None) or 
            ''
        ),
        operators=[
            FilterOperator.EQUALS,
            FilterOperator.NOT_EQUALS,
            FilterOperator.CONTAINS,
            FilterOperator.STARTS_WITH,
            FilterOperator.ENDS_WITH
        ]
    ),
    # Note: 'ip' is an alias that checks both 'ip_netmask' and 'ip_range' fields
    "ip": FilterConfig(
        "ip",
        custom_getter=lambda obj: (
            getattr(obj, 'ip_netmask', None) or 
            getattr(obj, 'ip_range', None) or 
            ''
        ),
        operators=[
            FilterOperator.EQUALS,
            FilterOperator.NOT_EQUALS,
            FilterOperator.CONTAINS,
            FilterOperator.STARTS_WITH,
            FilterOperator.ENDS_WITH
        ]
    ),
    "ip_netmask": FilterConfig("ip_netmask", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS,
        FilterOperator.STARTS_WITH
    ]),
    "ip_range": FilterConfig("ip_range", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS
    ]),
    "fqdn": FilterConfig("fqdn", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS,
        FilterOperator.STARTS_WITH,
        FilterOperator.ENDS_WITH
    ]),
    "description": FilterConfig("description", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS,
        FilterOperator.STARTS_WITH,
        FilterOperator.ENDS_WITH
    ]),
    "tag": FilterConfig("tag", operators=[
        FilterOperator.IN,
        FilterOperator.NOT_IN,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS
    ], type_=list),
    "xpath": FilterConfig("xpath", operators=[
        FilterOperator.EQUALS,
        FilterOperator.CONTAINS,
        FilterOperator.STARTS_WITH
    ]),
    "parent_device_group": FilterConfig("parent_device_group", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS
    ]),
    "parent_template": FilterConfig("parent_template", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS
    ]),
    "parent_vsys": FilterConfig("parent_vsys", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS
    ]),
    "location": FilterConfig(
        "parent_device_group",
        custom_getter=lambda obj: (
            "shared" if not any([obj.parent_device_group, obj.parent_template, obj.parent_vsys])
            else "device-group" if obj.parent_device_group
            else "template" if obj.parent_template
            else "vsys" if obj.parent_vsys
            else "unknown"
        ),
        operators=[
            FilterOperator.EQUALS,
            FilterOperator.NOT_EQUALS
        ]
    ),
    "type": FilterConfig("type", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS,
        FilterOperator.IN,
        FilterOperator.NOT_IN
    ])
}))

# Service object filters - comprehensive filtering for all properties
SERVICE_FILTERS = FilterDefinition(create_filter_with_aliases({
    "name": FilterConfig("name", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS,
        FilterOperator.STARTS_WITH,
        FilterOperator.ENDS_WITH
    ]),
    "protocol": FilterConfig(
        "protocol",
        custom_getter=lambda obj: (
            "tcp" if obj.protocol.tcp else "udp" if obj.protocol.udp else None
        ),
        operators=[
            FilterOperator.EQUALS,
            FilterOperator.NOT_EQUALS
        ]
    ),
    "port": FilterConfig(
        "protocol",
        custom_getter=lambda obj: (
            str(obj.protocol.tcp.get("port", "")) if obj.protocol.tcp
            else str(obj.protocol.udp.get("port", "")) if obj.protocol.udp
            else ""
        ),
        operators=[
            FilterOperator.EQUALS,
            FilterOperator.NOT_EQUALS,
            FilterOperator.CONTAINS,
            FilterOperator.GREATER_THAN,
            FilterOperator.LESS_THAN,
            FilterOperator.GREATER_THAN_OR_EQUAL,
            FilterOperator.LESS_THAN_OR_EQUAL
        ]
    ),
    "source_port": FilterConfig(
        "protocol",
        custom_getter=lambda obj: (
            str(obj.protocol.tcp.get("source-port", "")) if obj.protocol.tcp and "source-port" in obj.protocol.tcp
            else str(obj.protocol.udp.get("source-port", "")) if obj.protocol.udp and "source-port" in obj.protocol.udp
            else ""
        ),
        operators=[
            FilterOperator.EQUALS,
            FilterOperator.NOT_EQUALS,
            FilterOperator.CONTAINS
        ]
    ),
    "description": FilterConfig("description", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS,
        FilterOperator.STARTS_WITH,
        FilterOperator.ENDS_WITH
    ]),
    "tag": FilterConfig("tag", operators=[
        FilterOperator.IN,
        FilterOperator.NOT_IN,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS
    ], type_=list),
    "xpath": FilterConfig("xpath", operators=[
        FilterOperator.EQUALS,
        FilterOperator.CONTAINS,
        FilterOperator.STARTS_WITH
    ]),
    "parent_device_group": FilterConfig("parent_device_group", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS
    ]),
    "parent_template": FilterConfig("parent_template", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS
    ]),
    "parent_vsys": FilterConfig("parent_vsys", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS
    ]),
    "type": FilterConfig("type", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS,
        FilterOperator.IN,
        FilterOperator.NOT_IN
    ])
}))

SECURITY_RULE_FILTERS = FilterDefinition(create_filter_with_aliases({
    "name": FilterConfig("name", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS,
        FilterOperator.STARTS_WITH,
        FilterOperator.ENDS_WITH
    ]),
    "uuid": FilterConfig("uuid", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS
    ]),
    "source": FilterConfig("source", operators=[
        FilterOperator.IN,
        FilterOperator.NOT_IN,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS
    ], type_=list),
    "destination": FilterConfig("destination", operators=[
        FilterOperator.IN,
        FilterOperator.NOT_IN,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS
    ], type_=list),
    "source_zone": FilterConfig("from_", operators=[
        FilterOperator.IN,
        FilterOperator.NOT_IN,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS
    ], type_=list),
    "destination_zone": FilterConfig("to", operators=[
        FilterOperator.IN,
        FilterOperator.NOT_IN,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS
    ], type_=list),
    "source_user": FilterConfig("source_user", operators=[
        FilterOperator.IN,
        FilterOperator.NOT_IN,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS
    ], type_=list),
    "category": FilterConfig("category", operators=[
        FilterOperator.IN,
        FilterOperator.NOT_IN,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS
    ], type_=list),
    "service": FilterConfig("service", operators=[
        FilterOperator.IN,
        FilterOperator.NOT_IN,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS
    ], type_=list),
    "application": FilterConfig("application", operators=[
        FilterOperator.IN,
        FilterOperator.NOT_IN,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS
    ], type_=list),
    "action": FilterConfig("action", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS
    ]),
    "log_start": FilterConfig("log_start", type_=bool, operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS
    ]),
    "log_end": FilterConfig("log_end", type_=bool, operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS
    ]),
    "disabled": FilterConfig("disabled", type_=bool, operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS
    ]),
    "description": FilterConfig("description", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS,
        FilterOperator.STARTS_WITH,
        FilterOperator.ENDS_WITH
    ]),
    "tag": FilterConfig("tag", operators=[
        FilterOperator.IN,
        FilterOperator.NOT_IN,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS
    ], type_=list),
    "log_setting": FilterConfig("log_setting", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS
    ]),
    "xpath": FilterConfig("xpath", operators=[
        FilterOperator.EQUALS,
        FilterOperator.CONTAINS,
        FilterOperator.STARTS_WITH
    ]),
    "parent_device_group": FilterConfig("parent_device_group", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS
    ])
}))

# Device group filters - comprehensive filtering for all properties
DEVICE_GROUP_FILTERS = FilterDefinition(create_filter_with_aliases({
    "name": FilterConfig("name", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS,
        FilterOperator.STARTS_WITH,
        FilterOperator.ENDS_WITH
    ]),
    "parent": FilterConfig("parent_dg", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS
    ]),
    "parent_dg": FilterConfig("parent_dg", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS
    ]),
    "description": FilterConfig("description", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS,
        FilterOperator.STARTS_WITH,
        FilterOperator.ENDS_WITH
    ]),
    "devices_count": FilterConfig("devices_count", type_=int, operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.GREATER_THAN,
        FilterOperator.LESS_THAN,
        FilterOperator.GREATER_THAN_OR_EQUAL,
        FilterOperator.LESS_THAN_OR_EQUAL
    ]),
    "address_count": FilterConfig("address_count", type_=int, operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.GREATER_THAN,
        FilterOperator.LESS_THAN,
        FilterOperator.GREATER_THAN_OR_EQUAL,
        FilterOperator.LESS_THAN_OR_EQUAL
    ]),
    "address_group_count": FilterConfig("address_group_count", type_=int, operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.GREATER_THAN,
        FilterOperator.LESS_THAN,
        FilterOperator.GREATER_THAN_OR_EQUAL,
        FilterOperator.LESS_THAN_OR_EQUAL
    ]),
    "service_count": FilterConfig("service_count", type_=int, operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.GREATER_THAN,
        FilterOperator.LESS_THAN,
        FilterOperator.GREATER_THAN_OR_EQUAL,
        FilterOperator.LESS_THAN_OR_EQUAL
    ]),
    "service_group_count": FilterConfig("service_group_count", type_=int, operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.GREATER_THAN,
        FilterOperator.LESS_THAN,
        FilterOperator.GREATER_THAN_OR_EQUAL,
        FilterOperator.LESS_THAN_OR_EQUAL
    ]),
    "pre_security_rules_count": FilterConfig("pre_security_rules_count", type_=int, operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.GREATER_THAN,
        FilterOperator.LESS_THAN,
        FilterOperator.GREATER_THAN_OR_EQUAL,
        FilterOperator.LESS_THAN_OR_EQUAL
    ]),
    "post_security_rules_count": FilterConfig("post_security_rules_count", type_=int, operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.GREATER_THAN,
        FilterOperator.LESS_THAN,
        FilterOperator.GREATER_THAN_OR_EQUAL,
        FilterOperator.LESS_THAN_OR_EQUAL
    ]),
    "pre_nat_rules_count": FilterConfig("pre_nat_rules_count", type_=int, operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.GREATER_THAN,
        FilterOperator.LESS_THAN,
        FilterOperator.GREATER_THAN_OR_EQUAL,
        FilterOperator.LESS_THAN_OR_EQUAL
    ]),
    "post_nat_rules_count": FilterConfig("post_nat_rules_count", type_=int, operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.GREATER_THAN,
        FilterOperator.LESS_THAN,
        FilterOperator.GREATER_THAN_OR_EQUAL,
        FilterOperator.LESS_THAN_OR_EQUAL
    ]),
    "xpath": FilterConfig("xpath", operators=[
        FilterOperator.EQUALS,
        FilterOperator.CONTAINS,
        FilterOperator.STARTS_WITH
    ])
}))

# Address/Service group filters - comprehensive filtering for all properties
GROUP_FILTERS = FilterDefinition(create_filter_with_aliases({
    "name": FilterConfig("name", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS,
        FilterOperator.STARTS_WITH,
        FilterOperator.ENDS_WITH
    ]),
    "description": FilterConfig("description", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS,
        FilterOperator.STARTS_WITH,
        FilterOperator.ENDS_WITH
    ]),
    "member": FilterConfig(
        "members",
        custom_getter=lambda obj: (
            obj.static if hasattr(obj, 'static') and obj.static
            else obj.members if hasattr(obj, 'members')
            else []
        ),
        operators=[
            FilterOperator.IN,
            FilterOperator.NOT_IN,
            FilterOperator.CONTAINS,
            FilterOperator.NOT_CONTAINS
        ],
        type_=list
    ),
    "static": FilterConfig("static", operators=[
        FilterOperator.IN,
        FilterOperator.NOT_IN,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS
    ], type_=list),
    "tag": FilterConfig("tag", operators=[
        FilterOperator.IN,
        FilterOperator.NOT_IN,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS
    ], type_=list),
    "xpath": FilterConfig("xpath", operators=[
        FilterOperator.EQUALS,
        FilterOperator.CONTAINS,
        FilterOperator.STARTS_WITH
    ]),
    "parent_device_group": FilterConfig(
        "parent_device_group",
        custom_getter=lambda obj: (
            getattr(obj, 'parent_device_group', None) or
            getattr(obj, 'parent-device-group', None)
        ),
        operators=[
            FilterOperator.EQUALS,
            FilterOperator.NOT_EQUALS,
            FilterOperator.CONTAINS
        ]
    ),
    "parent_template": FilterConfig(
        "parent_template",
        custom_getter=lambda obj: (
            getattr(obj, 'parent_template', None) or
            getattr(obj, 'parent-template', None)
        ),
        operators=[
            FilterOperator.EQUALS,
            FilterOperator.NOT_EQUALS,
            FilterOperator.CONTAINS
        ]
    ),
    "parent_vsys": FilterConfig(
        "parent_vsys", 
        custom_getter=lambda obj: (
            getattr(obj, 'parent_vsys', None) or
            getattr(obj, 'parent-vsys', None)
        ),
        operators=[
            FilterOperator.EQUALS,
            FilterOperator.NOT_EQUALS,
            FilterOperator.CONTAINS
        ]
    )
}))

# Security profile filters - comprehensive filtering for all properties
PROFILE_FILTERS = FilterDefinition({
    "name": FilterConfig("name", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS,
        FilterOperator.STARTS_WITH,
        FilterOperator.ENDS_WITH
    ]),
    "description": FilterConfig("description", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS,
        FilterOperator.STARTS_WITH,
        FilterOperator.ENDS_WITH
    ]),
    "xpath": FilterConfig("xpath", operators=[
        FilterOperator.EQUALS,
        FilterOperator.CONTAINS,
        FilterOperator.STARTS_WITH
    ])
})

# NAT rule filters - comprehensive filtering for all properties
NAT_RULE_FILTERS = FilterDefinition({
    "name": FilterConfig("name", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS,
        FilterOperator.STARTS_WITH,
        FilterOperator.ENDS_WITH
    ]),
    "uuid": FilterConfig("uuid", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS
    ]),
    "source": FilterConfig("source", operators=[
        FilterOperator.IN,
        FilterOperator.NOT_IN,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS
    ], type_=list),
    "destination": FilterConfig("destination", operators=[
        FilterOperator.IN,
        FilterOperator.NOT_IN,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS
    ], type_=list),
    "source_zone": FilterConfig("from_", operators=[
        FilterOperator.IN,
        FilterOperator.NOT_IN,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS
    ], type_=list),
    "destination_zone": FilterConfig("to", operators=[
        FilterOperator.IN,
        FilterOperator.NOT_IN,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS
    ], type_=list),
    "service": FilterConfig("service", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS
    ]),
    "disabled": FilterConfig("disabled", type_=bool, operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS
    ]),
    "description": FilterConfig("description", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS,
        FilterOperator.STARTS_WITH,
        FilterOperator.ENDS_WITH
    ]),
    "tag": FilterConfig("tag", operators=[
        FilterOperator.IN,
        FilterOperator.NOT_IN,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS
    ], type_=list)
})

# Template filters - comprehensive filtering for all properties
TEMPLATE_FILTERS = FilterDefinition({
    "name": FilterConfig("name", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS,
        FilterOperator.STARTS_WITH,
        FilterOperator.ENDS_WITH
    ]),
    "description": FilterConfig("description", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS,
        FilterOperator.STARTS_WITH,
        FilterOperator.ENDS_WITH
    ]),
    "xpath": FilterConfig("xpath", operators=[
        FilterOperator.EQUALS,
        FilterOperator.CONTAINS,
        FilterOperator.STARTS_WITH
    ])
})

# Template stack filters - comprehensive filtering for all properties
TEMPLATE_STACK_FILTERS = FilterDefinition({
    "name": FilterConfig("name", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS,
        FilterOperator.STARTS_WITH,
        FilterOperator.ENDS_WITH
    ]),
    "description": FilterConfig("description", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS,
        FilterOperator.STARTS_WITH,
        FilterOperator.ENDS_WITH
    ]),
    "templates": FilterConfig("templates", operators=[
        FilterOperator.IN,
        FilterOperator.NOT_IN,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS
    ], type_=list),
    "xpath": FilterConfig("xpath", operators=[
        FilterOperator.EQUALS,
        FilterOperator.CONTAINS,
        FilterOperator.STARTS_WITH
    ])
})

# Log profile filters - comprehensive filtering for all properties
LOG_PROFILE_FILTERS = FilterDefinition({
    "name": FilterConfig("name", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS,
        FilterOperator.STARTS_WITH,
        FilterOperator.ENDS_WITH
    ]),
    "description": FilterConfig("description", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS,
        FilterOperator.STARTS_WITH,
        FilterOperator.ENDS_WITH
    ]),
    "xpath": FilterConfig("xpath", operators=[
        FilterOperator.EQUALS,
        FilterOperator.CONTAINS,
        FilterOperator.STARTS_WITH
    ])
})

# Schedule filters - comprehensive filtering for all properties
SCHEDULE_FILTERS = FilterDefinition({
    "name": FilterConfig("name", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS,
        FilterOperator.STARTS_WITH,
        FilterOperator.ENDS_WITH
    ]),
    "description": FilterConfig("description", operators=[
        FilterOperator.EQUALS,
        FilterOperator.NOT_EQUALS,
        FilterOperator.CONTAINS,
        FilterOperator.NOT_CONTAINS,
        FilterOperator.STARTS_WITH,
        FilterOperator.ENDS_WITH
    ]),
    "xpath": FilterConfig("xpath", operators=[
        FilterOperator.EQUALS,
        FilterOperator.CONTAINS,
        FilterOperator.STARTS_WITH
    ])
})