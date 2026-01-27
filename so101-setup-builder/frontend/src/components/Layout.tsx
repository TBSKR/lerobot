import { Outlet, Link, useLocation } from 'react-router-dom'
import { Bot, Home, Wand2, Package, GitCompare, FileText, Settings } from 'lucide-react'
import { clsx } from 'clsx'

const navItems = [
  { path: '/', label: 'Home', icon: Home },
  { path: '/wizard', label: 'Setup Wizard', icon: Wand2 },
  { path: '/components', label: 'Components', icon: Package },
  { path: '/comparison', label: 'Compare', icon: GitCompare },
  { path: '/docs', label: 'Documentation', icon: FileText },
]

export default function Layout() {
  const location = useLocation()

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-2">
              <Bot className="h-8 w-8 text-primary-600" />
              <span className="font-bold text-xl text-gray-900">SO-101 Builder</span>
            </Link>

            {/* Navigation */}
            <nav className="hidden md:flex items-center gap-1">
              {navItems.map((item) => {
                const Icon = item.icon
                const isActive = location.pathname === item.path
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={clsx(
                      'flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                      isActive
                        ? 'bg-primary-50 text-primary-700'
                        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                    )}
                  >
                    <Icon className="h-4 w-4" />
                    {item.label}
                  </Link>
                )
              })}
            </nav>

            {/* Settings */}
            <button className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
              <Settings className="h-5 w-5" />
            </button>
          </div>
        </div>
      </header>

      {/* Mobile Navigation */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-50">
        <div className="flex items-center justify-around py-2">
          {navItems.slice(0, 4).map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            return (
              <Link
                key={item.path}
                to={item.path}
                className={clsx(
                  'flex flex-col items-center gap-1 px-3 py-2 rounded-lg text-xs font-medium transition-colors',
                  isActive
                    ? 'text-primary-600'
                    : 'text-gray-500'
                )}
              >
                <Icon className="h-5 w-5" />
                {item.label}
              </Link>
            )
          })}
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1 pb-20 md:pb-0">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="hidden md:block bg-white border-t border-gray-200 py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between text-sm text-gray-500">
            <p>SO-101 Setup Builder - Built for LeRobot</p>
            <div className="flex items-center gap-4">
              <a
                href="https://github.com/huggingface/lerobot"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-gray-700"
              >
                GitHub
              </a>
              <a
                href="https://huggingface.co/docs/lerobot"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-gray-700"
              >
                LeRobot Docs
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
