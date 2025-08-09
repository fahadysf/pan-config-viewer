from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, model_validator
from enum import Enum


class ConfigLocation(BaseModel):
    """Base class for configuration location tracking"""
    xpath: Optional[str] = Field(None, description="XPath location in the XML")
    parent_device_group: Optional[str] = Field(None, alias="parent-device-group", description="Parent device group if applicable")
    parent_template: Optional[str] = Field(None, alias="parent-template", description="Parent template if applicable")
    parent_vsys: Optional[str] = Field(None, alias="parent-vsys", description="Parent virtual system if applicable")
    
    class Config:
        populate_by_name = True
        by_alias = True  # Use aliases (hyphens) in JSON serialization


class ProtocolType(str, Enum):
    TCP = "tcp"
    UDP = "udp"


class Action(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    DROP = "drop"
    DEFAULT = "default"
    RESET_CLIENT = "reset-client"
    RESET_SERVER = "reset-server"
    RESET_BOTH = "reset-both"


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class ZoneProtectionProfileType(str, Enum):
    FLOOD = "flood"
    RECONNAISSANCE = "reconnaissance"


class AddressType(str, Enum):
    FQDN = "fqdn"
    IP_NETMASK = "ip-netmask"
    IP_RANGE = "ip-range"


class Protocol(BaseModel):
    tcp: Optional[Dict[str, Any]] = Field(None, description="TCP protocol configuration")
    udp: Optional[Dict[str, Any]] = Field(None, description="UDP protocol configuration")


class ServiceObject(ConfigLocation):
    name: str = Field(..., description="Service object name")
    protocol: Protocol = Field(..., description="Protocol configuration")
    description: Optional[str] = Field(None, description="Service description")
    tag: Optional[List[str]] = Field(None, description="Tags associated with the service")


class ServiceGroup(ConfigLocation):
    name: str = Field(..., description="Service group name")
    members: List[str] = Field(..., description="Member services")
    description: Optional[str] = Field(None, description="Service group description")
    tag: Optional[List[str]] = Field(None, description="Tags associated with the service group")


class AddressObject(ConfigLocation):
    name: str = Field(..., description="Address object name")
    type: Optional[AddressType] = Field(None, description="Address type")
    ip_netmask: Optional[str] = Field(None, alias="ip-netmask", description="IP address with netmask")
    ip_range: Optional[str] = Field(None, alias="ip-range", description="IP address range")
    fqdn: Optional[str] = Field(None, description="Fully qualified domain name")
    description: Optional[str] = Field(None, description="Address description")
    tag: Optional[List[str]] = Field(None, description="Tags associated with the address")
    
    @model_validator(mode='after')
    def validate_address_type(self):
        """Determine the address type based on which field has a value"""
        # Check which field has an actual value (not None and not empty string)
        has_ip_netmask = self.ip_netmask is not None and self.ip_netmask.strip() != ""
        has_ip_range = self.ip_range is not None and self.ip_range.strip() != ""
        has_fqdn = self.fqdn is not None and self.fqdn.strip() != ""
        
        # Determine the type based on which field is populated
        if has_ip_netmask:
            self.type = AddressType.IP_NETMASK
            # Set other fields to None for cleanliness
            if not has_ip_range:
                self.ip_range = None
            if not has_fqdn:
                self.fqdn = None
        elif has_ip_range:
            self.type = AddressType.IP_RANGE
            # Set other fields to None for cleanliness
            if not has_ip_netmask:
                self.ip_netmask = None
            if not has_fqdn:
                self.fqdn = None
        elif has_fqdn:
            self.type = AddressType.FQDN
            # Set other fields to None for cleanliness
            if not has_ip_netmask:
                self.ip_netmask = None
            if not has_ip_range:
                self.ip_range = None
        else:
            # If type is explicitly specified but no corresponding value, 
            # keep it as is but clean up unused fields
            if self.type == AddressType.IP_NETMASK:
                self.ip_range = None
                self.fqdn = None
            elif self.type == AddressType.IP_RANGE:
                self.ip_netmask = None
                self.fqdn = None
            elif self.type == AddressType.FQDN:
                self.ip_netmask = None
                self.ip_range = None
        
        return self


class AddressGroup(ConfigLocation):
    name: str = Field(..., description="Address group name")
    static: Optional[List[str]] = Field(None, description="Static member addresses")
    dynamic: Optional[Dict[str, Any]] = Field(None, description="Dynamic address group configuration")
    description: Optional[str] = Field(None, description="Address group description")
    tag: Optional[List[str]] = Field(None, description="Tags associated with the address group")


class VulnerabilityRule(ConfigLocation):
    name: str = Field(..., description="Rule name")
    action: Action = Field(..., description="Action to take")
    vendor_id: List[str] = Field(..., alias="vendor-id", description="Vendor IDs")
    severity: List[Severity] = Field(..., description="Severity levels")
    cve: List[str] = Field(..., description="CVE identifiers")
    threat_name: str = Field(..., alias="threat-name", description="Threat name")
    host: str = Field(..., description="Host type (client/server/any)")
    category: str = Field(..., description="Category")
    packet_capture: Optional[str] = Field(None, alias="packet-capture", description="Packet capture setting")


class VulnerabilityProfile(ConfigLocation):
    name: str = Field(..., description="Vulnerability profile name")
    rules: List[VulnerabilityRule] = Field(..., description="Vulnerability rules")
    description: Optional[str] = Field(None, description="Profile description")


class AntivirusRule(ConfigLocation):
    name: str = Field(..., description="Rule name")
    action: str = Field(..., description="Action to take")
    wildfire_action: Optional[str] = Field(None, alias="wildfire-action", description="WildFire action")
    application: List[str] = Field(..., description="Applications")
    direction: str = Field(..., description="Traffic direction")


class AntivirusProfile(ConfigLocation):
    name: str = Field(..., description="Antivirus profile name")
    decoder: Optional[List[AntivirusRule]] = Field(None, description="Decoder rules")
    description: Optional[str] = Field(None, description="Profile description")
    packet_capture: Optional[bool] = Field(None, alias="packet-capture", description="Enable packet capture")


class SpywareThreat(ConfigLocation):
    name: str = Field(..., description="Threat name")
    action: Action = Field(..., description="Action to take")
    severity: List[Severity] = Field(..., description="Severity levels")
    category: str = Field(..., description="Category")
    packet_capture: Optional[str] = Field(None, alias="packet-capture", description="Packet capture setting")


class SpywareProfile(ConfigLocation):
    name: str = Field(..., description="Anti-spyware profile name")
    rules: List[SpywareThreat] = Field(..., description="Spyware rules")
    sinkhole: Optional[Dict[str, Any]] = Field(None, description="DNS sinkhole configuration")
    description: Optional[str] = Field(None, description="Profile description")


class URLCategory(ConfigLocation):
    name: str = Field(..., description="URL category name")
    action: str = Field(..., description="Action to take")
    log_http_hdr_xff: Optional[bool] = Field(None, alias="log-http-hdr-xff", description="Log X-Forwarded-For header")
    log_http_hdr_user_agent: Optional[bool] = Field(None, alias="log-http-hdr-user-agent", description="Log User-Agent header")
    log_http_hdr_referer: Optional[bool] = Field(None, alias="log-http-hdr-referer", description="Log Referer header")


class URLFilteringProfile(ConfigLocation):
    name: str = Field(..., description="URL filtering profile name")
    action: Optional[str] = Field(None, description="Default action")
    block: Optional[List[URLCategory]] = Field(None, description="Blocked categories")
    alert: Optional[List[URLCategory]] = Field(None, description="Alert categories")
    allow: Optional[List[URLCategory]] = Field(None, description="Allowed categories")
    continue_: Optional[List[URLCategory]] = Field(None, alias="continue", description="Continue categories")
    override: Optional[List[URLCategory]] = Field(None, description="Override categories")
    description: Optional[str] = Field(None, description="Profile description")
    log_http_hdr_xff: Optional[bool] = Field(None, alias="log-http-hdr-xff", description="Log X-Forwarded-For header")
    log_http_hdr_user_agent: Optional[bool] = Field(None, alias="log-http-hdr-user-agent", description="Log User-Agent header")
    log_http_hdr_referer: Optional[bool] = Field(None, alias="log-http-hdr-referer", description="Log Referer header")


class FileBlockingRule(ConfigLocation):
    name: str = Field(..., description="Rule name")
    applications: List[str] = Field(..., description="Applications")
    file_types: List[str] = Field(..., alias="file-types", description="File types to block")
    direction: str = Field(..., description="Direction")
    action: str = Field(..., description="Action to take")


class FileBlockingProfile(ConfigLocation):
    name: str = Field(..., description="File blocking profile name")
    rules: List[FileBlockingRule] = Field(..., description="File blocking rules")
    description: Optional[str] = Field(None, description="Profile description")


class WildFireAnalysisProfile(ConfigLocation):
    name: str = Field(..., description="WildFire analysis profile name")
    rules: Optional[List[Dict[str, Any]]] = Field(None, description="Analysis rules")
    description: Optional[str] = Field(None, description="Profile description")


class DataPattern(ConfigLocation):
    name: str = Field(..., description="Data pattern name")
    pattern: str = Field(..., description="Pattern to match")
    file_types: Optional[List[str]] = Field(None, alias="file-types", description="File types")
    description: Optional[str] = Field(None, description="Pattern description")


class DataFilteringProfile(ConfigLocation):
    name: str = Field(..., description="Data filtering profile name")
    data_capture: Optional[bool] = Field(None, alias="data-capture", description="Enable data capture")
    rules: Optional[List[Dict[str, Any]]] = Field(None, description="Data filtering rules")
    description: Optional[str] = Field(None, description="Profile description")


class SecurityProfileGroup(ConfigLocation):
    name: str = Field(..., description="Security profile group name")
    virus: Optional[str] = Field(None, description="Antivirus profile")
    spyware: Optional[str] = Field(None, description="Anti-spyware profile")
    vulnerability: Optional[str] = Field(None, description="Vulnerability protection profile")
    url_filtering: Optional[str] = Field(None, alias="url-filtering", description="URL filtering profile")
    file_blocking: Optional[str] = Field(None, alias="file-blocking", description="File blocking profile")
    data_filtering: Optional[str] = Field(None, alias="data-filtering", description="Data filtering profile")
    wildfire_analysis: Optional[str] = Field(None, alias="wildfire-analysis", description="WildFire analysis profile")
    description: Optional[str] = Field(None, description="Group description")


class LogSetting(ConfigLocation):
    name: str = Field(..., description="Log setting name")
    match_list: Optional[List[Dict[str, Any]]] = Field(None, alias="match-list", description="Match list configuration")
    description: Optional[str] = Field(None, description="Log setting description")


class Schedule(ConfigLocation):
    name: str = Field(..., description="Schedule name")
    schedule_type: Dict[str, Any] = Field(..., alias="schedule-type", description="Schedule type configuration")
    description: Optional[str] = Field(None, description="Schedule description")


class ZoneProtectionProfile(ConfigLocation):
    name: str = Field(..., description="Zone protection profile name")
    flood: Optional[Dict[str, Any]] = Field(None, description="Flood protection settings")
    reconnaissance: Optional[Dict[str, Any]] = Field(None, description="Reconnaissance protection settings")
    packet_based_attack_protection: Optional[Dict[str, Any]] = Field(None, alias="packet-based-attack-protection", description="Packet-based attack protection")
    description: Optional[str] = Field(None, description="Profile description")


class SecurityRule(ConfigLocation):
    name: str = Field(..., description="Security rule name")
    uuid: Optional[str] = Field(None, description="Rule UUID")
    from_: List[str] = Field(..., alias="from", description="Source zones")
    to: List[str] = Field(..., description="Destination zones")
    source: List[str] = Field(..., description="Source addresses")
    destination: List[str] = Field(..., description="Destination addresses")
    source_user: Optional[List[str]] = Field(None, alias="source-user", description="Source users")
    category: Optional[List[str]] = Field(None, description="URL categories")
    application: List[str] = Field(..., description="Applications")
    service: List[str] = Field(..., description="Services")
    action: Action = Field(..., description="Action to take")
    profile_setting: Optional[Dict[str, Any]] = Field(None, alias="profile-setting", description="Security profile settings")
    log_setting: Optional[str] = Field(None, alias="log-setting", description="Log forwarding profile")
    log_start: Optional[bool] = Field(None, alias="log-start", description="Log at session start")
    log_end: Optional[bool] = Field(None, alias="log-end", description="Log at session end")
    disabled: Optional[bool] = Field(False, description="Rule disabled")
    description: Optional[str] = Field(None, description="Rule description")
    tag: Optional[List[str]] = Field(None, description="Tags")
    # Runtime metadata fields (populated dynamically)
    device_group: Optional[str] = Field(None, description="Device group name (runtime)")
    rule_type: Optional[str] = Field(None, description="Rule type (runtime)")
    order: Optional[int] = Field(None, description="Rule order (runtime)")
    rulebase_location: Optional[str] = Field(None, description="Rule location (runtime)")


class NATRule(ConfigLocation):
    name: str = Field(..., description="NAT rule name")
    uuid: Optional[str] = Field(None, description="Rule UUID")
    from_: List[str] = Field(..., alias="from", description="Source zones")
    to: List[str] = Field(..., description="Destination zones")
    source: List[str] = Field(..., description="Source addresses")
    destination: List[str] = Field(..., description="Destination addresses")
    service: str = Field(..., description="Service")
    source_translation: Optional[Dict[str, Any]] = Field(None, alias="source-translation", description="Source NAT configuration")
    destination_translation: Optional[Dict[str, Any]] = Field(None, alias="destination-translation", description="Destination NAT configuration")
    disabled: Optional[bool] = Field(False, description="Rule disabled")
    description: Optional[str] = Field(None, description="Rule description")
    tag: Optional[List[str]] = Field(None, description="Tags")
    # Runtime metadata fields (populated dynamically)
    device_group: Optional[str] = Field(None, description="Device group name (runtime)")
    rule_type: Optional[str] = Field(None, description="Rule type (runtime)")
    order: Optional[int] = Field(None, description="Rule order (runtime)")
    rulebase_location: Optional[str] = Field(None, description="Rule location (runtime)")


class DeviceGroup(ConfigLocation):
    name: str = Field(..., description="Device group name")
    description: Optional[str] = Field(None, description="Device group description")
    devices: Optional[List[Dict[str, str]]] = Field(None, description="Devices in the group")
    address: Optional[List[AddressObject]] = Field(None, description="Address objects")
    address_group: Optional[List[AddressGroup]] = Field(None, alias="address-group", description="Address groups")
    service: Optional[List[ServiceObject]] = Field(None, description="Service objects")
    service_group: Optional[List[ServiceGroup]] = Field(None, alias="service-group", description="Service groups")
    pre_rules: Optional[Dict[str, List[SecurityRule]]] = Field(None, alias="pre-rulebase", description="Pre-rules")
    post_rules: Optional[Dict[str, List[SecurityRule]]] = Field(None, alias="post-rulebase", description="Post-rules")
    profiles: Optional[Dict[str, Any]] = Field(None, description="Security profiles")
    parent_dg: Optional[str] = Field(None, alias="parent-dg", description="Parent device group")
    
    class Config:
        populate_by_name = True


class DeviceGroupSummary(ConfigLocation):
    """Summary of a device group with counts of child objects"""
    name: str = Field(..., description="Device group name")
    description: Optional[str] = Field(None, description="Device group description")
    parent_dg: Optional[str] = Field(None, alias="parent-dg", description="Parent device group")
    devices_count: int = Field(0, description="Number of devices in the group")
    address_count: int = Field(0, description="Number of address objects")
    address_group_count: int = Field(0, alias="address-group-count", description="Number of address groups")
    service_count: int = Field(0, description="Number of service objects")
    service_group_count: int = Field(0, alias="service-group-count", description="Number of service groups")
    pre_security_rules_count: int = Field(0, alias="pre-security-rules-count", description="Number of pre-security rules")
    post_security_rules_count: int = Field(0, alias="post-security-rules-count", description="Number of post-security rules")
    pre_nat_rules_count: int = Field(0, alias="pre-nat-rules-count", description="Number of pre-NAT rules")
    post_nat_rules_count: int = Field(0, alias="post-nat-rules-count", description="Number of post-NAT rules")
    
    class Config:
        populate_by_name = True


class Template(ConfigLocation):
    name: str = Field(..., description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    settings: Optional[Dict[str, Any]] = Field(None, description="Template settings")
    config: Optional[Dict[str, Any]] = Field(None, description="Template configuration")
    
    class Config:
        populate_by_name = True


class TemplateStack(ConfigLocation):
    name: str = Field(..., description="Template stack name")
    description: Optional[str] = Field(None, description="Template stack description")
    templates: List[str] = Field(..., description="Member templates")
    devices: Optional[List[Dict[str, Any]]] = Field(None, description="Devices using this stack")
    
    class Config:
        populate_by_name = True


class PanoramaConfig(ConfigLocation):
    version: str = Field(..., description="Configuration version")
    device_groups: List[DeviceGroup] = Field(..., alias="device-groups", description="Device groups")
    templates: List[Template] = Field(..., description="Templates")
    template_stacks: List[TemplateStack] = Field(..., alias="template-stacks", description="Template stacks")
    shared: Optional[Dict[str, Any]] = Field(None, description="Shared objects configuration")
    
    class Config:
        populate_by_name = True


class PaginationParams(BaseModel):
    """Pagination query parameters"""
    page: int = Field(1, ge=1, description="Page number (1-based)")
    page_size: int = Field(500, ge=1, le=10000, description="Number of items per page")
    disable_paging: bool = Field(False, description="Return all results without pagination")


class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper"""
    items: List[Any] = Field(..., description="List of items for current page")
    total_items: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")