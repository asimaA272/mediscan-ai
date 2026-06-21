import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Activity, ScanLine, FileCheck2, Clock3 } from 'lucide-react'
import { getPipelineStatus } from '../services/api'

export default function Dashboard() {
  const [agents, setAgents] = useState([])

  useEffect(() => {
    let isMounted = true
    getPipelineStatus()
      .then((res) => {
        if (isMounted) setAgents(res.data.agents)
      })
      .catch(() => {
        // backend not running yet — show empty state, no crash
        if (isMounted) setAgents([])
      })
    return () => { isMounted = false }
  }, [])

  const metrics = [
    { label: 'Agents online', value: agents.length || 5, icon: Activity, color: 'text-accent-cyan' },
    { label: 'Scans this session', value: 0, icon: ScanLine, color: 'text-accent-blue' },
    { label: 'Reports drafted', value: 0, icon: FileCheck2, color: 'text-accent-green' },
    { label: 'Avg. pipeline time', value: '—', icon: Clock3, color: 'text-accent-amber' },
  ]

  return (
    <div className="p-8 max-w-6xl">
      <header className="mb-8">
        <h1 className="font-display text-2xl font-semibold tracking-tight">Dashboard</h1>
        <p className="text-muted text-sm mt-1">
          Overview of your autonomous medical imaging pipeline.
        </p>
      </header>

      {/* Metrics grid */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        {metrics.map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="bg-bg-panel border border-line rounded-xl p-4">
            <Icon size={18} className={color} />
            <div className="font-display text-2xl font-semibold mt-3">{value}</div>
            <div className="text-xs text-muted mt-1">{label}</div>
          </div>
        ))}
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-2 gap-4 mb-8">
        <Link
          to="/analysis"
          className="bg-bg-panel border border-line rounded-xl p-6 hover:border-accent-cyan/50 transition-colors group"
        >
          <ScanLine size={24} className="text-accent-cyan mb-3" />
          <h3 className="font-display font-semibold mb-1">Upload a new scan</h3>
          <p className="text-sm text-muted">
            Upload a chest X-ray (.dcm, .png, .jpg) and run the full diagnostic pipeline.
          </p>
        </Link>
        <Link
          to="/chat"
          className="bg-bg-panel border border-line rounded-xl p-6 hover:border-accent-cyan/50 transition-colors group"
        >
          <Activity size={24} className="text-accent-green mb-3" />
          <h3 className="font-display font-semibold mb-1">Ask MediScan AI</h3>
          <p className="text-sm text-muted">
            Have a question about an X-ray finding or a condition? Ask the assistant.
          </p>
        </Link>
      </div>

      {/* Agent status preview */}
      <div className="bg-bg-panel border border-line rounded-xl p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-display font-semibold">Agent pipeline status</h3>
          <Link to="/pipeline" className="text-xs text-accent-cyan hover:underline">
            View full pipeline →
          </Link>
        </div>
        <div className="space-y-2">
          {(agents.length ? agents : [
            { agent_name: 'Image Agent', status: 'idle' },
            { agent_name: 'Detection Agent', status: 'idle' },
            { agent_name: 'Differential Agent', status: 'idle' },
            { agent_name: 'Evidence Agent', status: 'idle' },
            { agent_name: 'Report Agent', status: 'idle' },
          ]).map((a) => (
            <div key={a.agent_name} className="flex items-center justify-between py-2 px-3 rounded-lg bg-bg-elevated">
              <span className="text-sm">{a.agent_name}</span>
              <StatusBadge status={a.status} />
            </div>
          ))}
        </div>
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
