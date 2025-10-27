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
      isOpen ? "w-52" : "w-14"
    )}>
      {/* Toggle Button */}
      <div className="flex items-center justify-between p-3 border-b border-gray-800">
        <h2 className={cn("font-semibold text-sm", !isOpen && "hidden")}>Navigation</h2>
        <button
          onClick={onToggle}
          className="p-1 hover:bg-gray-800 rounded"
        >
          {isOpen ? <X size={18} /> : <Menu size={18} />}
        </button>
      </div>

      {/* Menu Items */}
      <nav className="flex-1 overflow-y-auto p-2">
        <ul className="space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon
            const isActive = activeSection === item.id
            const count = stats[item.id] || 0

            return (
              <li key={item.id}>
                <button
                  onClick={() => setActiveSection(item.id)}
                  className={cn(
                    "w-full flex items-center transition-colors",
                    isOpen ? "justify-between px-2 py-1 rounded-lg" : "justify-center p-1 mx-1 rounded-lg",
                    isActive ? "bg-blue-600 text-white" : "hover:bg-gray-800 text-gray-300"
                  )}
                >
                  <div className={cn("flex items-center", isOpen && "gap-2")}>
                    <Icon size={18} />
                    {isOpen && <span className="text-sm">{item.label}</span>}
                  </div>
                  {isOpen && count > 0 && (
                    <span className="bg-gray-700 text-xs px-1.5 py-0.5 rounded">
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
              className={cn(
                "w-full flex items-center transition-colors",
                isOpen ? "justify-between px-2 py-1 rounded-lg" : "justify-center p-1 mx-1 rounded-lg",
                "hover:bg-gray-800 text-gray-300"
              )}
            >
              <div className={cn("flex items-center", isOpen && "gap-2")}>
                <Shield size={18} />
                {isOpen && <span className="text-sm">Security Profiles</span>}
              </div>
              {isOpen && (
                showSecurityProfiles ? <ChevronDown size={14} /> : <ChevronRight size={14} />
              )}
            </button>
            
            {isOpen && showSecurityProfiles && (
              <ul className="ml-6 mt-1 space-y-0.5">
                {securityProfiles.map((profile) => {
                  const isActive = activeSection === `security-profile-${profile.id}`
                  return (
                    <li key={profile.id}>
                      <button
                        onClick={() => setActiveSection(`security-profile-${profile.id}`)}
                        className={cn(
                          "w-full text-left px-2 py-1 rounded text-xs transition-colors",
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