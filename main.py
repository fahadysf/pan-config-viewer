from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.responses import RedirectResponse
from typing import List, Optional, Dict
import os
import glob
from parser import PanoramaXMLParser
from models import (
    AddressObject, AddressGroup, ServiceObject, ServiceGroup,
    VulnerabilityProfile, AntivirusProfile, SpywareProfile,
    URLFilteringProfile, FileBlockingProfile, WildFireAnalysisProfile,
    DataFilteringProfile, SecurityProfileGroup, SecurityRule, NATRule,
    DeviceGroup, DeviceGroupSummary, Template, TemplateStack, LogSetting, Schedule,
    ZoneProtectionProfile
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
    
    ## Usage
    
    All endpoints support filtering by name using the `name` query parameter.
    Some endpoints support tag-based filtering using the `tag` parameter.
    
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
CONFIG_FILES_PATH = os.environ.get("CONFIG_FILES_PATH", "/config-files")
parsers: Dict[str, PanoramaXMLParser] = {}
available_configs: List[str] = []

@app.on_event("startup")
async def startup_event():
    """Scan for XML files on startup"""
    global available_configs
    
    if not os.path.exists(CONFIG_FILES_PATH):
        os.makedirs(CONFIG_FILES_PATH, exist_ok=True)
    
    # Find all XML files in the config directory
    xml_files = glob.glob(os.path.join(CONFIG_FILES_PATH, "*.xml"))
    
    if not xml_files:
        print(f"Warning: No XML files found in {CONFIG_FILES_PATH}")
    
    # Store available config names (without path and extension)
    available_configs = [os.path.splitext(os.path.basename(f))[0] for f in xml_files]
    print(f"Found {len(available_configs)} configuration files: {available_configs}")

def get_parser(config_name: str) -> PanoramaXMLParser:
    """Get or create parser for a specific config file"""
    if config_name not in parsers:
        # Check if the config exists
        if config_name not in available_configs:
            raise HTTPException(
                status_code=404, 
                detail=f"Configuration '{config_name}' not found. Available configs: {available_configs}"
            )
        
        # Create parser for this config
        xml_path = os.path.join(CONFIG_FILES_PATH, f"{config_name}.xml")
        try:
            parsers[config_name] = PanoramaXMLParser(xml_path)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse configuration '{config_name}': {str(e)}"
            )
    
    return parsers[config_name]

@app.get("/", include_in_schema=False)
async def root():
    """Redirect to API documentation"""
    return RedirectResponse(url="/docs")

# Configuration Management Endpoints
@app.get("/api/v1/configs",
         tags=["Configuration"],
         summary="List available configurations",
         description="Get a list of all available XML configuration files")
async def list_configs():
    """List all available configuration files"""
    return {
        "configs": available_configs,
        "count": len(available_configs),
        "path": CONFIG_FILES_PATH
    }

@app.get("/api/v1/configs/{config_name}/info",
         tags=["Configuration"],
         summary="Get configuration info",
         description="Get information about a specific configuration file")
async def get_config_info(
    config_name: str = Path(..., description="Configuration name (without .xml extension)")
):
    """Get information about a specific configuration"""
    parser = get_parser(config_name)
    xml_path = os.path.join(CONFIG_FILES_PATH, f"{config_name}.xml")
    
    return {
        "name": config_name,
        "path": xml_path,
        "size": os.path.getsize(xml_path),
        "modified": os.path.getmtime(xml_path),
        "loaded": config_name in parsers
    }

# Address Objects Endpoints
@app.get("/api/v1/configs/{config_name}/addresses", 
         response_model=List[AddressObject],
         tags=["Address Objects"],
         summary="Get all address objects",
         description="Retrieve all shared address objects from the configuration. Supports filtering by name and tags.")
async def get_addresses(
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    name: Optional[str] = Query(None, description="Filter by address name (partial match)"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    location: Optional[str] = Query("all", description="Filter by location (all/shared/device-group/template/vsys)")
):
    """Get address objects with optional filtering"""
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
    
    # Apply filters
    if name:
        addresses = [a for a in addresses if name.lower() in a.name.lower()]
    if tag:
        addresses = [a for a in addresses if a.tag and tag in a.tag]
    
    return addresses

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
         response_model=List[AddressGroup],
         tags=["Address Objects"],
         summary="Get all address groups",
         description="Retrieve all shared address groups including static and dynamic groups")
async def get_address_groups(
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    name: Optional[str] = Query(None, description="Filter by group name (partial match)"),
    tag: Optional[str] = Query(None, description="Filter by tag")
):
    """Get all shared address groups with optional filtering"""
    parser = get_parser(config_name)
    groups = parser.get_shared_address_groups()
    
    # Apply filters
    if name:
        groups = [g for g in groups if name.lower() in g.name.lower()]
    if tag:
        groups = [g for g in groups if g.tag and tag in g.tag]
    
    return groups

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
         response_model=List[ServiceObject],
         tags=["Service Objects"],
         summary="Get all service objects",
         description="Retrieve all shared service objects with protocol definitions")
async def get_services(
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    name: Optional[str] = Query(None, description="Filter by service name (partial match)"),
    protocol: Optional[str] = Query(None, description="Filter by protocol (tcp/udp)")
):
    """Get all shared service objects with optional filtering"""
    parser = get_parser(config_name)
    services = parser.get_shared_services()
    
    # Apply filters
    if name:
        services = [s for s in services if name.lower() in s.name.lower()]
    if protocol and protocol.lower() in ["tcp", "udp"]:
        services = [s for s in services if hasattr(s.protocol, protocol.lower()) and getattr(s.protocol, protocol.lower())]
    
    return services

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
         response_model=List[ServiceGroup],
         tags=["Service Objects"],
         summary="Get all service groups",
         description="Retrieve all shared service groups")
async def get_service_groups(
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    name: Optional[str] = Query(None, description="Filter by group name (partial match)")
):
    """Get all shared service groups with optional filtering"""
    parser = get_parser(config_name)
    groups = parser.get_shared_service_groups()
    
    # Apply filters
    if name:
        groups = [g for g in groups if name.lower() in g.name.lower()]
    
    return groups

# Security Profiles Endpoints
@app.get("/api/v1/configs/{config_name}/security-profiles/vulnerability",
         response_model=List[VulnerabilityProfile],
         tags=["Security Profiles"],
         summary="Get vulnerability protection profiles",
         description="Retrieve all vulnerability protection profiles with their rules")
async def get_vulnerability_profiles(
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    name: Optional[str] = Query(None, description="Filter by profile name (partial match)")
):
    """Get all vulnerability protection profiles"""
    parser = get_parser(config_name)
    profiles = parser.get_vulnerability_profiles()
    
    if name:
        profiles = [p for p in profiles if name.lower() in p.name.lower()]
    
    return profiles

@app.get("/api/v1/configs/{config_name}/security-profiles/url-filtering",
         response_model=List[URLFilteringProfile],
         tags=["Security Profiles"],
         summary="Get URL filtering profiles",
         description="Retrieve all URL filtering profiles with category actions")
async def get_url_filtering_profiles(
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    name: Optional[str] = Query(None, description="Filter by profile name (partial match)")
):
    """Get all URL filtering profiles"""
    parser = get_parser(config_name)
    profiles = parser.get_url_filtering_profiles()
    
    if name:
        profiles = [p for p in profiles if name.lower() in p.name.lower()]
    
    return profiles

# Device Management Endpoints
@app.get("/api/v1/configs/{config_name}/device-groups",
         response_model=List[DeviceGroupSummary],
         tags=["Device Management"],
         summary="Get all device groups summary",
         description="Retrieve all device groups with counts of their child objects")
async def get_device_groups(
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    name: Optional[str] = Query(None, description="Filter by device group name (partial match)"),
    parent: Optional[str] = Query(None, description="Filter by parent device group")
):
    """Get all device groups with counts of child objects"""
    parser = get_parser(config_name)
    groups = parser.get_device_group_summaries()
    
    # Apply filters
    if name:
        groups = [g for g in groups if name.lower() in g.name.lower()]
    if parent:
        groups = [g for g in groups if g.parent_dg and parent.lower() in g.parent_dg.lower()]
    
    return groups

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
         response_model=List[AddressObject],
         tags=["Device Management"],
         summary="Get addresses for device group",
         description="Retrieve all address objects defined in a specific device group")
async def get_device_group_addresses(
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    group_name: str = Path(..., description="Device group name"),
    name: Optional[str] = Query(None, description="Filter by address name (partial match)")
):
    """Get addresses for a specific device group"""
    parser = get_parser(config_name)
    addresses = parser.get_device_group_addresses(group_name)
    
    if not addresses and not parser.get_device_group_summaries():
        raise HTTPException(status_code=404, detail=f"Device group '{group_name}' not found")
    
    # Apply filters
    if name:
        addresses = [a for a in addresses if name.lower() in a.name.lower()]
    
    return addresses

@app.get("/api/v1/configs/{config_name}/device-groups/{group_name}/address-groups",
         response_model=List[AddressGroup],
         tags=["Device Management"],
         summary="Get address groups for device group",
         description="Retrieve all address groups defined in a specific device group")
async def get_device_group_address_groups(
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    group_name: str = Path(..., description="Device group name"),
    name: Optional[str] = Query(None, description="Filter by group name (partial match)")
):
    """Get address groups for a specific device group"""
    parser = get_parser(config_name)
    groups = parser.get_device_group_address_groups(group_name)
    
    # Apply filters
    if name:
        groups = [g for g in groups if name.lower() in g.name.lower()]
    
    return groups

@app.get("/api/v1/configs/{config_name}/device-groups/{group_name}/services",
         response_model=List[ServiceObject],
         tags=["Device Management"],
         summary="Get services for device group",
         description="Retrieve all service objects defined in a specific device group")
async def get_device_group_services(
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    group_name: str = Path(..., description="Device group name"),
    name: Optional[str] = Query(None, description="Filter by service name (partial match)")
):
    """Get services for a specific device group"""
    parser = get_parser(config_name)
    services = parser.get_device_group_services(group_name)
    
    # Apply filters
    if name:
        services = [s for s in services if name.lower() in s.name.lower()]
    
    return services

@app.get("/api/v1/configs/{config_name}/device-groups/{group_name}/service-groups",
         response_model=List[ServiceGroup],
         tags=["Device Management"],
         summary="Get service groups for device group",
         description="Retrieve all service groups defined in a specific device group")
async def get_device_group_service_groups(
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    group_name: str = Path(..., description="Device group name"),
    name: Optional[str] = Query(None, description="Filter by group name (partial match)")
):
    """Get service groups for a specific device group"""
    parser = get_parser(config_name)
    groups = parser.get_device_group_service_groups(group_name)
    
    # Apply filters
    if name:
        groups = [g for g in groups if name.lower() in g.name.lower()]
    
    return groups

@app.get("/api/v1/configs/{config_name}/device-groups/{group_name}/rules",
         response_model=List[SecurityRule],
         tags=["Policies"],
         summary="Get security rules for device group",
         description="Retrieve all security rules (pre and post) for a specific device group")
async def get_device_group_rules(
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    group_name: str = Path(..., description="Device group name"),
    rulebase: Optional[str] = Query("all", description="Filter by rulebase type (pre/post/all)")
):
    """Get security rules for a specific device group"""
    parser = get_parser(config_name)
    rules = parser.get_device_group_security_rules(group_name, rulebase)
    
    if not rules:
        # Check if device group exists
        summaries = parser.get_device_group_summaries()
        if not any(s.name == group_name for s in summaries):
            raise HTTPException(status_code=404, detail=f"Device group '{group_name}' not found")
    
    return rules

@app.get("/api/v1/configs/{config_name}/templates",
         response_model=List[Template],
         tags=["Device Management"],
         summary="Get all templates",
         description="Retrieve all device templates")
async def get_templates(
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    name: Optional[str] = Query(None, description="Filter by template name (partial match)")
):
    """Get all templates with optional filtering"""
    parser = get_parser(config_name)
    templates = parser.get_templates()
    
    if name:
        templates = [t for t in templates if name.lower() in t.name.lower()]
    
    return templates

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
         response_model=List[TemplateStack],
         tags=["Device Management"],
         summary="Get all template stacks",
         description="Retrieve all template stacks with their member templates")
async def get_template_stacks(
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    name: Optional[str] = Query(None, description="Filter by stack name (partial match)")
):
    """Get all template stacks with optional filtering"""
    parser = get_parser(config_name)
    stacks = parser.get_template_stacks()
    
    if name:
        stacks = [s for s in stacks if name.lower() in s.name.lower()]
    
    return stacks

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
         response_model=List[LogSetting],
         tags=["Logging"],
         summary="Get all log forwarding profiles",
         description="Retrieve all log forwarding profiles")
async def get_log_profiles(
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    name: Optional[str] = Query(None, description="Filter by profile name (partial match)")
):
    """Get all log forwarding profiles"""
    parser = get_parser(config_name)
    profiles = parser.get_log_profiles()
    
    if name:
        profiles = [p for p in profiles if name.lower() in p.name.lower()]
    
    return profiles

@app.get("/api/v1/configs/{config_name}/schedules",
         response_model=List[Schedule],
         tags=["Logging"],
         summary="Get all schedules",
         description="Retrieve all time-based schedules")
async def get_schedules(
    config_name: str = Path(..., description="Configuration name (without .xml extension)"),
    name: Optional[str] = Query(None, description="Filter by schedule name (partial match)")
):
    """Get all schedules"""
    parser = get_parser(config_name)
    schedules = parser.get_schedules()
    
    if name:
        schedules = [s for s in schedules if name.lower() in s.name.lower()]
    
    return schedules

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
        "configs_loaded": len(parsers),
        "available_configs": available_configs
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)