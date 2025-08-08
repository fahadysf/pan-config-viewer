export interface Config {
  name: string
  path: string
  size: number
  modified: string
}

export interface Address {
  xpath: string
  'parent-device-group': string | null
  'parent-template': string | null
  'parent-vsys': string | null
  name: string
  type: 'ip-netmask' | 'fqdn' | 'ip-range'
  'ip-netmask': string | null
  'ip-range': string | null
  fqdn: string | null
  description?: string
  tag: string[]
}

export interface AddressGroup {
  xpath: string
  'parent-device-group': string | null
  'parent-template': string | null
  'parent-vsys': string | null
  name: string
  static: string[] | null
  dynamic: any | null
  description?: string
  tag: string[]
}

export interface Service {
  xpath: string
  'parent-device-group': string | null
  'parent-template': string | null
  'parent-vsys': string | null
  name: string
  protocol: {
    tcp?: {
      port: string
      override: boolean
    } | null
    udp?: {
      port: string
      override: boolean
    } | null
  }
  description?: string
  tag: string[]
}

export interface ServiceGroup {
  xpath: string | null
  'parent-device-group': string | null
  'parent-template': string | null
  'parent-vsys': string | null
  name: string
  members: string[]
  description?: string
  tag: string[]
}

export interface SecurityPolicy {
  order: number
  name: string
  rule_type: string
  source_zones: string[]
  source_addresses: string[]
  destination_zones: string[]
  destination_addresses: string[]
  applications: string[]
  services: string[]
  action: string
  log_setting?: string
  profile_settings?: Record<string, any>
  description?: string
}

export interface DeviceGroup {
  xpath: string
  'parent-device-group': string | null
  'parent-template': string | null
  'parent-vsys': string | null
  name: string
  description?: string
  'parent-dg': string | null
  devices_count: number
  address_count: number
  'address-group-count': number
  service_count: number
  'service-group-count': number
  'pre-security-rules-count': number
  'post-security-rules-count': number
  'pre-nat-rules-count': number
  'post-nat-rules-count': number
}

export interface Template {
  xpath: string | null
  'parent-device-group': string | null
  'parent-template': string | null
  'parent-vsys': string | null
  name: string
  description?: string
  settings: Record<string, any>
  config: Record<string, any>
}

export interface SecurityProfile {
  name: string
  type: 'vulnerability' | 'url-filtering'
  rules?: any[]
  settings?: Record<string, any>
  description?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total_items: number
  page: number
  page_size: number
  total_pages: number
  has_next: boolean
  has_previous: boolean
}

export interface ApiStats {
  endpoint: string
  query_time: number
  items_retrieved: number
  timestamp: number
}

export interface FilterOperator {
  value: string
  label: string
  applicableTypes: ('text' | 'number')[]
}

export interface ColumnFilter {
  field: string
  operator: string
  value: string
}