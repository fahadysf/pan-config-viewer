import { useState } from 'react'
import { Sidebar } from './components/layout/Sidebar'
import { Header } from './components/layout/Header'
import { MainContent } from './components/layout/MainContent'
import { ApiStatsWidget } from './components/widgets/ApiStatsWidget'
import { useConfigStore } from './stores/configStore'
import { useApiStatsStore } from './stores/apiStatsStore'

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const { selectedConfig } = useConfigStore()
  const { stats } = useApiStatsStore()

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />
      
      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <Header />
        
        {/* Content */}
        <main className="flex-1 overflow-auto bg-white">
          {selectedConfig ? (
            <MainContent />
          ) : (
            <div className="flex items-center justify-center h-full text-gray-500">
              <div className="text-center">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <h3 className="mt-2 text-sm font-medium text-gray-900">No configuration selected</h3>
                <p className="mt-1 text-sm text-gray-500">Get started by selecting a configuration file from the dropdown above.</p>
              </div>
            </div>
          )}
        </main>
        
        {/* API Stats Widget */}
        <ApiStatsWidget stats={stats} />
      </div>
    </div>
  )
}

export default App