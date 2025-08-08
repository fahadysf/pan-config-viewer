export interface Config {
  name: string
  path: string
  size: number
  modified: string
}

export interface Address {
  name: string
  type: 'ip-netmask' | 'fqdn' | 'ip-range'
  value: string
  location: string
  description?: string
}

export interface AddressGroup {
  name: string
  type: string
  members: string[]
  location: string
  description?: string
}

export interface Service {
  name: string
  protocol: string
  port: string
  location: string
  description?: string
}

export interface ServiceGroup {
  name: string
  members: string[]
  location: string
  description?: string
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
  name: string
  parent?: string
  devices: string[]
  addresses: number
  services: number
  policies: {
    pre_rules: number
    post_rules: number
  }
  description?: string
}

export interface Template {
  name: string
  devices: string[]
  variables: Record<string, any>
  description?: string
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
  total: number
  page: number
  page_size: number
  total_pages: number
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