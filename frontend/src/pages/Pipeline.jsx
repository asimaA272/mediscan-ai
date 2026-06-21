import React, { useEffect, useState } from 'react'
import { ImageIcon, ScanSearch, ListTree, BookOpenText, FileSignature } from 'lucide-react'
import { getPipelineStatus } from '../services/api'

const AGENT_ICONS = {
  'Image Agent': ImageIcon,
  'Detection Agent': ScanSearch,
  'Differential Agent': ListTree,
  'Evidence Agent': BookOpenText,
  'Report Agent': FileSignature,
}

export default function Pipeline() {
  const [agents, setAgents] = useState([])
  const [error, setError] = useState(false)

  useEffect(() => {
    let isMounted = true

    const poll = () => {
      getPipelineStatus()
        .then((res) => {
          if (isMounted) {
            setAgents(res.data.agents)
            setError(false)
          }
        })
        .catch(() => {
          if (isMounted) setError(true)
        })
    }

    poll()
    const interval = setInterval(poll, 2000) // live polling every 2s
    return () => {
      isMounted = false
      clearInterval(interval)
    }
  }, [])

  return (
    <div className="p-8 max-w-6xl">
      <header className="mb-6">
        <h1 className="font-display text-2xl font-semibold tracking-tight">Multi-Agent Pipeline</h1>
        <p className="text-muted text-sm mt-1">
          Live status of all 5 agents. Updates every 2 seconds while a scan runs.
        </p>
      </header>

      {error && (
        <div className="mb-4 text-sm text-accent-red bg-accent-red/10 rounded-lg p-3">
          Could not reach the backend. Make sure it's running on the URL set in VITE_API_URL.
        </div>
      )}

      <div className="space-y-3">
        {agents.map((agent, i) => {
          const Icon = AGENT_ICONS[agent.agent_name] || ImageIcon
          return (
            <div key={agent.agent_name} className="bg-bg-panel border border-line rounded-xl p-5 flex items-center gap-4">
              <div className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 ${
                agent.status === 'active' ? 'bg-accent-cyan/10' :
                agent.status === 'done' ? 'bg-accent-green/10' :
                agent.status === 'error' ? 'bg-accent-red/10' : 'bg-bg-elevated'
              }`}>
                <Icon size={18} className={
                  agent.status === 'active' ? 'text-accent-cyan' :
                  agent.status === 'done' ? 'text-accent-green' :
                  agent.status === 'error' ? 'text-accent-red' : 'text-muted'
                } />
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <span className="font-medium text-sm">{i + 1}. {agent.agent_name}</span>
                  <StatusBadge status={agent.status} />
                </div>
                <p className="text-xs text-muted mt-1">{agent.last_message}</p>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

function StatusBadge({ status }) {
  const styles = {
    idle: 'bg-muted/10 text-muted',
    active: 'bg-accent-cyan/10 text-accent-cyan',
    busy: 'bg-accent-amber/10 text-accent-amber',
    done: 'bg-accent-green/10 text-accent-green',
    error: 'bg-accent-red/10 text-accent-red',
  }
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full font-medium capitalize ${styles[status] || styles.idle}`}>
      {status}
    </span>
  )
}
