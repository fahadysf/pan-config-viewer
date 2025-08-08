interface SecurityProfilesTableProps {
  type: string
}

export function SecurityProfilesTable({ type }: SecurityProfilesTableProps) {
  const getTitle = () => {
    switch (type) {
      case 'vulnerability':
        return 'Vulnerability Protection Profiles'
      case 'url-filtering':
        return 'URL Filtering Profiles'
      default:
        return 'Security Profiles'
    }
  }

  const getDescription = () => {
    switch (type) {
      case 'vulnerability':
        return 'Manage vulnerability protection and threat prevention profiles'
      case 'url-filtering':
        return 'Manage URL filtering and web security profiles'
      default:
        return 'Manage security profiles and protection settings'
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">{getTitle()}</h2>
        <p className="text-muted-foreground">
          {getDescription()}
        </p>
      </div>
      
      <div className="flex items-center justify-center h-64 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
        <div className="text-center">
          <h3 className="text-lg font-medium text-gray-900 mb-2">Coming Soon</h3>
          <p className="text-gray-500">This feature is currently under development</p>
        </div>
      </div>
    </div>
  )
}