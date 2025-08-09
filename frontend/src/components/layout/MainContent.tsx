import { useConfigStore } from '@/stores/configStore'
import { DeferredAddressesTable } from '@/components/tables/DeferredAddressesTable'
import { AddressGroupsTable } from '@/components/tables/AddressGroupsTable'
import { ServicesTable } from '@/components/tables/ServicesTable'
import { ServiceGroupsTable } from '@/components/tables/ServiceGroupsTable'
import { DeviceGroupsTable } from '@/components/tables/DeviceGroupsTable'
import { SecurityPoliciesTable } from '@/components/tables/SecurityPoliciesTable'
import { TemplatesTable } from '@/components/tables/TemplatesTable'
import { SecurityProfilesTable } from '@/components/tables/SecurityProfilesTable'

export function MainContent() {
  const { activeSection, selectedConfig } = useConfigStore()

  // Don't render tables if no config is selected
  if (!selectedConfig) {
    return null
  }

  const renderContent = () => {
    // Use key prop to force remount on config change
    const key = `${selectedConfig.name}-${activeSection}`
    
    switch (activeSection) {
      case 'addresses':
        return <DeferredAddressesTable key={key} />
      case 'address-groups':
        return <AddressGroupsTable key={key} />
      case 'services':
        return <ServicesTable key={key} />
      case 'service-groups':
        return <ServiceGroupsTable key={key} />
      case 'device-groups':
        return <DeviceGroupsTable key={key} />
      case 'security-policies':
        return <SecurityPoliciesTable key={key} />
      case 'templates':
        return <TemplatesTable key={key} />
      case 'security-profile-vulnerability':
        return <SecurityProfilesTable key={key} type="vulnerability" />
      case 'security-profile-url-filtering':
        return <SecurityProfilesTable key={key} type="url-filtering" />
      default:
        return <DeferredAddressesTable key={key} />
    }
  }

  return (
    <div className="p-6">
      {renderContent()}
    </div>
  )
}