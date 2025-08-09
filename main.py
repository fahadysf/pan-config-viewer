from fastapi import FastAPI, HTTPException, Query, Path, Request
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Optional, Dict, Any, Set
import os
import glob
import asyncio
from parser import PanoramaXMLParser
from background_cache import background_cache
from models import (
    AddressObject, AddressGroup, ServiceObject, ServiceGroup,
    VulnerabilityProfile, AntivirusProfile, SpywareProfile,
    URLFilteringProfile, FileBlockingProfile, WildFireAnalysisProfile,
    DataFilteringProfile, SecurityProfileGroup, SecurityRule, NATRule,
    DeviceGroup, DeviceGroupSummary, Template, TemplateStack, LogSetting, Schedule,
    ZoneProtectionProfile, PaginationParams, PaginatedResponse
)
from filtering import (
    apply_filters, FilterDefinition, FilterConfig, FilterOperator,
    ADDRESS_FILTERS, SERVICE_FILTERS, SECURITY_RULE_FILTERS,
    DEVICE_GROUP_FILTERS, GROUP_FILTERS, PROFILE_FILTERS,
    NAT_RULE_FILTERS, TEMPLATE_FILTERS, TEMPLATE_STACK_FILTERS,
    LOG_PROFILE_FILTERS, SCHEDULE_FILTERS
)

# Initialize FastAPI app with comprehensive documentation
app = FastAPI(
    title="PAN-OS Panorama Configuration API",
    description="""
    This API provides real-time access to Panorama PAN-OS configuration data from XML files.
    
    ## Features
    
    * **Address Objects**: View and filter IP addresses, FQDNs, and address ranges
    * **Address Groups**: Access static and dynamic address groups
    * **Service Objects**: Browse TCP/UDP service definitions
    * **Service Groups**: View service group configurations
    * **Security Profiles**: Access antivirus, anti-spyware, vulnerability, URL filtering, and other security profiles
    * **Device Groups**: Browse device group hierarchies and configurations
    * **Templates**: Access device templates and template stacks
    * **Security Rules**: View pre and post security rules from device groups
    * **Log Profiles**: Access log forwarding profiles
    * **Schedules**: View time-based schedule configurations
    
    ## Pagination
    
    All list endpoints support pagination to efficiently handle large datasets:
    
    ### Query Parameters
    
    * **page** (int): Page number, starting from 1 (default: 1)
    * **page_size** (int): Number of items per page, 1-10000 (default: 500)
    * **disable_paging** (bool): Return all results without pagination (default: false)
    
    ### Response Format
    
    Paginated responses include:
    ```json
    {
        "items": [...],           // Array of items for current page
        "total_items": 1500,      // Total number of items
        "page": 1,                // Current page number
        "page_size": 500,         // Items per page
        "total_pages": 3,         // Total number of pages
        "has_next": true,         // Whether there is a next page
        "has_previous": false     // Whether there is a previous page
    }
    ```
    
    ### Example Usage
    
    ```bash
    # Get first page with default page size (500 items)
    GET /api/v1/configs/production/addresses
    
    # Get second page with 100 items per page
    GET /api/v1/configs/production/addresses?page=2&page_size=100
    
    # Get all items without pagination
    GET /api/v1/configs/production/addresses?disable_paging=true
    
    # Combine pagination with filtering
    GET /api/v1/configs/production/addresses?name=server&page=1&page_size=50
    ```
    
    ## Filtering
    
    All list endpoints support comprehensive filtering using two syntaxes.
    This includes both shared object endpoints and device-group/template specific endpoints:
    
    ### 1. Basic Query Parameters
    Simple filters using standard query parameters:
    - `name=firewall` - Filter by name (partial match)
    - `tag=production` - Filter by tag
    - `location=shared` - Filter by location
    - `protocol=tcp` - Filter by protocol (for services)
    
    ### 2. Advanced Filter Syntax
    Use `filter.property.operator=value` for precise filtering.
    If no operator is specified, `contains` is used by default: `filter.property=value`
    
    #### Available Operators:
    - `eq` or `equals` - Exact match
    - `ne` or `not_equals` - Not equal to value
    - `contains` - Contains substring (default if no operator specified)
    - `not_contains` - Does not contain substring
    - `starts_with` - Starts with value
    - `ends_with` - Ends with value
    - `in` - Value in list (for array fields)
    - `not_in` - Value not in list
    - `gt` - Greater than (numeric comparisons)
    - `lt` - Less than (numeric comparisons)
    - `gte` - Greater than or equal
    - `lte` - Less than or equal
    - `regex` - Regular expression match
    - `exists` - Field exists (for optional fields)
    
    #### Filter Examples:
    ```
    # Name contains "firewall" (default operator)
    filter.name=firewall
    
    # Name equals exactly "firewall-01"
    filter.name.equals=firewall-01
    
    # IP starts with "10."
    filter.ip.starts_with=10.
    
    # Port greater than 8000
    filter.port.gt=8000
    
    # Has "production" tag
    filter.tag.in=production
    
    # Name matches regex pattern
    filter.name.regex=^fw-.*-\\d+$
    
    # Multiple filters (AND logic)
    filter.protocol.eq=tcp&filter.port.gte=8000&filter.port.lte=9000
    
    # Device-group specific endpoints (same filtering syntax!)
    GET /api/v1/configs/pan/device-groups/DMZ/addresses?filter.name.contains=server
    GET /api/v1/configs/pan/device-groups/HQ/services?filter.protocol.eq=tcp
    ```
    
    ### Object-Specific Filters
    
    #### Address Objects:
    - `name`, `ip`, `ip_netmask`, `ip_range`, `fqdn`, `type`, `tag`, `description`
    - `parent_device_group`, `parent_template`, `parent_vsys`
    
    #### Service Objects:
    - `name`, `protocol`, `port`, `tag`, `description`
    - `parent_device_group`, `parent_template`
    
    #### Security Rules:
    - `name`, `uuid`, `source`, `destination`, `source_zone`, `dest_zone`
    - `application`, `service`, `action`, `disabled`, `source_user`
    - `category`, `tag`, `device_group`, `rule_type`, `log_start`, `log_end`
    
    #### Device Groups:
    - `name`, `parent`, `parent_dg`, `description`
    - `devices_count`, `address_count`, `service_count`
    - `pre_security_rules_count`, `post_security_rules_count`
    
    ## Data Source
    
    This API reads configuration data directly from the Panorama XML backup file.
    The data is parsed in real-time, ensuring you always see the current configuration.
    """,
    version="1.0.0",
    contact={
        "name": "PAN-OS API Support",
        "email": "support@example.com"
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html"
    },
    tags_metadata=[
        {
            "name": "Configuration",
            "description": "Configuration file management and selection"
        },
        {
            "name": "Address Objects",
            "description": "Operations related to address objects and address groups"
        },
        {
            "name": "Service Objects", 
            "description": "Operations related to service objects and service groups"
        },
        {
            "name": "Security Profiles",
            "description": "Operations for security profiles (AV, AS, VP, URL, etc.)"
        },
        {
            "name": "Device Management",
            "description": "Device groups, templates, and template stacks"
        },
        {
            "name": "Policies",
            "description": "Security rules and NAT rules"
        },
        {
            "name": "Logging",
            "description": "Log profiles and settings"
        },
        {
            "name": "Search",
            "description": "Search configuration objects by various criteria"
        },
        {
            "name": "System",
            "description": "System health and status endpoints"
        }
    ]
)

# Configuration
CONFIG_FILES_PATH = os.environ.get("CONFIG_FILES_PATH", "./config-files")
parsers: Dict[str, PanoramaXMLParser] = {}
available_configs: List[str] = []
# Track which configs are fully loaded and ready
ready_configs: Set[str] = set()
# Track configs currently being loaded
loading_configs: Set[str] = set()

# Templates removed - using React frontend instead

async def load_and_cache_config(config_name: str) -> None:
    """Load a configuration and fully cache all its objects synchronously"""
    import time
    start_time = time.time()
    xml_path = os.path.join(CONFIG_FILES_PATH, f"{config_name}.xml")
    
    print(f"  Parsing XML file...")
    # Parse the XML file
    parser = PanoramaXMLParser(xml_path)
    parsers[config_name] = parser
    
    # Define what to cache with proper method names
    cache_methods = [
        ('addresses', 'get_all_addresses'),
        ('address_groups', 'get_address_groups'),
        ('services', 'get_shared_services'),
        ('service_groups', 'get_shared_service_groups'),
        ('device_groups', 'get_device_group_summaries'),
        ('templates', 'get_templates'),
        ('vulnerability_profiles', 'get_vulnerability_profiles'),
        ('url_filtering_profiles', 'get_url_filtering_profiles'),
    ]
    
    total_items = 0
    # Cache each object type
    for obj_type, method_name in cache_methods:
        try:
            if hasattr(parser, method_name):
                print(f"  Caching {obj_type}...", end=" ", flush=True)
                method = getattr(parser, method_name)
                items = method()
                
                # Store in background cache
                cache_key = f"{config_name}:{obj_type}"
                background_cache.cache[cache_key] = {
                    'items': items,
                    'timestamp': time.time()
                }
                
                item_count = len(items) if items else 0
                total_items += item_count
                print(f"{item_count} items")
        except Exception as e:
            print(f"Failed: {e}")
    
    # Mark this config as fully cached
    background_cache.mark_config_ready(config_name)
    
    elapsed = time.time() - start_time
    print(f"  Total: {total_items} items cached in {elapsed:.2f} seconds")

@app.on_event("startup")
async def startup_event():
    """Scan for XML files and pre-load/cache them on startup"""
    global available_configs, ready_configs, loading_configs
    
    if not os.path.exists(CONFIG_FILES_PATH):
        os.makedirs(CONFIG_FILES_PATH, exist_ok=True)
    
    # Find all XML files in the config directory
    xml_files = glob.glob(os.path.join(CONFIG_FILES_PATH, "*.xml"))
    
    if not xml_files:
        print(f"Warning: No XML files found in {CONFIG_FILES_PATH}")
        return
    
    # Store available config names (without path and extension)
    available_configs = [os.path.splitext(os.path.basename(f))[0] for f in xml_files]
    print(f"Found {len(available_configs)} configuration files: {available_configs}")
    
    # Pre-load and fully cache each configuration
    print("Pre-loading and caching all configurations...")
    for config_name in available_configs:
        print(f"Loading configuration: {config_name}")
        loading_configs.add(config_name)
        
        try:
            # Load the parser and trigger full caching synchronously
            await load_and_cache_config(config_name)
            ready_configs.add(config_name)
            print(f"✓ Configuration '{config_name}' fully loaded and cached")
        except Exception as e:
            print(f"✗ Failed to load configuration '{config_name}': {e}")
        finally:
            loading_configs.discard(config_name)
    
    print(f"Startup complete. {len(ready_configs)}/{len(available_configs)} configurations ready.")

def get_parser(config_name: str) -> PanoramaXMLParser:
    """Get parser for a specific config file (must be fully loaded)"""
    # Check if config is ready
    if config_name not in ready_configs:
        if config_name in loading_configs:
            raise HTTPException(
                status_code=503,  # Service Unavailable
                detail=f"Configuration '{config_name}' is still being loaded. Please try again later."
            )
        elif config_name in available_configs:
            raise HTTPException(
                status_code=503,  # Service Unavailable
                detail=f"Configuration '{config_name}' failed to load or is not ready."
            )
        else:
            raise HTTPException(
                status_code=404, 
                detail=f"Configuration '{config_name}' not found. Available configs: {list(ready_configs)}"
            )
    
    # Return the pre-loaded parser
    if config_name not in parsers:
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: Configuration '{config_name}' marked as ready but parser not found."
        )
    
    return parsers[config_name]

def paginate_results(items: List, pagination: PaginationParams) -> Dict:
    """Apply pagination to a list of items and return paginated response"""
    if pagination.disable_paging:
        return {
            "items": items,
            "total_items": len(items),
            "page": 1,
            "page_size": len(items),
            "total_pages": 1,
            "has_next": False,
            "has_previous": False
        }
    
    total_items = len(items)
    total_pages = (total_items + pagination.page_size - 1) // pagination.page_size
    
    # Calculate start and end indices
    start_idx = (pagination.page - 1) * pagination.page_size
    end_idx = start_idx + pagination.page_size
    
    # Get the page of items
    paginated_items = items[start_idx:end_idx]
    
    return {
        "items": paginated_items,
        "total_items": total_items,
        "page": pagination.page,
        "page_size": pagination.page_size,
        "total_pages": total_pages,
        "has_next": pagination.page < total_pages,
        "has_previous": pagination.page > 1
    }

def parse_filter_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """Parse filter parameters from request with validation
    
    Supports dot notation for filters:
    - filter.name=value (defaults to contains operator)
    - filter.name.equals=value (explicit operator)
    - filter.name.starts_with=value
    """
    filters = {}
    
    # Create a mapping of operator aliases to their enum values
    operator_aliases = {
        'eq': 'eq',
        'equals': 'eq',
        'ne': 'ne',
        'not_equals': 'ne',
        'contains': 'contains',
        'not_contains': 'not_contains',
        'starts_with': 'starts_with',
        'ends_with': 'ends_with',
        'in': 'in',
        'not_in': 'not_in',
        'gt': 'gt',
        'greater_than': 'gt',
        'lt': 'lt',
        'less_than': 'lt',
        'gte': 'gte',
        'greater_than_or_equal': 'gte',
        'lte': 'lte',
        'less_than_or_equal': 'lte',
        'regex': 'regex',
        'exists': 'exists'
    }
    
    for key, value in params.items():
        if key.startswith('filter.') and value is not None:
            try:
                # Extract field name and operator from filter.field or filter.field.operator
                filter_key = key[7:]  # Remove 'filter.' prefix
                
                # Validate filter key format
                if not filter_key:
                    raise HTTPException(status_code=400, detail=f"Invalid filter format: {key}")
                
                # Check if there's an operator specified
                parts = filter_key.rsplit('.', 1)  # Split from the right to handle field names with dots
                
                # Check if the last part is an operator alias
                if len(parts) == 2 and parts[1] in operator_aliases:
                    # filter.field.operator format
                    field, op_alias = parts
                    if not field:
                        raise HTTPException(status_code=400, detail=f"Invalid filter format: {key}")
                    # Map the alias to the actual operator value
                    op = operator_aliases[op_alias]
                    filters[f"{field}_{op}"] = value
                else:
                    # filter.field format (default to contains operator)
                    filters[filter_key] = value
                    
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Error parsing filter {key}: {str(e)}")
    return filters

@app.get("/", include_in_schema=False)
async def root():
    """Serve the React frontend"""
    # Check if we have a built React app
    if os.path.exists("static/dist/index.html"):
        return FileResponse("static/dist/index.html")
    else:
        # Fallback to API docs if no frontend is built
        return RedirectResponse(url="/docs")


# Configuration Management Endpoints
@app.get("/api/v1/configs",
         tags=["Configuration"],
         summary="List available configurations",
         description="Get a list of all fully loaded and cached XML configuration files")
async def list_configs():
    """List all fully loaded and cached configuration files
    
    Only returns configurations that have been completely parsed and cached.
    Configurations still being loaded will not appear in this list.
    """
    # Only return configs that are ready
    return {
        "configs": list(ready_configs),
        "count": len(ready_configs),
        "path": CONFIG_FILES_PATH,
        "loading": list(loading_configs),
        "total_available": len(available_configs)
    }

@app.get("/api/v1/configs/{config_name}/info",
         tags=["Configuration"],
         summary="Get configuration info",
         description="Get information about a specific configuration file")
async def get_config_info(
    config_name: str = Path(..., description="Configuration name (without .xml extension)")
):
    """Get information about a specific configuration"""
    # Check if config exists
    if config_name not in available_configs:
        raise HTTPException(
            status_code=404,
            detail=f"Configuration '{config_name}' not found"
        )
    
    xml_path = os.path.join(CONFIG_FILES_PATH, f"{config_name}.xml")
    
    return {
        "name": config_name,
        "path": xml_path,
        "size": os.path.getsize(xml_path),
        "modified": os.path.getmtime(xml_path),
        "ready": config_name in ready_configs,
        "loading": config_name in loading_configs,
        "cached": background_cache.is_config_ready(config_name)
    }

# Address Objects Endpoints
@app.get("/api/v1/configs/{config_name}/addresses", 
         response_model=PaginatedResponse,
         tags=["Address Objects"],
         summary="Get all address objects",
         description="Retrieve all shared address objects from the configuration. Supports filtering by name and tags, with pagination.")
async def get_addresses(
    request: Request,
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    name: Optional[str] = Query(None, description="Filter by address name (partial match)"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    location: Optional[str] = Query("all", description="Filter by location (all/shared/device-group/template/vsys)"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(500, ge=1, le=10000, description="Number of items per page"),
    disable_paging: bool = Query(False, description="Return all results without pagination")
):
    """Get address objects with optional filtering and pagination
    
    Supports comprehensive filtering on all address properties:
    
    **Basic filters:**
    - name: Filter by name (partial match)
    - tag: Filter by tag
    - location: Filter by location (all/shared/device-group/template/vsys)
    
    **Advanced filters using filter[property] syntax:**
    - filter[name]: Name filtering with operators
    - filter[ip]: IP address filtering (alias for ip_netmask)
    - filter[ip_netmask]: IP address with netmask filtering
    - filter[ip_range]: IP range filtering
    - filter[fqdn]: Fully qualified domain name filtering
    - filter[description]: Description filtering
    - filter[tag]: Tag filtering (supports list operations)
    - filter[xpath]: XPath location filtering
    - filter[parent_device_group]: Parent device group filtering
    - filter[parent_template]: Parent template filtering
    - filter[parent_vsys]: Parent vsys filtering
    - filter[location]: Location type filtering (shared/device-group/template/vsys)
    
    **Supported operators:**
    - [eq]: Exact match (e.g., filter[name][eq]=web-server)
    - [ne]: Not equals
    - [contains]: Contains substring (default for most fields)
    - [not_contains]: Does not contain
    - [starts_with]: Starts with prefix
    - [ends_with]: Ends with suffix
    - [in]: Value in list (for tags)
    - [not_in]: Value not in list
    
    **Examples:**
    - filter[name][starts_with]=web
    - filter[ip][contains]=10.0.0
    - filter[tag][in]=production
    - filter[description][not_contains]=test
    - filter[parent_device_group][eq]=branch-offices
    """
    # Check if we have cached data first
    # Parse filter parameters to check for advanced filters
    advanced_filters = parse_filter_params(dict(request.query_params))
    
    # Only use cache if no advanced filters are present
    if background_cache.is_cached(config_name, 'addresses') and not advanced_filters:
        # Check if simple filters are being applied
        has_simple_filters = (name or tag or location != "all")
        
        if not has_simple_filters:
            # No filters - return paginated cached data directly
            cached_data = background_cache.get_cached_data(config_name, 'addresses', page, page_size)
            if cached_data:
                return cached_data
        else:
            # Simple filters present - use cached filtering
            filtered_data = background_cache.get_filtered_cached_data(
                config_name, 'addresses',
                filters={
                    'location': location,
                    'name': name,
                    'tag': tag,
                    'advanced': {}  # No advanced filters
                },
                page=page,
                page_size=page_size
            )
            if filtered_data:
                return filtered_data
    
    # Fall back to parser if no cache available
    parser = get_parser(config_name)
    
    # Get addresses based on location filter
    if location == "shared":
        addresses = parser.get_shared_addresses()
    else:
        addresses = parser.get_all_addresses()
        
    # Additional filtering based on location
    if location == "device-group":
        addresses = [a for a in addresses if a.parent_device_group is not None]
    elif location == "template":
        addresses = [a for a in addresses if a.parent_template is not None]
    elif location == "vsys":
        addresses = [a for a in addresses if a.parent_vsys is not None]
    
    # Apply legacy filters for backwards compatibility
    if name:
        addresses = [a for a in addresses if name.lower() in a.name.lower()]
    if tag:
        addresses = [a for a in addresses if a.tag and tag in a.tag]
    
    # Apply advanced filters (already parsed above)
    if advanced_filters:
        addresses = apply_filters(addresses, advanced_filters, ADDRESS_FILTERS)
    
    # Apply pagination
    pagination = PaginationParams(page=page, page_size=page_size, disable_paging=disable_paging)
    return paginate_results(addresses, pagination)

@app.get("/api/v1/configs/{config_name}/addresses/{address_name}",
         response_model=AddressObject,
         tags=["Address Objects"],
         summary="Get specific address object",
         description="Retrieve a specific address object by its exact name, including location details")
async def get_address(
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    address_name: str = Path(..., description="Address object name")
):
    """Get a specific address object by name"""
    parser = get_parser(config_name)
    # Search in all locations
    addresses = parser.get_all_addresses()
    for address in addresses:
        if address.name == address_name:
            return address
    raise HTTPException(status_code=404, detail=f"Address '{address_name}' not found")

@app.get("/api/v1/configs/{config_name}/address-groups",
         response_model=PaginatedResponse,
         tags=["Address Objects"],
         summary="Get all address groups",
         description="Retrieve all shared address groups including static and dynamic groups, with pagination")
async def get_address_groups(
    request: Request,
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    name: Optional[str] = Query(None, description="Filter by group name (partial match)"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(500, ge=1, le=10000, description="Number of items per page"),
    disable_paging: bool = Query(False, description="Return all results without pagination")
):
    """Get all shared address groups with optional filtering and pagination
    
    Supports comprehensive filtering on all address group properties:
    
    **Basic filters:**
    - name: Filter by group name (partial match)
    - tag: Filter by tag
    
    **Advanced filters using filter[property] syntax:**
    - filter[name]: Name filtering with operators
    - filter[description]: Description filtering
    - filter[member]: Filter by member addresses (supports list operations)
    - filter[static]: Filter by static members
    - filter[tag]: Tag filtering (supports list operations)
    - filter[xpath]: XPath location filtering
    - filter[parent_device_group]: Parent device group filtering
    - filter[parent_template]: Parent template filtering
    - filter[parent_vsys]: Parent vsys filtering
    
    **Supported operators:**
    - [eq], [ne]: Exact match / not equals
    - [contains], [not_contains]: Contains / does not contain
    - [starts_with], [ends_with]: String prefix/suffix matching
    - [in], [not_in]: List membership operations
    
    **Examples:**
    - filter[member][contains]=web-server
    - filter[tag][in]=production
    - filter[description][starts_with]=DMZ
    """
    # Check if we have cached data first
    if background_cache.is_cached(config_name, 'address_groups'):
        # Get all cached items for filtering
        all_cached_data = background_cache.get_cached_data(config_name, 'address_groups', page=1, page_size=999999)
        if all_cached_data:
            items = all_cached_data['items']
            
            # Apply legacy filters
            if name:
                items = [g for g in items if name.lower() in g.get('name', '').lower()]
            if tag:
                items = [g for g in items if g.get('tag') and tag in g.get('tag')]
            
            # Apply advanced filters
            filter_params = parse_filter_params(dict(request.query_params))
            if filter_params:
                # Convert dict items to objects for filter compatibility
                from types import SimpleNamespace
                items = [SimpleNamespace(**item) for item in items]
                items = apply_filters(items, filter_params, GROUP_FILTERS)
                # Convert back to dicts
                items = [vars(item) for item in items]
            
            # Now apply pagination after filtering
            total_items = len(items)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_items = items[start_idx:end_idx]
            
            return {
                "items": paginated_items,
                "total_items": total_items,
                "page": page,
                "page_size": page_size,
                "total_pages": (total_items + page_size - 1) // page_size,
                "has_next": end_idx < total_items,
                "has_previous": page > 1,
                "from_cache": True
            }
    
    # Fall back to parser if no cache available
    parser = get_parser(config_name)
    groups = parser.get_shared_address_groups()
    
    # Apply legacy filters for backwards compatibility
    if name:
        groups = [g for g in groups if name.lower() in g.name.lower()]
    if tag:
        groups = [g for g in groups if g.tag and tag in g.tag]
    
    # Apply advanced filters
    filter_params = parse_filter_params(dict(request.query_params))
    if filter_params:
        groups = apply_filters(groups, filter_params, GROUP_FILTERS)
    
    # Apply pagination
    pagination = PaginationParams(page=page, page_size=page_size, disable_paging=disable_paging)
    return paginate_results(groups, pagination)

@app.get("/api/v1/configs/{config_name}/address-groups/{group_name}",
         response_model=AddressGroup,
         tags=["Address Objects"],
         summary="Get specific address group",
         description="Retrieve a specific address group by its exact name")
async def get_address_group(
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    group_name: str = Path(..., description="Address group name")
):
    """Get a specific address group by name"""
    parser = get_parser(config_name)
    groups = parser.get_shared_address_groups()
    for group in groups:
        if group.name == group_name:
            return group
    raise HTTPException(status_code=404, detail=f"Address group '{group_name}' not found")

# Service Objects Endpoints
@app.get("/api/v1/configs/{config_name}/services",
         response_model=PaginatedResponse,
         tags=["Service Objects"],
         summary="Get all service objects",
         description="Retrieve all shared service objects with protocol definitions, with pagination")
async def get_services(
    request: Request,
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    name: Optional[str] = Query(None, description="Filter by service name (partial match)"),
    protocol: Optional[str] = Query(None, description="Filter by protocol (tcp/udp)"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(500, ge=1, le=10000, description="Number of items per page"),
    disable_paging: bool = Query(False, description="Return all results without pagination")
):
    """Get all shared service objects with optional filtering and pagination
    
    Supports comprehensive filtering on all service properties:
    
    **Basic filters:**
    - name: Filter by service name (partial match)
    - protocol: Filter by protocol (tcp/udp)
    
    **Advanced filters using filter[property] syntax:**
    - filter[name]: Name filtering with operators
    - filter[protocol]: Protocol filtering (tcp/udp)
    - filter[port]: Port number filtering (supports numeric comparisons)
    - filter[source_port]: Source port filtering
    - filter[description]: Description filtering
    - filter[tag]: Tag filtering (supports list operations)
    - filter[xpath]: XPath location filtering
    - filter[parent_device_group]: Parent device group filtering
    - filter[parent_template]: Parent template filtering
    - filter[parent_vsys]: Parent vsys filtering
    
    **Supported operators:**
    - [eq], [ne]: Exact match / not equals
    - [contains], [not_contains]: Contains / does not contain
    - [starts_with], [ends_with]: String prefix/suffix matching
    - [gt], [lt], [gte], [lte]: Numeric comparisons (for port numbers)
    - [in], [not_in]: List membership operations
    
    **Examples:**
    - filter[port][gte]=1024
    - filter[port][lte]=49151
    - filter[protocol][eq]=tcp
    - filter[tag][contains]=web
    """
    # Check if we have cached data first
    if background_cache.is_cached(config_name, 'services'):
        # Get all cached items for filtering
        all_cached_data = background_cache.get_cached_data(config_name, 'services', page=1, page_size=999999)
        if all_cached_data:
            items = all_cached_data['items']
            
            # Apply legacy filters
            if name:
                items = [s for s in items if name.lower() in s.get('name', '').lower()]
            if protocol and protocol.lower() in ["tcp", "udp"]:
                items = [s for s in items if s.get('protocol', {}).get(protocol.lower())]
            
            # Apply advanced filters
            filter_params = parse_filter_params(dict(request.query_params))
            if filter_params:
                # Convert dict items to objects for filter compatibility
                from types import SimpleNamespace
                items = [SimpleNamespace(**item) for item in items]
                items = apply_filters(items, filter_params, SERVICE_FILTERS)
                # Convert back to dicts
                items = [vars(item) for item in items]
            
            # Now apply pagination after filtering
            total_items = len(items)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_items = items[start_idx:end_idx]
            
            return {
                "items": paginated_items,
                "total_items": total_items,
                "page": page,
                "page_size": page_size,
                "total_pages": (total_items + page_size - 1) // page_size,
                "has_next": end_idx < total_items,
                "has_previous": page > 1,
                "from_cache": True
            }
    
    # Fall back to parser if no cache available
    parser = get_parser(config_name)
    services = parser.get_shared_services()
    
    # Apply legacy filters for backwards compatibility
    if name:
        services = [s for s in services if name.lower() in s.name.lower()]
    if protocol and protocol.lower() in ["tcp", "udp"]:
        services = [s for s in services if hasattr(s.protocol, protocol.lower()) and getattr(s.protocol, protocol.lower())]
    
    # Apply advanced filters
    filter_params = parse_filter_params(dict(request.query_params))
    if filter_params:
        services = apply_filters(services, filter_params, SERVICE_FILTERS)
    
    # Apply pagination
    pagination = PaginationParams(page=page, page_size=page_size, disable_paging=disable_paging)
    return paginate_results(services, pagination)

@app.get("/api/v1/configs/{config_name}/services/{service_name}",
         response_model=ServiceObject,
         tags=["Service Objects"],
         summary="Get specific service object",
         description="Retrieve a specific service object by its exact name")
async def get_service(
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    service_name: str = Path(..., description="Service object name")
):
    """Get a specific service object by name"""
    parser = get_parser(config_name)
    services = parser.get_shared_services()
    for service in services:
        if service.name == service_name:
            return service
    raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")

@app.get("/api/v1/configs/{config_name}/service-groups",
         response_model=PaginatedResponse,
         tags=["Service Objects"],
         summary="Get all service groups",
         description="Retrieve all shared service groups, with pagination")
async def get_service_groups(
    request: Request,
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    name: Optional[str] = Query(None, description="Filter by group name (partial match)"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(500, ge=1, le=10000, description="Number of items per page"),
    disable_paging: bool = Query(False, description="Return all results without pagination")
):
    """Get all shared service groups with optional filtering and pagination
    
    Supports advanced filtering with the following parameters:
    - filter[name]: Filter by group name
    - filter[description]: Filter by description
    - filter[member]: Filter by member services
    - filter[tag]: Filter by tags
    """
    parser = get_parser(config_name)
    groups = parser.get_shared_service_groups()
    
    # Apply legacy filters for backwards compatibility
    if name:
        groups = [g for g in groups if name.lower() in g.name.lower()]
    
    # Apply advanced filters
    filter_params = parse_filter_params(dict(request.query_params))
    if filter_params:
        groups = apply_filters(groups, filter_params, GROUP_FILTERS)
    
    # Apply pagination
    pagination = PaginationParams(page=page, page_size=page_size, disable_paging=disable_paging)
    return paginate_results(groups, pagination)

# Shared Location Endpoints
@app.get("/api/v1/configs/{config_name}/shared/addresses",
         response_model=PaginatedResponse,
         tags=["Address Objects"],
         summary="Get shared address objects",
         description="Retrieve all address objects defined in the shared location, with pagination")
async def get_shared_addresses(
    request: Request,
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    name: Optional[str] = Query(None, description="Filter by address name (partial match)"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(500, ge=1, le=10000, description="Number of items per page"),
    disable_paging: bool = Query(False, description="Return all results without pagination")
):
    """Get all shared address objects with pagination"""
    parser = get_parser(config_name)
    addresses = parser.get_shared_addresses()
    
    if name:
        addresses = [a for a in addresses if name.lower() in a.name.lower()]
    
    # Ensure all have location set to shared
    for addr in addresses:
        addr.parent_device_group = None
        addr.parent_template = None
        addr.parent_vsys = None
    
    # Apply advanced filters
    filter_params = parse_filter_params(dict(request.query_params))
    if filter_params:
        addresses = apply_filters(addresses, filter_params, ADDRESS_FILTERS)
    
    # Apply pagination
    pagination = PaginationParams(page=page, page_size=page_size, disable_paging=disable_paging)
    return paginate_results(addresses, pagination)

@app.get("/api/v1/configs/{config_name}/shared/address-groups",
         response_model=PaginatedResponse,
         tags=["Address Objects"],
         summary="Get shared address groups",
         description="Retrieve all address groups defined in the shared location, with pagination")
async def get_shared_address_groups_endpoint(
    request: Request,
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    name: Optional[str] = Query(None, description="Filter by group name (partial match)"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(500, ge=1, le=10000, description="Number of items per page"),
    disable_paging: bool = Query(False, description="Return all results without pagination")
):
    """Get all shared address groups with pagination"""
    parser = get_parser(config_name)
    groups = parser.get_shared_address_groups()
    
    if name:
        groups = [g for g in groups if name.lower() in g.name.lower()]
    
    # Ensure all have location set to shared
    for group in groups:
        group.parent_device_group = None
        group.parent_template = None
        group.parent_vsys = None
    
    # Apply advanced filters
    filter_params = parse_filter_params(dict(request.query_params))
    if filter_params:
        groups = apply_filters(groups, filter_params, GROUP_FILTERS)
    
    # Apply pagination
    pagination = PaginationParams(page=page, page_size=page_size, disable_paging=disable_paging)
    return paginate_results(groups, pagination)

@app.get("/api/v1/configs/{config_name}/shared/services",
         response_model=PaginatedResponse,
         tags=["Service Objects"],
         summary="Get shared service objects",
         description="Retrieve all service objects defined in the shared location, with pagination")
async def get_shared_services(
    request: Request,
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    name: Optional[str] = Query(None, description="Filter by service name (partial match)"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(500, ge=1, le=10000, description="Number of items per page"),
    disable_paging: bool = Query(False, description="Return all results without pagination")
):
    """Get all shared service objects with pagination"""
    parser = get_parser(config_name)
    services = parser.get_shared_services()
    
    if name:
        services = [s for s in services if name.lower() in s.name.lower()]
    
    # Ensure all have location set to shared
    for svc in services:
        svc.parent_device_group = None
        svc.parent_template = None
        svc.parent_vsys = None
    
    # Apply advanced filters
    filter_params = parse_filter_params(dict(request.query_params))
    if filter_params:
        services = apply_filters(services, filter_params, SERVICE_FILTERS)
    
    # Apply pagination
    pagination = PaginationParams(page=page, page_size=page_size, disable_paging=disable_paging)
    return paginate_results(services, pagination)

@app.get("/api/v1/configs/{config_name}/shared/service-groups",
         response_model=PaginatedResponse,
         tags=["Service Objects"],
         summary="Get shared service groups",
         description="Retrieve all service groups defined in the shared location, with pagination")
async def get_shared_service_groups_endpoint(
    request: Request,
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    name: Optional[str] = Query(None, description="Filter by group name (partial match)"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(500, ge=1, le=10000, description="Number of items per page"),
    disable_paging: bool = Query(False, description="Return all results without pagination")
):
    """Get all shared service groups with pagination"""
    parser = get_parser(config_name)
    groups = parser.get_shared_service_groups()
    
    if name:
        groups = [g for g in groups if name.lower() in g.name.lower()]
    
    # Ensure all have location set to shared
    for group in groups:
        group.parent_device_group = None
        group.parent_template = None
        group.parent_vsys = None
    
    # Apply advanced filters
    filter_params = parse_filter_params(dict(request.query_params))
    if filter_params:
        groups = apply_filters(groups, filter_params, GROUP_FILTERS)
    
    # Apply pagination
    pagination = PaginationParams(page=page, page_size=page_size, disable_paging=disable_paging)
    return paginate_results(groups, pagination)

# Security Profiles Endpoints
@app.get("/api/v1/configs/{config_name}/security-profiles/vulnerability",
         response_model=PaginatedResponse,
         tags=["Security Profiles"],
         summary="Get vulnerability protection profiles",
         description="Retrieve all vulnerability protection profiles with their rules, with pagination")
async def get_vulnerability_profiles(
    request: Request,
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    name: Optional[str] = Query(None, description="Filter by profile name (partial match)"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(500, ge=1, le=10000, description="Number of items per page"),
    disable_paging: bool = Query(False, description="Return all results without pagination")
):
    """Get all vulnerability protection profiles with pagination"""
    parser = get_parser(config_name)
    profiles = parser.get_vulnerability_profiles()
    
    if name:
        profiles = [p for p in profiles if name.lower() in p.name.lower()]
    
    # Apply advanced filters
    filter_params = parse_filter_params(dict(request.query_params))
    if filter_params:
        profiles = apply_filters(profiles, filter_params, PROFILE_FILTERS)
    
    # Apply pagination
    pagination = PaginationParams(page=page, page_size=page_size, disable_paging=disable_paging)
    return paginate_results(profiles, pagination)

@app.get("/api/v1/configs/{config_name}/security-profiles/url-filtering",
         response_model=PaginatedResponse,
         tags=["Security Profiles"],
         summary="Get URL filtering profiles",
         description="Retrieve all URL filtering profiles with category actions, with pagination")
async def get_url_filtering_profiles(
    request: Request,
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    name: Optional[str] = Query(None, description="Filter by profile name (partial match)"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(500, ge=1, le=10000, description="Number of items per page"),
    disable_paging: bool = Query(False, description="Return all results without pagination")
):
    """Get all URL filtering profiles with pagination"""
    parser = get_parser(config_name)
    profiles = parser.get_url_filtering_profiles()
    
    if name:
        profiles = [p for p in profiles if name.lower() in p.name.lower()]
    
    # Apply advanced filters
    filter_params = parse_filter_params(dict(request.query_params))
    if filter_params:
        profiles = apply_filters(profiles, filter_params, PROFILE_FILTERS)
    
    # Apply pagination
    pagination = PaginationParams(page=page, page_size=page_size, disable_paging=disable_paging)
    return paginate_results(profiles, pagination)

# Device Management Endpoints
@app.get("/api/v1/configs/{config_name}/device-groups",
         response_model=PaginatedResponse,
         tags=["Device Management"],
         summary="Get all device groups summary",
         description="Retrieve all device groups with counts of their child objects, with pagination")
async def get_device_groups(
    request: Request,
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    name: Optional[str] = Query(None, description="Filter by device group name (partial match)"),
    parent: Optional[str] = Query(None, description="Filter by parent device group"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(500, ge=1, le=10000, description="Number of items per page"),
    disable_paging: bool = Query(False, description="Return all results without pagination")
):
    """Get all device groups with counts of child objects and pagination
    
    Supports comprehensive filtering on all device group properties:
    
    **Basic filters:**
    - name: Filter by device group name (partial match)
    - parent: Filter by parent device group
    
    **Advanced filters using filter[property] syntax:**
    - filter[name]: Name filtering with operators
    - filter[parent]: Parent device group filtering (alias for parent_dg)
    - filter[parent_dg]: Parent device group filtering
    - filter[description]: Description filtering
    - filter[devices_count]: Filter by device count (numeric comparisons)
    - filter[address_count]: Filter by address object count (numeric comparisons)
    - filter[xpath]: XPath location filtering
    
    **Supported operators:**
    - [eq], [ne]: Exact match / not equals
    - [contains], [not_contains]: Contains / does not contain
    - [starts_with], [ends_with]: String prefix/suffix matching
    - [gt], [lt], [gte], [lte]: Numeric comparisons (for count fields)
    
    **Examples:**
    - filter[parent_dg][eq]=headquarters
    - filter[devices_count][gte]=10
    - filter[address_count][lt]=100
    - filter[description][contains]=branch
    """
    # Check if we have cached data first
    if background_cache.is_cached(config_name, 'device_groups'):
        # Get all cached items for filtering
        all_cached_data = background_cache.get_cached_data(config_name, 'device_groups', page=1, page_size=999999)
        if all_cached_data:
            items = all_cached_data['items']
            
            # Apply legacy filters
            if name:
                items = [g for g in items if name.lower() in g.get('name', '').lower()]
            if parent:
                items = [g for g in items if g.get('parent-dg') and parent.lower() in g.get('parent-dg', '').lower()]
            
            # Apply advanced filters
            filter_params = parse_filter_params(dict(request.query_params))
            if filter_params:
                # Convert dict items to objects for filter compatibility
                from types import SimpleNamespace
                items = [SimpleNamespace(**item) for item in items]
                items = apply_filters(items, filter_params, DEVICE_GROUP_FILTERS)
                # Convert back to dicts
                items = [vars(item) for item in items]
            
            # Now apply pagination after filtering
            total_items = len(items)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_items = items[start_idx:end_idx]
            
            return {
                "items": paginated_items,
                "total_items": total_items,
                "page": page,
                "page_size": page_size,
                "total_pages": (total_items + page_size - 1) // page_size,
                "has_next": end_idx < total_items,
                "has_previous": page > 1,
                "from_cache": True
            }
    
    # Fall back to parser if no cache available
    parser = get_parser(config_name)
    groups = parser.get_device_group_summaries()
    
    # Apply legacy filters for backwards compatibility
    if name:
        groups = [g for g in groups if name.lower() in g.name.lower()]
    if parent:
        groups = [g for g in groups if g.parent_dg and parent.lower() in g.parent_dg.lower()]
    
    # Apply advanced filters
    filter_params = parse_filter_params(dict(request.query_params))
    if filter_params:
        groups = apply_filters(groups, filter_params, DEVICE_GROUP_FILTERS)
    
    # Apply pagination
    pagination = PaginationParams(page=page, page_size=page_size, disable_paging=disable_paging)
    return paginate_results(groups, pagination)

@app.get("/api/v1/configs/{config_name}/device-groups/{group_name}",
         response_model=DeviceGroup,
         tags=["Device Management"],
         summary="Get specific device group",
         description="Retrieve a specific device group by its exact name")
async def get_device_group(
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    group_name: str = Path(..., description="Device group name")
):
    """Get a specific device group by name"""
    parser = get_parser(config_name)
    groups = parser.get_device_groups()
    for group in groups:
        if group.name == group_name:
            return group
    raise HTTPException(status_code=404, detail=f"Device group '{group_name}' not found")

@app.get("/api/v1/configs/{config_name}/device-groups/{group_name}/addresses",
         response_model=PaginatedResponse,
         tags=["Device Management"],
         summary="Get addresses for device group",
         description="Retrieve all address objects defined in a specific device group, with pagination")
async def get_device_group_addresses(
    request: Request,
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    group_name: str = Path(..., description="Device group name"),
    name: Optional[str] = Query(None, description="Filter by address name (partial match)"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(500, ge=1, le=10000, description="Number of items per page"),
    disable_paging: bool = Query(False, description="Return all results without pagination")
):
    """Get addresses for a specific device group with pagination"""
    parser = get_parser(config_name)
    addresses = parser.get_device_group_addresses(group_name)
    
    if not addresses and not parser.get_device_group_summaries():
        raise HTTPException(status_code=404, detail=f"Device group '{group_name}' not found")
    
    # Apply legacy filters
    if name:
        addresses = [a for a in addresses if name.lower() in a.name.lower()]
    
    # Apply advanced filters
    filter_params = parse_filter_params(dict(request.query_params))
    if filter_params:
        addresses = apply_filters(addresses, filter_params, ADDRESS_FILTERS)
    
    # Apply pagination
    pagination = PaginationParams(page=page, page_size=page_size, disable_paging=disable_paging)
    return paginate_results(addresses, pagination)

@app.get("/api/v1/configs/{config_name}/device-groups/{group_name}/address-groups",
         response_model=PaginatedResponse,
         tags=["Device Management"],
         summary="Get address groups for device group",
         description="Retrieve all address groups defined in a specific device group, with pagination")
async def get_device_group_address_groups(
    request: Request,
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    group_name: str = Path(..., description="Device group name"),
    name: Optional[str] = Query(None, description="Filter by group name (partial match)"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(500, ge=1, le=10000, description="Number of items per page"),
    disable_paging: bool = Query(False, description="Return all results without pagination")
):
    """Get address groups for a specific device group with pagination"""
    parser = get_parser(config_name)
    groups = parser.get_device_group_address_groups(group_name)
    
    # Apply legacy filters
    if name:
        groups = [g for g in groups if name.lower() in g.name.lower()]
    
    # Apply advanced filters
    filter_params = parse_filter_params(dict(request.query_params))
    if filter_params:
        groups = apply_filters(groups, filter_params, GROUP_FILTERS)
    
    # Apply pagination
    pagination = PaginationParams(page=page, page_size=page_size, disable_paging=disable_paging)
    return paginate_results(groups, pagination)

@app.get("/api/v1/configs/{config_name}/device-groups/{group_name}/services",
         response_model=PaginatedResponse,
         tags=["Device Management"],
         summary="Get services for device group",
         description="Retrieve all service objects defined in a specific device group, with pagination")
async def get_device_group_services(
    request: Request,
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    group_name: str = Path(..., description="Device group name"),
    name: Optional[str] = Query(None, description="Filter by service name (partial match)"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(500, ge=1, le=10000, description="Number of items per page"),
    disable_paging: bool = Query(False, description="Return all results without pagination")
):
    """Get services for a specific device group with pagination"""
    parser = get_parser(config_name)
    services = parser.get_device_group_services(group_name)
    
    # Apply legacy filters
    if name:
        services = [s for s in services if name.lower() in s.name.lower()]
    
    # Apply advanced filters
    filter_params = parse_filter_params(dict(request.query_params))
    if filter_params:
        services = apply_filters(services, filter_params, SERVICE_FILTERS)
    
    # Apply pagination
    pagination = PaginationParams(page=page, page_size=page_size, disable_paging=disable_paging)
    return paginate_results(services, pagination)

@app.get("/api/v1/configs/{config_name}/device-groups/{group_name}/service-groups",
         response_model=PaginatedResponse,
         tags=["Device Management"],
         summary="Get service groups for device group",
         description="Retrieve all service groups defined in a specific device group, with pagination")
async def get_device_group_service_groups(
    request: Request,
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    group_name: str = Path(..., description="Device group name"),
    name: Optional[str] = Query(None, description="Filter by group name (partial match)"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(500, ge=1, le=10000, description="Number of items per page"),
    disable_paging: bool = Query(False, description="Return all results without pagination")
):
    """Get service groups for a specific device group with pagination"""
    parser = get_parser(config_name)
    groups = parser.get_device_group_service_groups(group_name)
    
    # Apply legacy filters
    if name:
        groups = [g for g in groups if name.lower() in g.name.lower()]
    
    # Apply advanced filters
    filter_params = parse_filter_params(dict(request.query_params))
    if filter_params:
        groups = apply_filters(groups, filter_params, GROUP_FILTERS)
    
    # Apply pagination
    pagination = PaginationParams(page=page, page_size=page_size, disable_paging=disable_paging)
    return paginate_results(groups, pagination)

@app.get("/api/v1/configs/{config_name}/device-groups/{group_name}/rules",
         response_model=PaginatedResponse,
         tags=["Policies"],
         summary="Get security rules for device group",
         description="Retrieve all security rules (pre and post) for a specific device group, with pagination")
async def get_device_group_rules(
    request: Request,
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    group_name: str = Path(..., description="Device group name"),
    rulebase: Optional[str] = Query("all", description="Filter by rulebase type (pre/post/all)"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(500, ge=1, le=10000, description="Number of items per page"),
    disable_paging: bool = Query(False, description="Return all results without pagination")
):
    """Get security rules for a specific device group with pagination"""
    parser = get_parser(config_name)
    rules = parser.get_device_group_security_rules(group_name, rulebase)
    
    if not rules:
        # Check if device group exists
        summaries = parser.get_device_group_summaries()
        if not any(s.name == group_name for s in summaries):
            raise HTTPException(status_code=404, detail=f"Device group '{group_name}' not found")
    
    # Apply advanced filters
    filter_params = parse_filter_params(dict(request.query_params))
    if filter_params:
        rules = apply_filters(rules, filter_params, SECURITY_RULE_FILTERS)
    
    # Apply pagination
    pagination = PaginationParams(page=page, page_size=page_size, disable_paging=disable_paging)
    return paginate_results(rules, pagination)

@app.get("/api/v1/configs/{config_name}/security-policies",
         response_model=PaginatedResponse,
         tags=["Policies"],
         summary="Get all security policies across device groups",
         description="Retrieve all security policies aggregated from all device groups, with pagination and filtering")
async def get_all_security_policies(
    request: Request,
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    name: Optional[str] = Query(None, description="Filter by rule name (partial match)"),
    device_group: Optional[str] = Query(None, description="Filter by device group name"),
    action: Optional[str] = Query(None, description="Filter by action (allow/deny)"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(500, ge=1, le=10000, description="Number of items per page"),
    disable_paging: bool = Query(False, description="Return all results without pagination")
):
    """Get all security policies from all device groups with pagination
    
    Supports comprehensive filtering on all security rule properties:
    
    **Basic filters:**
    - name: Filter by rule name (partial match)
    - device_group: Filter by device group name
    - action: Filter by action (allow/deny)
    
    **Advanced filters using filter[property] syntax:**
    - filter[name]: Name filtering with operators
    - filter[uuid]: UUID filtering
    - filter[source]: Source address filtering (list operations)
    - filter[destination]: Destination address filtering (list operations)
    - filter[source_zone]: Source zone filtering (list operations)
    - filter[destination_zone]: Destination zone filtering (list operations)
    - filter[source_user]: Source user filtering (list operations)
    - filter[category]: URL category filtering (list operations)
    - filter[service]: Service filtering (list operations)
    - filter[application]: Application filtering (list operations)
    - filter[action]: Action filtering (allow/deny/drop/reset-client/reset-server/reset-both)
    - filter[log_start]: Log at session start (true/false)
    - filter[log_end]: Log at session end (true/false)
    - filter[disabled]: Rule disabled status (true/false)
    - filter[description]: Description filtering
    - filter[tag]: Tag filtering (list operations)
    - filter[log_setting]: Log forwarding profile filtering
    - filter[xpath]: XPath location filtering
    - filter[parent_device_group]: Parent device group filtering
    
    **Supported operators:**
    - [eq], [ne]: Exact match / not equals
    - [contains], [not_contains]: Contains / does not contain
    - [starts_with], [ends_with]: String prefix/suffix matching
    - [in], [not_in]: List membership operations
    
    **Examples:**
    - filter[source][contains]=10.0.0.0
    - filter[destination_zone][in]=untrust
    - filter[application][not_in]=ssl,web-browsing
    - filter[action][eq]=deny
    - filter[disabled][eq]=false
    """
    parser = get_parser(config_name)
    
    # Get all device groups
    device_groups = parser.get_device_group_summaries()
    
    all_rules = []
    
    # Fetch security rules from each device group
    for dg in device_groups:
        rules = parser.get_device_group_security_rules(dg.name, "all")
        for index, rule in enumerate(rules):
            # Add metadata to each rule
            rule.device_group = dg.name
            rule.rule_type = 'Device Group' if rule.parent_device_group else 'Shared'
            rule.order = index + 1
            rule.rulebase_location = f"{dg.name} #{index + 1}"
            all_rules.append(rule)
    
    # Apply legacy filters for backwards compatibility
    if name:
        all_rules = [r for r in all_rules if name.lower() in r.name.lower()]
    if device_group:
        all_rules = [r for r in all_rules if device_group.lower() in r.device_group.lower()]
    if action:
        all_rules = [r for r in all_rules if r.action and action.lower() == r.action.lower()]
    
    # Apply advanced filters
    filter_params = parse_filter_params(dict(request.query_params))
    if filter_params:
        all_rules = apply_filters(all_rules, filter_params, SECURITY_RULE_FILTERS)
    
    # Apply pagination
    pagination = PaginationParams(page=page, page_size=page_size, disable_paging=disable_paging)
    return paginate_results(all_rules, pagination)

@app.get("/api/v1/configs/{config_name}/templates",
         response_model=PaginatedResponse,
         tags=["Device Management"],
         summary="Get all templates",
         description="Retrieve all device templates, with pagination")
async def get_templates(
    request: Request,
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    name: Optional[str] = Query(None, description="Filter by template name (partial match)"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(500, ge=1, le=10000, description="Number of items per page"),
    disable_paging: bool = Query(False, description="Return all results without pagination")
):
    """Get all templates with optional filtering and pagination"""
    parser = get_parser(config_name)
    templates = parser.get_templates()
    
    if name:
        templates = [t for t in templates if name.lower() in t.name.lower()]
    
    # Apply advanced filters
    filter_params = parse_filter_params(dict(request.query_params))
    if filter_params:
        templates = apply_filters(templates, filter_params, TEMPLATE_FILTERS)
    
    # Apply pagination
    pagination = PaginationParams(page=page, page_size=page_size, disable_paging=disable_paging)
    return paginate_results(templates, pagination)

@app.get("/api/v1/configs/{config_name}/templates/{template_name}",
         response_model=Template,
         tags=["Device Management"],
         summary="Get specific template",
         description="Retrieve a specific template by its exact name")
async def get_template(
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    template_name: str = Path(..., description="Template name")
):
    """Get a specific template by name"""
    parser = get_parser(config_name)
    templates = parser.get_templates()
    for template in templates:
        if template.name == template_name:
            return template
    raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found")

@app.get("/api/v1/configs/{config_name}/template-stacks",
         response_model=PaginatedResponse,
         tags=["Device Management"],
         summary="Get all template stacks",
         description="Retrieve all template stacks with their member templates, with pagination")
async def get_template_stacks(
    request: Request,
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    name: Optional[str] = Query(None, description="Filter by stack name (partial match)"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(500, ge=1, le=10000, description="Number of items per page"),
    disable_paging: bool = Query(False, description="Return all results without pagination")
):
    """Get all template stacks with optional filtering and pagination"""
    parser = get_parser(config_name)
    stacks = parser.get_template_stacks()
    
    if name:
        stacks = [s for s in stacks if name.lower() in s.name.lower()]
    
    # Apply advanced filters
    filter_params = parse_filter_params(dict(request.query_params))
    if filter_params:
        stacks = apply_filters(stacks, filter_params, TEMPLATE_STACK_FILTERS)
    
    # Apply pagination
    pagination = PaginationParams(page=page, page_size=page_size, disable_paging=disable_paging)
    return paginate_results(stacks, pagination)

@app.get("/api/v1/configs/{config_name}/template-stacks/{stack_name}",
         response_model=TemplateStack,
         tags=["Device Management"],
         summary="Get specific template stack",
         description="Retrieve a specific template stack by its exact name")
async def get_template_stack(
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    stack_name: str = Path(..., description="Template stack name")
):
    """Get a specific template stack by name"""
    parser = get_parser(config_name)
    stacks = parser.get_template_stacks()
    for stack in stacks:
        if stack.name == stack_name:
            return stack
    raise HTTPException(status_code=404, detail=f"Template stack '{stack_name}' not found")

# Logging Endpoints
@app.get("/api/v1/configs/{config_name}/log-profiles",
         response_model=PaginatedResponse,
         tags=["Logging"],
         summary="Get all log forwarding profiles",
         description="Retrieve all log forwarding profiles, with pagination")
async def get_log_profiles(
    request: Request,
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    name: Optional[str] = Query(None, description="Filter by profile name (partial match)"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(500, ge=1, le=10000, description="Number of items per page"),
    disable_paging: bool = Query(False, description="Return all results without pagination")
):
    """Get all log forwarding profiles with pagination"""
    parser = get_parser(config_name)
    profiles = parser.get_log_profiles()
    
    if name:
        profiles = [p for p in profiles if name.lower() in p.name.lower()]
    
    # Apply advanced filters
    filter_params = parse_filter_params(dict(request.query_params))
    if filter_params:
        profiles = apply_filters(profiles, filter_params, LOG_PROFILE_FILTERS)
    
    # Apply pagination
    pagination = PaginationParams(page=page, page_size=page_size, disable_paging=disable_paging)
    return paginate_results(profiles, pagination)

@app.get("/api/v1/configs/{config_name}/schedules",
         response_model=PaginatedResponse,
         tags=["Logging"],
         summary="Get all schedules",
         description="Retrieve all time-based schedules, with pagination")
async def get_schedules(
    request: Request,
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    name: Optional[str] = Query(None, description="Filter by schedule name (partial match)"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(500, ge=1, le=10000, description="Number of items per page"),
    disable_paging: bool = Query(False, description="Return all results without pagination")
):
    """Get all schedules with pagination"""
    parser = get_parser(config_name)
    schedules = parser.get_schedules()
    
    if name:
        schedules = [s for s in schedules if name.lower() in s.name.lower()]
    
    # Apply advanced filters
    filter_params = parse_filter_params(dict(request.query_params))
    if filter_params:
        schedules = apply_filters(schedules, filter_params, SCHEDULE_FILTERS)
    
    # Apply pagination
    pagination = PaginationParams(page=page, page_size=page_size, disable_paging=disable_paging)
    return paginate_results(schedules, pagination)

# Object search endpoints
@app.get("/api/v1/configs/{config_name}/search/by-xpath",
         tags=["Search"],
         summary="Search objects by XPath",
         description="Search for any configuration object by its XPath")
async def search_by_xpath(
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    xpath: str = Query(..., description="XPath to search for")
):
    """Search for objects by XPath"""
    parser = get_parser(config_name)
    
    # Search across all object types
    results = []
    
    # Search addresses
    for addr in parser.get_all_addresses():
        if addr.xpath == xpath:
            results.append({"type": "address", "object": addr})
    
    # Search address groups
    for group in parser.get_shared_address_groups():
        if group.xpath == xpath:
            results.append({"type": "address-group", "object": group})
    
    # Search services
    for service in parser.get_shared_services():
        if service.xpath == xpath:
            results.append({"type": "service", "object": service})
    
    # Search device groups
    for dg in parser.get_device_groups():
        if dg.xpath == xpath:
            results.append({"type": "device-group", "object": dg})
    
    if not results:
        raise HTTPException(status_code=404, detail=f"No object found at XPath: {xpath}")
    
    return results

# Cache status endpoint
@app.get("/api/v1/configs/{config_name}/cache-status",
         tags=["System"],
         summary="Get cache status",
         description="Get the caching status for a specific configuration")
async def get_cache_status(
    config_name: str = Path(..., description="Configuration name (without .xml extension)")
):
    """Get cache status for a configuration"""
    # Ensure parser exists (will trigger caching if not already started)
    _ = get_parser(config_name)
    
    return background_cache.get_cache_status(config_name)

# Health check endpoint
@app.get("/api/v1/health",
         tags=["System"],
         summary="Health check",
         description="Check if the API is running and XML files are accessible")
async def health_check():
    """Check API health status"""
    return {
        "status": "healthy",
        "config_path": CONFIG_FILES_PATH,
        "configs_available": len(available_configs),
        "configs_ready": len(ready_configs),
        "configs_loading": len(loading_configs),
        "available_configs": available_configs
    }

# Mount static files for the React app (after all API routes are defined)
if os.path.exists("static/dist"):
    app.mount("/assets", StaticFiles(directory="static/dist/assets"), name="react-assets")
    
    # Catch-all route for React app (must be defined AFTER all API routes)
    @app.get("/{path:path}", include_in_schema=False)
    async def serve_react_app(path: str):
        """Serve React app for all non-API routes"""
        # Return the index.html for client-side routing
        if os.path.exists("static/dist/index.html"):
            return FileResponse("static/dist/index.html")
        raise HTTPException(status_code=404)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)