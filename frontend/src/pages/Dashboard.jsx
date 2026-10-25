import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

const API = 'http://localhost:8000'

function Metric({ label, value, tone = '' }) {
  return <div className={`metric ${tone}`}><span>{label}</span><strong>{value}</strong></div>
}

export default function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [patterns, setPatterns] = useState([])
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([
      fetch(`${API}/api/dashboard/summary`).then((response) => response.json()),
      fetch(`${API}/api/access-patterns`).then((response) => response.json()),
    ]).then(([summaryData, patternData]) => {
      setSummary(summaryData)
      setPatterns(patternData)
    }).catch(() => setError('Start the FastAPI backend to load live telemetry.'))
  }, [])

  return (
    <main className="page-shell">
      <section className="hero-panel">
        <div>
          <p className="eyebrow">IDENTITY DEFENSE / LIVE PROTOTYPE</p>
          <h1>Access intelligence, without the guesswork.</h1>
          <p className="hero-copy">IAMShield AI watches real access behavior, finds unnecessary privilege, and turns observed usage into reviewable least-privilege policy.</p>
        </div>
        <Link className="primary-button" to="/synthesis">Run synthesis</Link>
      </section>
      {error && <div className="notice error">{error}</div>}
      <section className="metrics-grid">
        <Metric label="Access events" value={summary?.access_events ?? '—'} />
        <Metric label="Observed permissions" value={summary?.unique_permissions ?? '—'} />
        <Metric label="Risk signals" value={summary?.risky_permissions ?? '—'} tone="warning" />
        <Metric label="Generated policies" value={summary?.generated_policies ?? '—'} tone="success" />
      </section>
      <section className="content-grid">
        <div className="panel">
          <div className="panel-heading"><div><p className="eyebrow">BEHAVIORAL TELEMETRY</p><h2>Observed access patterns</h2></div><span className="status-pill">● monitoring</span></div>
          <div className="table-wrap"><table><thead><tr><th>Resource</th><th>Action</th><th>Frequency</th><th>Signal</th></tr></thead><tbody>
            {patterns.map((item) => <tr key={item.id}><td className="mono">{item.resource}</td><td>{item.action}</td><td>{item.access_count}</td><td>{item.resource === '*' || item.action.includes('*') ? <span className="risk-tag">Review</span> : <span className="safe-tag">Observed</span>}</td></tr>)}
          </tbody></table></div>
        </div>
        <div className="panel side-panel"><p className="eyebrow">CONTROL LOOP</p><h2>From behavior to policy</h2><ol className="workflow"><li><b>Ingest</b><span>CloudTrail and application events</span></li><li><b>Map</b><span>Identity-to-resource relationships</span></li><li><b>Synthesize</b><span>Minimal JSON policy statements</span></li><li><b>Validate</b><span>Wildcard and baseline checks</span></li></ol><Link className="secondary-button" to="/policies">Review policies</Link></div>
      </section>
    </main>
  )
}
