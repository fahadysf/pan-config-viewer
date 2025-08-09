import axios from 'axios'
import { 
  Config, 
  PaginatedResponse, 
  Address, 
  AddressGroup, 
  Service, 
  ServiceGroup,
  SecurityPolicy,
  DeviceGroup,
  Template,
  SecurityProfile,
  ColumnFilter
} from '@/types/api'
import { useApiStatsStore } from '@/stores/apiStatsStore'

const API_BASE_URL = '/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60 second timeout to prevent hanging
})

// Extend AxiosRequestConfig to include metadata
declare module 'axios' {
  export interface AxiosRequestConfig {
    metadata?: {
      startTime: number
    }
  }
}

// Add request interceptor to track API calls
api.interceptors.request.use((config) => {
  config.metadata = { startTime: Date.now() }
  return config
})

// Add response interceptor to track API stats
api.interceptors.response.use(
  (response) => {
    const endTime = Date.now()
    const duration = endTime - (response.config.metadata?.startTime || Date.now())
    
    // Add to stats store
    const { addStat } = useApiStatsStore.getState()
    addStat({
      endpoint: response.config.url || '',
      query_time: duration,
      items_retrieved: response.data.items?.length || response.data.length || 0,
      timestamp: endTime,
    })
    
    return response
  },
  (error) => {
    // Handle cancellation gracefully
    if (axios.isCancel(error)) {
      console.log('Request cancelled:', error.message)
      return Promise.resolve(null)
    }
    return Promise.reject(error)
  }
)

// Build filter query params
const buildFilterParams = (filters: ColumnFilter[]): Record<string, string> => {
  const params: Record<string, string> = {}
  filters.forEach(filter => {
    if (filter.operator === 'is_empty') {
      params['is_null'] = 'true'
    } else if (filter.operator === 'is_not_empty') {
      params['is_not_null'] = 'true'
    } else {
      // Use dot notation format: filter.field.operator=value
      params[`filter.${filter.field}.${filter.operator}`] = filter.value
    }
  })
  return params
}

// API methods
export const configApi = {
  getConfigInfo: async (configName: string): Promise<Config> => {
    const response = await api.get(`/configs/${configName}/info`)
    return response.data
  },

  getConfigs: async (): Promise<Config[]> => {
    const response = await api.get('/configs')
    // The API returns { configs: [...], count: number, path: string }
    // configs is an array of string names, we need to get full info for each
    const configNames: string[] = response.data.configs || []
    
    // Get full info for each config
    const configPromises = configNames.map(async (name) => {
      try {
        const infoResponse = await api.get(`/configs/${name}/info`)
        return infoResponse.data
      } catch (error) {
        // If we can't get info, create a minimal config object
        return {
          name,
          path: `./config-files/${name}.xml`,
          size: 0,
          modified: new Date().toISOString()
        }
      }
    })
    
    return Promise.all(configPromises)
  },

  getAddresses: async (
    config: string, 
    page = 1, 
    pageSize = 10,
    filters: ColumnFilter[] = []
  ): Promise<PaginatedResponse<Address>> => {
    const response = await api.get(`/configs/${config}/addresses`, {
      params: {
        page,
        page_size: pageSize,
        ...buildFilterParams(filters),
      },
    })
    return response.data
  },

  getAddressGroups: async (
    config: string,
    page = 1,
    pageSize = 10,
    filters: ColumnFilter[] = []
  ): Promise<PaginatedResponse<AddressGroup>> => {
    const response = await api.get(`/configs/${config}/address-groups`, {
      params: {
        page,
        page_size: pageSize,
        ...buildFilterParams(filters),
      },
    })
    return response.data
  },

  getServices: async (
    config: string,
    page = 1,
    pageSize = 10,
    filters: ColumnFilter[] = []
  ): Promise<PaginatedResponse<Service>> => {
    const response = await api.get(`/configs/${config}/services`, {
      params: {
        page,
        page_size: pageSize,
        ...buildFilterParams(filters),
      },
    })
    return response.data
  },

  getServiceGroups: async (
    config: string,
    page = 1,
    pageSize = 10,
    filters: ColumnFilter[] = []
  ): Promise<PaginatedResponse<ServiceGroup>> => {
    const response = await api.get(`/configs/${config}/service-groups`, {
      params: {
        page,
        page_size: pageSize,
        ...buildFilterParams(filters),
      },
    })
    return response.data
  },

  getSecurityPolicies: async (
    config: string,
    page = 1,
    pageSize = 10,
    filters: ColumnFilter[] = []
  ): Promise<PaginatedResponse<SecurityPolicy>> => {
    const response = await api.get(`/configs/${config}/security-policies`, {
      params: {
        page,
        page_size: pageSize,
        ...buildFilterParams(filters),
      },
    })
    return response.data
  },

  getDeviceGroups: async (
    config: string,
    page = 1,
    pageSize = 10,
    filters: ColumnFilter[] = []
  ): Promise<PaginatedResponse<DeviceGroup>> => {
    const response = await api.get(`/configs/${config}/device-groups`, {
      params: {
        page,
        page_size: pageSize,
        ...buildFilterParams(filters),
      },
    })
    return response.data
  },

  getTemplates: async (
    config: string,
    page = 1,
    pageSize = 10,
    filters: ColumnFilter[] = []
  ): Promise<PaginatedResponse<Template>> => {
    const response = await api.get(`/configs/${config}/templates`, {
      params: {
        page,
        page_size: pageSize,
        ...buildFilterParams(filters),
      },
    })
    return response.data
  },

  getSecurityProfiles: async (
    config: string,
    type: 'vulnerability' | 'url-filtering',
    page = 1,
    pageSize = 10,
    filters: ColumnFilter[] = []
  ): Promise<PaginatedResponse<SecurityProfile>> => {
    const response = await api.get(`/configs/${config}/security-profiles/${type}`, {
      params: {
        page,
        page_size: pageSize,
        ...buildFilterParams(filters),
      },
    })
    return response.data
  },
}