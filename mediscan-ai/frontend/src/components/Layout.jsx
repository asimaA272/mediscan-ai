import React from 'react'
import { NavLink } from 'react-router-dom'
import { LayoutDashboard, ScanLine, GitBranch, MessageSquareText, Activity } from 'lucide-react'

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/analysis', label: 'X-Ray Analysis', icon: ScanLine },
  { to: '/pipeline', label: 'Pipeline', icon: GitBranch },
  { to: '/chat', label: 'AI Chat', icon: MessageSquareText },
]

export default function Layout({ children }) {
  return (
    <div className="min-h-screen flex bg-bg text-[#E5EAF2] font-body">
      {/* Sidebar */}
      <aside className="w-60 shrink-0 border-r border-line bg-bg-panel flex flex-col">
        <div className="px-5 py-6 border-b border-line">
          <div className="flex items-center gap-2">
            <Activity size={22} className="text-accent-cyan" strokeWidth={2.5} />
            <span className="font-display font-semibold text-lg tracking-tight">MediScan AI</span>
          </div>
          <p className="text-xs text-muted mt-1">Autonomous Diagnostic System</p>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1">
          {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-accent-cyan/10 text-accent-cyan'
                    : 'text-muted hover:text-[#E5EAF2] hover:bg-bg-elevated'
                }`
              }
            >
              <Icon size={18} strokeWidth={2} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="px-5 py-4 border-t border-line">
          <div className="flex items-center gap-2 text-xs text-muted">
            <span className="w-2 h-2 rounded-full bg-accent-green animate-pulse" />
            NVIDIA NIM connected
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">{children}</main>
    </div>
  )
}
