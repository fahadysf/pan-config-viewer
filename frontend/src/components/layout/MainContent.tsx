import { useConfigStore } from '@/stores/configStore'
import { AddressesTable } from '@/components/tables/AddressesTable'
import { AddressGroupsTable } from '@/components/tables/AddressGroupsTable'
import { ServicesTable } from '@/components/tables/ServicesTable'
import { ServiceGroupsTable } from '@/components/tables/ServiceGroupsTable'
import { DeviceGroupsTable } from '@/components/tables/DeviceGroupsTable'
import { SecurityPoliciesTable } from '@/components/tables/SecurityPoliciesTable'
import { TemplatesTable } from '@/components/tables/TemplatesTable'
import { SecurityProfilesTable } from '@/components/tables/SecurityProfilesTable'

export function MainContent() {
  const { activeSection } = useConfigStore()

  const renderContent = () => {
    switch (activeSection) {
      case 'addresses':
        return <AddressesTable />
      case 'address-groups':
        return <AddressGroupsTable />
      case 'services':
        return <ServicesTable />
      case 'service-groups':
        return <ServiceGroupsTable />
      case 'device-groups':
        return <DeviceGroupsTable />
      case 'security-policies':
        return <SecurityPoliciesTable />
      case 'templates':
        return <TemplatesTable />
      case 'security-profile-vulnerability':
        return <SecurityProfilesTable type="vulnerability" />
      case 'security-profile-url-filtering':
        return <SecurityProfilesTable type="url-filtering" />
      default:
        return <AddressesTable />
    }
  }

  return (
    <div className="p-6">
      {renderContent()}
    </div>
  )
}