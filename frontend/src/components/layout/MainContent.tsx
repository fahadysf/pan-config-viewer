import { useConfigStore } from '@/stores/configStore'
import { DeferredAddressesTable } from '@/components/tables/DeferredAddressesTable'
import { DeferredAddressGroupsTable } from '@/components/tables/DeferredAddressGroupsTable'
import { DeferredServicesTable } from '@/components/tables/DeferredServicesTable'
import { DeferredServiceGroupsTable } from '@/components/tables/DeferredServiceGroupsTable'
import { DeferredDeviceGroupsTable } from '@/components/tables/DeferredDeviceGroupsTable'
import { DeferredSecurityPoliciesTable } from '@/components/tables/DeferredSecurityPoliciesTable'
import { DeferredTemplatesTable } from '@/components/tables/DeferredTemplatesTable'
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
        return <DeferredAddressGroupsTable key={key} />
      case 'services':
        return <DeferredServicesTable key={key} />
      case 'service-groups':
        return <DeferredServiceGroupsTable key={key} />
      case 'device-groups':
        return <DeferredDeviceGroupsTable key={key} />
      case 'security-policies':
        return <DeferredSecurityPoliciesTable key={key} />
      case 'templates':
        return <DeferredTemplatesTable key={key} />
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