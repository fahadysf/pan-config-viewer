#!/usr/bin/env python3

from lxml import etree
from parser import PanoramaXMLParser

def debug_address_parsing():
    parser = PanoramaXMLParser("/Users/fahad/code/pan-config-viewer/config-files/pan-bkp-202507151414.xml")
    
    # Find the ubuntu-server.fy.loc address entry in XML
    entry = parser.root.find('.//address/entry[@name="ubuntu-server.fy.loc"]')
    if entry is not None:
        print(f"Found entry: {entry.get('name')}")
        
        ip_netmask_elem = entry.find("ip-netmask")
        ip_range_elem = entry.find("ip-range")
        fqdn_elem = entry.find("fqdn")
        
        print(f"IP netmask element: {ip_netmask_elem}")
        print(f"IP range element: {ip_range_elem}")
        print(f"FQDN element: {fqdn_elem}")
        
        if ip_netmask_elem is not None:
            print(f"IP netmask text: '{ip_netmask_elem.text}' (bool: {bool(ip_netmask_elem.text)})")
        if ip_range_elem is not None:
            print(f"IP range text: '{ip_range_elem.text}' (bool: {bool(ip_range_elem.text)})")
        if fqdn_elem is not None:
            print(f"FQDN text: '{fqdn_elem.text}' (bool: {bool(fqdn_elem.text)})")
        
        # Test the values that would be set
        ip_netmask_value = parser._get_text(ip_netmask_elem) if ip_netmask_elem is not None and ip_netmask_elem.text else None
        ip_range_value = parser._get_text(ip_range_elem) if ip_range_elem is not None and ip_range_elem.text else None
        fqdn_value = parser._get_text(fqdn_elem) if fqdn_elem is not None and fqdn_elem.text else None
        
        print(f"Values that would be set:")
        print(f"  ip_netmask: {ip_netmask_value}")
        print(f"  ip_range: {ip_range_value}")
        print(f"  fqdn: {fqdn_value}")
        
        # Parse using the actual method
        print("\nActual parsing result:")
        addresses = parser.get_all_addresses()
        for addr in addresses:
            if addr.name == "ubuntu-server.fy.loc":
                print(f"  Name: {addr.name}")
                print(f"  Type: {addr.type}")
                print(f"  IP netmask: {addr.ip_netmask}")
                print(f"  IP range: {addr.ip_range}")
                print(f"  FQDN: {addr.fqdn}")
                break
    else:
        print("Entry not found!")

if __name__ == "__main__":
    debug_address_parsing()