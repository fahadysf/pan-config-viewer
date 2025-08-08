import { useState } from 'react'
import { cn } from '@/lib/utils'
import { useConfigStore } from '@/stores/configStore'
import {
  ChevronRight,
  ChevronDown,
  Database,
  Network,
  Server,
  Shield,
  FileText,
  Layers,
  Menu,
  X
} from 'lucide-react'

interface SidebarProps {
  isOpen: boolean
  onToggle: () => void
}

const menuItems = [
  { id: 'addresses', label: 'Addresses', icon: Network },
  { id: 'address-groups', label: 'Address Groups', icon: Layers },
  { id: 'services', label: 'Services', icon: Server },
  { id: 'service-groups', label: 'Service Groups', icon: Database },
  { id: 'device-groups', label: 'Device Groups', icon: Layers },
  { id: 'security-policies', label: 'Security Policies', icon: Shield },
  { id: 'templates', label: 'Templates', icon: FileText },
]

const securityProfiles = [
  { id: 'vulnerability', label: 'Vulnerability Profiles' },
  { id: 'url-filtering', label: 'URL Filtering Profiles' },
]

export function Sidebar({ isOpen, onToggle }: SidebarProps) {
  const { activeSection, setActiveSection, stats } = useConfigStore()
  const [showSecurityProfiles, setShowSecurityProfiles] = useState(false)

  return (
    <div className={cn(
      "bg-gray-900 text-white transition-all duration-300 flex flex-col",
      isOpen ? "w-64" : "w-16"
    )}>
      {/* Toggle Button */}
      <div className="flex items-center justify-between p-4 border-b border-gray-800">
        <h2 className={cn("font-semibold", !isOpen && "hidden")}>Navigation</h2>
        <button
          onClick={onToggle}
          className="p-1 hover:bg-gray-800 rounded"
        >
          {isOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Menu Items */}
      <nav className="flex-1 overflow-y-auto p-4">
        <ul className="space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon
            const isActive = activeSection === item.id
            const count = stats[item.id] || 0

            return (
              <li key={item.id}>
                <button
                  onClick={() => setActiveSection(item.id)}
                  className={cn(
                    "w-full flex items-center justify-between px-3 py-2 rounded-lg transition-colors",
                    isActive ? "bg-blue-600 text-white" : "hover:bg-gray-800 text-gray-300"
                  )}
                >
                  <div className="flex items-center gap-3">
                    <Icon size={20} />
                    {isOpen && <span>{item.label}</span>}
                  </div>
                  {isOpen && count > 0 && (
                    <span className="bg-gray-700 text-xs px-2 py-1 rounded">
                      {count}
                    </span>
                  )}
                </button>
              </li>
            )
          })}

          {/* Security Profiles Section */}
          <li>
            <button
              onClick={() => setShowSecurityProfiles(!showSecurityProfiles)}
              className="w-full flex items-center justify-between px-3 py-2 rounded-lg hover:bg-gray-800 text-gray-300"
            >
              <div className="flex items-center gap-3">
                <Shield size={20} />
                {isOpen && <span>Security Profiles</span>}
              </div>
              {isOpen && (
                showSecurityProfiles ? <ChevronDown size={16} /> : <ChevronRight size={16} />
              )}
            </button>
            
            {isOpen && showSecurityProfiles && (
              <ul className="ml-8 mt-2 space-y-1">
                {securityProfiles.map((profile) => {
                  const isActive = activeSection === `security-profile-${profile.id}`
                  return (
                    <li key={profile.id}>
                      <button
                        onClick={() => setActiveSection(`security-profile-${profile.id}`)}
                        className={cn(
                          "w-full text-left px-3 py-2 rounded text-sm transition-colors",
                          isActive ? "bg-blue-600 text-white" : "hover:bg-gray-800 text-gray-400"
                        )}
                      >
                        {profile.label}
                      </button>
                    </li>
                  )
                })}
              </ul>
            )}
          </li>
        </ul>
      </nav>
    </div>
  )
}