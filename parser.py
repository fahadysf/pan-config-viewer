import os
from typing import List, Dict, Any, Optional
from lxml import etree
from models import (
    AddressObject, AddressGroup, ServiceObject, ServiceGroup,
    VulnerabilityProfile, AntivirusProfile, SpywareProfile,
    URLFilteringProfile, FileBlockingProfile, WildFireAnalysisProfile,
    DataFilteringProfile, SecurityProfileGroup, SecurityRule, NATRule,
    DeviceGroup, DeviceGroupSummary, Template, TemplateStack, LogSetting, Schedule,
    ZoneProtectionProfile, VulnerabilityRule, AntivirusRule,
    SpywareThreat, URLCategory, FileBlockingRule
)


class PanoramaXMLParser:
    def __init__(self, xml_file_path: str):
        self.xml_file_path = xml_file_path
        self.tree = None
        self.root = None
        self.is_panorama = False
        self.is_firewall = False
        self._load_xml()
        self._detect_config_type()
    
    def _load_xml(self):
        """Load and parse the XML file"""
        if not os.path.exists(self.xml_file_path):
            raise FileNotFoundError(f"XML file not found: {self.xml_file_path}")
        
        self.tree = etree.parse(self.xml_file_path)
        self.root = self.tree.getroot()
    
    def _detect_config_type(self):
        """Detect if this is a Panorama or firewall configuration"""
        # Check for Panorama-specific elements
        if self.root.find(".//device-group") is not None or self.root.find(".//template") is not None:
            self.is_panorama = True
        # Check for firewall-specific elements
        elif self.root.find(".//devices/entry/vsys") is not None:
            self.is_firewall = True
    
    def _get_text(self, element, default: str = "") -> str:
        """Safely get text from an XML element"""
        return element.text if element is not None and element.text else default
    
    def _get_list_from_members(self, element) -> List[str]:
        """Extract list from member elements"""
        if element is None:
            return []
        members = element.findall("member")
        return [m.text for m in members if m.text]
    
    def _get_xpath(self, element) -> str:
        """Get the XPath for an element"""
        if element is None:
            return ""
        return self.tree.getpath(element)
    
    def _get_parent_context(self, element) -> Dict[str, Optional[str]]:
        """Get parent device-group, template, or vsys for an element"""
        context = {
            "parent_device_group": None,
            "parent_template": None,
            "parent_vsys": None
        }
        
        if element is None:
            return context
        
        # Walk up the tree to find parent context
        parent = element.getparent()
        while parent is not None:
            # Check for device-group
            if parent.tag == "device-group":
                # Go up one more level to get the entry with the name
                grandparent = parent.getparent()
                if grandparent is not None and grandparent.tag == "entry":
                    context["parent_device_group"] = grandparent.get("name")
                break
            
            # Check for template
            elif parent.tag == "template":
                # Go up one more level to get the entry with the name
                grandparent = parent.getparent()
                if grandparent is not None and grandparent.tag == "entry":
                    context["parent_template"] = grandparent.get("name")
                break
            
            # Check for vsys
            elif parent.tag == "vsys":
                # Go up one more level to get the entry with the name
                grandparent = parent.getparent()
                if grandparent is not None and grandparent.tag == "entry":
                    context["parent_vsys"] = grandparent.get("name")
                break
            
            # Check if we're in a device-group entry
            elif parent.tag == "entry" and parent.getparent() is not None and parent.getparent().tag == "device-group":
                context["parent_device_group"] = parent.get("name")
                break
            
            # Check if we're in a template entry
            elif parent.tag == "entry" and parent.getparent() is not None and parent.getparent().tag == "template":
                context["parent_template"] = parent.get("name")
                break
            
            # Check if we're in a vsys entry
            elif parent.tag == "entry" and parent.getparent() is not None and parent.getparent().tag == "vsys":
                context["parent_vsys"] = parent.get("name")
                break
            
            parent = parent.getparent()
        
        return context
    
    def _add_location_info(self, obj_dict: Dict[str, Any], element) -> Dict[str, Any]:
        """Add xpath and parent context to an object dictionary"""
        obj_dict["xpath"] = self._get_xpath(element)
        context = self._get_parent_context(element)
        obj_dict.update(context)
        return obj_dict
    
    def _parse_addresses_from_element(self, base_element) -> List[AddressObject]:
        """Parse address objects from any element containing address entries"""
        addresses = []
        if base_element is None:
            return addresses
        
        for entry in base_element.findall("entry"):
            name = entry.get("name")
            if not name:
                continue
            
            address_dict = {
                "name": name,
                "ip_netmask": self._get_text(entry.find("ip-netmask")),
                "ip_range": self._get_text(entry.find("ip-range")),
                "fqdn": self._get_text(entry.find("fqdn")),
                "description": self._get_text(entry.find("description")),
                "tag": self._get_list_from_members(entry.find("tag"))
            }
            
            # Add location information
            address_dict = self._add_location_info(address_dict, entry)
            
            address = AddressObject(**address_dict)
            addresses.append(address)
        
        return addresses
    
    def get_all_addresses(self) -> List[AddressObject]:
        """Get all address objects from shared, device groups, templates, and vsys"""
        all_addresses = []
        
        # Get shared addresses
        shared_addresses = self.root.find(".//shared/address")
        all_addresses.extend(self._parse_addresses_from_element(shared_addresses))
        
        # Get addresses from device groups
        for dg in self.root.findall(".//device-group/entry"):
            dg_addresses = dg.find("address")
            all_addresses.extend(self._parse_addresses_from_element(dg_addresses))
        
        # Get addresses from templates  
        for tmpl in self.root.findall(".//template/entry"):
            # Templates may have addresses in config/devices/entry/vsys/entry/address
            for vsys_addresses in tmpl.findall(".//vsys/entry/address"):
                all_addresses.extend(self._parse_addresses_from_element(vsys_addresses))
        
        # Get addresses from firewall vsys
        for vsys_addresses in self.root.findall(".//devices/entry/vsys/entry/address"):
            all_addresses.extend(self._parse_addresses_from_element(vsys_addresses))
        
        return all_addresses
    
    def get_shared_addresses(self) -> List[AddressObject]:
        """Parse shared address objects"""
        shared_addresses = self.root.find(".//shared/address")
        return self._parse_addresses_from_element(shared_addresses)
    
    def get_shared_address_groups(self) -> List[AddressGroup]:
        """Parse shared address groups"""
        groups = []
        shared_groups = self.root.find(".//shared/address-group")
        if shared_groups is None:
            return groups
        
        for entry in shared_groups.findall("entry"):
            name = entry.get("name")
            if not name:
                continue
            
            static_elem = entry.find("static")
            dynamic_elem = entry.find("dynamic")
            
            group_dict = {
                "name": name,
                "static": self._get_list_from_members(static_elem) if static_elem is not None else None,
                "dynamic": self._parse_dynamic_group(dynamic_elem) if dynamic_elem is not None else None,
                "description": self._get_text(entry.find("description")),
                "tag": self._get_list_from_members(entry.find("tag"))
            }
            
            # Add location information
            group_dict = self._add_location_info(group_dict, entry)
            
            group = AddressGroup(**group_dict)
            groups.append(group)
        
        return groups
    
    def _parse_dynamic_group(self, dynamic_elem) -> Dict[str, Any]:
        """Parse dynamic address group configuration"""
        if dynamic_elem is None:
            return {}
        
        result = {}
        filter_elem = dynamic_elem.find("filter")
        if filter_elem is not None:
            result["filter"] = self._get_text(filter_elem)
        
        return result
    
    def get_shared_services(self) -> List[ServiceObject]:
        """Parse shared service objects"""
        services = []
        shared_services = self.root.find(".//shared/service")
        if shared_services is None:
            return services
        
        for entry in shared_services.findall("entry"):
            name = entry.get("name")
            if not name:
                continue
            
            protocol_elem = entry.find("protocol")
            protocol_dict = {}
            
            if protocol_elem is not None:
                tcp_elem = protocol_elem.find("tcp")
                udp_elem = protocol_elem.find("udp")
                
                if tcp_elem is not None:
                    protocol_dict["tcp"] = {
                        "port": self._get_text(tcp_elem.find("port")),
                        "override": self._get_text(tcp_elem.find("override/no")) is not None
                    }
                
                if udp_elem is not None:
                    protocol_dict["udp"] = {
                        "port": self._get_text(udp_elem.find("port")),
                        "override": self._get_text(udp_elem.find("override/no")) is not None
                    }
            
            service_dict = {
                "name": name,
                "protocol": protocol_dict,
                "description": self._get_text(entry.find("description")),
                "tag": self._get_list_from_members(entry.find("tag"))
            }
            
            # Add location information
            service_dict = self._add_location_info(service_dict, entry)
            
            service = ServiceObject(**service_dict)
            services.append(service)
        
        return services
    
    def get_shared_service_groups(self) -> List[ServiceGroup]:
        """Parse shared service groups"""
        groups = []
        shared_groups = self.root.find(".//shared/service-group")
        if shared_groups is None:
            return groups
        
        for entry in shared_groups.findall("entry"):
            name = entry.get("name")
            if not name:
                continue
            
            group = ServiceGroup(
                name=name,
                members=self._get_list_from_members(entry.find("members")),
                description=self._get_text(entry.find("description")),
                tag=self._get_list_from_members(entry.find("tag"))
            )
            groups.append(group)
        
        return groups
    
    def get_vulnerability_profiles(self) -> List[VulnerabilityProfile]:
        """Parse vulnerability protection profiles"""
        profiles = []
        vp_profiles = self.root.find(".//shared/profiles/vulnerability")
        if vp_profiles is None:
            return profiles
        
        for entry in vp_profiles.findall("entry"):
            name = entry.get("name")
            if not name:
                continue
            
            rules = []
            rules_elem = entry.find("rules")
            if rules_elem is not None:
                for rule_entry in rules_elem.findall("entry"):
                    rule_name = rule_entry.get("name")
                    if not rule_name:
                        continue
                    
                    rule_dict = {
                        "name": rule_name,
                        "action": self._get_text(rule_entry.find("action/default"), "default"),
                        "vendor_id": self._get_list_from_members(rule_entry.find("vendor-id")),
                        "severity": self._get_list_from_members(rule_entry.find("severity")),
                        "cve": self._get_list_from_members(rule_entry.find("cve")),
                        "threat_name": self._get_text(rule_entry.find("threat-name"), "any"),
                        "host": self._get_text(rule_entry.find("host"), "any"),
                        "category": self._get_text(rule_entry.find("category"), "any"),
                        "packet_capture": self._get_text(rule_entry.find("packet-capture"))
                    }
                    
                    # Add location information for the rule
                    rule_dict = self._add_location_info(rule_dict, rule_entry)
                    
                    rule = VulnerabilityRule(**rule_dict)
                    rules.append(rule)
            
            profile_dict = {
                "name": name,
                "rules": rules,
                "description": self._get_text(entry.find("description"))
            }
            
            # Add location information for the profile
            profile_dict = self._add_location_info(profile_dict, entry)
            
            profile = VulnerabilityProfile(**profile_dict)
            profiles.append(profile)
        
        return profiles
    
    def get_url_filtering_profiles(self) -> List[URLFilteringProfile]:
        """Parse URL filtering profiles"""
        profiles = []
        url_profiles = self.root.find(".//shared/profiles/url-filtering")
        if url_profiles is None:
            return profiles
        
        for entry in url_profiles.findall("entry"):
            name = entry.get("name")
            if not name:
                continue
            
            profile = URLFilteringProfile(
                name=name,
                action=self._get_text(entry.find("action")),
                block=self._parse_url_categories(entry.find("block")),
                alert=self._parse_url_categories(entry.find("alert")),
                allow=self._parse_url_categories(entry.find("allow")),
                continue_=self._parse_url_categories(entry.find("continue")),
                override=self._parse_url_categories(entry.find("override")),
                description=self._get_text(entry.find("description")),
                log_http_hdr_xff=entry.find("log-http-hdr-xff") is not None,
                log_http_hdr_user_agent=entry.find("log-http-hdr-user-agent") is not None,
                log_http_hdr_referer=entry.find("log-http-hdr-referer") is not None
            )
            profiles.append(profile)
        
        return profiles
    
    def _parse_url_categories(self, element) -> List[URLCategory]:
        """Parse URL categories from an element"""
        categories = []
        if element is None:
            return categories
        
        for member in element.findall("member"):
            if member.text:
                categories.append(URLCategory(
                    name=member.text,
                    action="block"  # Action is determined by parent element
                ))
        
        return categories
    
    def get_device_group_summaries(self) -> List[DeviceGroupSummary]:
        """Parse device groups and return summaries with counts"""
        summaries = []
        dg_element = self.root.find(".//device-group")
        if dg_element is None:
            return summaries
        
        for entry in dg_element.findall("entry"):
            name = entry.get("name")
            if not name:
                continue
            
            # Count devices
            devices_elem = entry.find("devices")
            devices_count = len(devices_elem.findall("entry")) if devices_elem is not None else 0
            
            # Count addresses
            address_elem = entry.find("address")
            address_count = len(address_elem.findall("entry")) if address_elem is not None else 0
            
            # Count address groups
            address_group_elem = entry.find("address-group")
            address_group_count = len(address_group_elem.findall("entry")) if address_group_elem is not None else 0
            
            # Count services
            service_elem = entry.find("service")
            service_count = len(service_elem.findall("entry")) if service_elem is not None else 0
            
            # Count service groups
            service_group_elem = entry.find("service-group")
            service_group_count = len(service_group_elem.findall("entry")) if service_group_elem is not None else 0
            
            # Count rules
            pre_security_rules_count = 0
            post_security_rules_count = 0
            pre_nat_rules_count = 0
            post_nat_rules_count = 0
            
            pre_rulebase = entry.find("pre-rulebase")
            if pre_rulebase is not None:
                security_rules = pre_rulebase.find("security/rules")
                if security_rules is not None:
                    pre_security_rules_count = len(security_rules.findall("entry"))
                nat_rules = pre_rulebase.find("nat/rules")
                if nat_rules is not None:
                    pre_nat_rules_count = len(nat_rules.findall("entry"))
            
            post_rulebase = entry.find("post-rulebase")
            if post_rulebase is not None:
                security_rules = post_rulebase.find("security/rules")
                if security_rules is not None:
                    post_security_rules_count = len(security_rules.findall("entry"))
                nat_rules = post_rulebase.find("nat/rules")
                if nat_rules is not None:
                    post_nat_rules_count = len(nat_rules.findall("entry"))
            
            parent_dg = entry.find("parent-dg")
            
            summary_dict = {
                "name": name,
                "description": self._get_text(entry.find("description")),
                "parent_dg": self._get_text(parent_dg) if parent_dg is not None else None,
                "devices_count": devices_count,
                "address_count": address_count,
                "address_group_count": address_group_count,
                "service_count": service_count,
                "service_group_count": service_group_count,
                "pre_security_rules_count": pre_security_rules_count,
                "post_security_rules_count": post_security_rules_count,
                "pre_nat_rules_count": pre_nat_rules_count,
                "post_nat_rules_count": post_nat_rules_count
            }
            
            # Add location information
            summary_dict = self._add_location_info(summary_dict, entry)
            
            summary = DeviceGroupSummary(**summary_dict)
            summaries.append(summary)
        
        return summaries
    
    def get_device_groups(self) -> List[DeviceGroup]:
        """Parse device groups"""
        groups = []
        dg_element = self.root.find(".//device-group")
        if dg_element is None:
            return groups
        
        for entry in dg_element.findall("entry"):
            name = entry.get("name")
            if not name:
                continue
            
            devices = []
            devices_elem = entry.find("devices")
            if devices_elem is not None:
                for device in devices_elem.findall("entry"):
                    dev_name = device.get("name")
                    if dev_name:
                        devices.append({"name": dev_name})
            
            # Parse pre and post rulebases
            pre_rules = {}
            post_rules = {}
            
            pre_rulebase = entry.find("pre-rulebase")
            if pre_rulebase is not None:
                security_rules = pre_rulebase.find("security/rules")
                if security_rules is not None:
                    pre_rules["security"] = self._parse_security_rules(security_rules)
            
            post_rulebase = entry.find("post-rulebase")
            if post_rulebase is not None:
                security_rules = post_rulebase.find("security/rules")
                if security_rules is not None:
                    post_rules["security"] = self._parse_security_rules(security_rules)
            
            parent_dg = entry.find("parent-dg")
            
            group_dict = {
                "name": name,
                "description": self._get_text(entry.find("description")),
                "devices": devices if devices else None,
                "pre_rules": pre_rules if pre_rules else None,
                "post_rules": post_rules if post_rules else None,
                "parent_dg": self._get_text(parent_dg) if parent_dg is not None else None
            }
            
            # Add location information
            group_dict = self._add_location_info(group_dict, entry)
            
            group = DeviceGroup(**group_dict)
            groups.append(group)
        
        return groups
    
    def _parse_security_rules(self, rules_elem) -> List[SecurityRule]:
        """Parse security rules"""
        rules = []
        for rule_entry in rules_elem.findall("entry"):
            name = rule_entry.get("name")
            if not name:
                continue
            
            rule_dict = {
                "name": name,
                "uuid": self._get_text(rule_entry.find("uuid")),
                "from_": self._get_list_from_members(rule_entry.find("from")),
                "to": self._get_list_from_members(rule_entry.find("to")),
                "source": self._get_list_from_members(rule_entry.find("source")),
                "destination": self._get_list_from_members(rule_entry.find("destination")),
                "source_user": self._get_list_from_members(rule_entry.find("source-user")),
                "category": self._get_list_from_members(rule_entry.find("category")),
                "application": self._get_list_from_members(rule_entry.find("application")),
                "service": self._get_list_from_members(rule_entry.find("service")),
                "action": self._get_text(rule_entry.find("action"), "allow"),
                "log_setting": self._get_text(rule_entry.find("log-setting")),
                "log_start": rule_entry.find("log-start") is not None and self._get_text(rule_entry.find("log-start")) == "yes",
                "log_end": rule_entry.find("log-end") is not None and self._get_text(rule_entry.find("log-end")) == "yes",
                "disabled": rule_entry.find("disabled") is not None and self._get_text(rule_entry.find("disabled")) == "yes",
                "description": self._get_text(rule_entry.find("description")),
                "tag": self._get_list_from_members(rule_entry.find("tag"))
            }
            
            # Parse profile settings
            profile_setting = rule_entry.find("profile-setting")
            if profile_setting is not None:
                rule_dict["profile_setting"] = self._parse_profile_setting(profile_setting)
            
            # Add location information
            rule_dict = self._add_location_info(rule_dict, rule_entry)
            
            rule = SecurityRule(**rule_dict)
            rules.append(rule)
        
        return rules
    
    def _parse_profile_setting(self, profile_elem) -> Dict[str, Any]:
        """Parse profile settings"""
        settings = {}
        
        profiles = profile_elem.find("profiles")
        if profiles is not None:
            profile_dict = {}
            
            for profile_type in ["virus", "spyware", "vulnerability", "url-filtering", 
                               "file-blocking", "data-filtering", "wildfire-analysis"]:
                profile_members = profiles.find(profile_type)
                if profile_members is not None:
                    members = self._get_list_from_members(profile_members)
                    if members:
                        profile_dict[profile_type.replace("-", "_")] = members
            
            if profile_dict:
                settings["profiles"] = profile_dict
        
        group = profile_elem.find("group")
        if group is not None:
            members = self._get_list_from_members(group)
            if members:
                settings["group"] = members
        
        return settings
    
    def get_templates(self) -> List[Template]:
        """Parse templates"""
        templates = []
        template_element = self.root.find(".//template")
        if template_element is None:
            return templates
        
        for entry in template_element.findall("entry"):
            name = entry.get("name")
            if not name:
                continue
            
            settings = {}
            settings_elem = entry.find("settings")
            if settings_elem is not None:
                settings = {
                    "default-vsys": self._get_text(settings_elem.find("default-vsys"))
                }
            
            template = Template(
                name=name,
                description=self._get_text(entry.find("description")),
                settings=settings if settings else None,
                config={}  # Config is complex, implement as needed
            )
            templates.append(template)
        
        return templates
    
    def get_template_stacks(self) -> List[TemplateStack]:
        """Parse template stacks"""
        stacks = []
        stack_element = self.root.find(".//template-stack")
        if stack_element is None:
            return stacks
        
        for entry in stack_element.findall("entry"):
            name = entry.get("name")
            if not name:
                continue
            
            templates = self._get_list_from_members(entry.find("templates"))
            
            devices = []
            devices_elem = entry.find("devices")
            if devices_elem is not None:
                for device in devices_elem.findall("entry"):
                    dev_name = device.get("name")
                    if dev_name:
                        devices.append({"name": dev_name})
            
            stack = TemplateStack(
                name=name,
                description=self._get_text(entry.find("description")),
                templates=templates,
                devices=devices if devices else None
            )
            stacks.append(stack)
        
        return stacks
    
    def get_log_profiles(self) -> List[LogSetting]:
        """Parse log forwarding profiles"""
        profiles = []
        log_profiles = self.root.find(".//shared/log-settings/profiles")
        if log_profiles is None:
            return profiles
        
        for entry in log_profiles.findall("entry"):
            name = entry.get("name")
            if not name:
                continue
            
            profile = LogSetting(
                name=name,
                description=self._get_text(entry.find("description"))
            )
            profiles.append(profile)
        
        return profiles
    
    def get_device_group_addresses(self, device_group_name: str) -> List[AddressObject]:
        """Get addresses for a specific device group"""
        dg_element = self.root.find(f".//device-group/entry[@name='{device_group_name}']")
        if dg_element is None:
            return []
        
        address_elem = dg_element.find("address")
        return self._parse_addresses_from_element(address_elem)
    
    def get_device_group_address_groups(self, device_group_name: str) -> List[AddressGroup]:
        """Get address groups for a specific device group"""
        dg_element = self.root.find(f".//device-group/entry[@name='{device_group_name}']")
        if dg_element is None:
            return []
        
        groups = []
        address_groups = dg_element.find("address-group")
        if address_groups is None:
            return groups
        
        for entry in address_groups.findall("entry"):
            name = entry.get("name")
            if not name:
                continue
            
            static_elem = entry.find("static")
            dynamic_elem = entry.find("dynamic")
            
            group_dict = {
                "name": name,
                "static": self._get_list_from_members(static_elem) if static_elem is not None else None,
                "dynamic": self._parse_dynamic_group(dynamic_elem) if dynamic_elem is not None else None,
                "description": self._get_text(entry.find("description")),
                "tag": self._get_list_from_members(entry.find("tag"))
            }
            
            # Add location information
            group_dict = self._add_location_info(group_dict, entry)
            
            group = AddressGroup(**group_dict)
            groups.append(group)
        
        return groups
    
    def get_device_group_services(self, device_group_name: str) -> List[ServiceObject]:
        """Get services for a specific device group"""
        dg_element = self.root.find(f".//device-group/entry[@name='{device_group_name}']")
        if dg_element is None:
            return []
        
        services = []
        service_elem = dg_element.find("service")
        if service_elem is None:
            return services
        
        for entry in service_elem.findall("entry"):
            name = entry.get("name")
            if not name:
                continue
            
            protocol_elem = entry.find("protocol")
            protocol_dict = {}
            
            if protocol_elem is not None:
                tcp_elem = protocol_elem.find("tcp")
                udp_elem = protocol_elem.find("udp")
                
                if tcp_elem is not None:
                    protocol_dict["tcp"] = {
                        "port": self._get_text(tcp_elem.find("port")),
                        "override": self._get_text(tcp_elem.find("override/no")) is not None
                    }
                
                if udp_elem is not None:
                    protocol_dict["udp"] = {
                        "port": self._get_text(udp_elem.find("port")),
                        "override": self._get_text(udp_elem.find("override/no")) is not None
                    }
            
            service_dict = {
                "name": name,
                "protocol": protocol_dict,
                "description": self._get_text(entry.find("description")),
                "tag": self._get_list_from_members(entry.find("tag"))
            }
            
            # Add location information
            service_dict = self._add_location_info(service_dict, entry)
            
            service = ServiceObject(**service_dict)
            services.append(service)
        
        return services
    
    def get_device_group_service_groups(self, device_group_name: str) -> List[ServiceGroup]:
        """Get service groups for a specific device group"""
        dg_element = self.root.find(f".//device-group/entry[@name='{device_group_name}']")
        if dg_element is None:
            return []
        
        groups = []
        service_groups = dg_element.find("service-group")
        if service_groups is None:
            return groups
        
        for entry in service_groups.findall("entry"):
            name = entry.get("name")
            if not name:
                continue
            
            group_dict = {
                "name": name,
                "members": self._get_list_from_members(entry.find("members")),
                "description": self._get_text(entry.find("description")),
                "tag": self._get_list_from_members(entry.find("tag"))
            }
            
            # Add location information
            group_dict = self._add_location_info(group_dict, entry)
            
            group = ServiceGroup(**group_dict)
            groups.append(group)
        
        return groups
    
    def get_device_group_security_rules(self, device_group_name: str, rulebase: str = "all") -> List[SecurityRule]:
        """Get security rules for a specific device group"""
        dg_element = self.root.find(f".//device-group/entry[@name='{device_group_name}']")
        if dg_element is None:
            return []
        
        rules = []
        
        if rulebase in ["pre", "all"]:
            pre_rulebase = dg_element.find("pre-rulebase")
            if pre_rulebase is not None:
                security_rules = pre_rulebase.find("security/rules")
                if security_rules is not None:
                    rules.extend(self._parse_security_rules(security_rules))
        
        if rulebase in ["post", "all"]:
            post_rulebase = dg_element.find("post-rulebase")
            if post_rulebase is not None:
                security_rules = post_rulebase.find("security/rules")
                if security_rules is not None:
                    rules.extend(self._parse_security_rules(security_rules))
        
        return rules
    
    def get_schedules(self) -> List[Schedule]:
        """Parse schedules"""
        schedules = []
        schedule_elem = self.root.find(".//shared/schedule")
        if schedule_elem is None:
            return schedules
        
        for entry in schedule_elem.findall("entry"):
            name = entry.get("name")
            if not name:
                continue
            
            schedule_type = {}
            type_elem = entry.find("schedule-type")
            if type_elem is not None:
                recurring = type_elem.find("recurring")
                if recurring is not None:
                    daily = recurring.find("daily")
                    if daily is not None:
                        schedule_type = {
                            "recurring": {
                                "daily": self._get_list_from_members(daily)
                            }
                        }
            
            schedule = Schedule(
                name=name,
                schedule_type=schedule_type,
                description=self._get_text(entry.find("description"))
            )
            schedules.append(schedule)
        
        return schedules