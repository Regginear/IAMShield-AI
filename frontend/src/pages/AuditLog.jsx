import { useEffect, useState } from 'react'
import { apiRequest } from '../lib/api'

export default function AuditLog() {
  const [logs, setLogs] = useState([])
  const [error, setError] = useState('')

  useEffect(() => {
    apiRequest('/api/audit-logs')
      .then(setLogs)
      .catch((requestError) => setError(requestError.message))
  }, [])

  return (
    <main className="page-shell">
      <section className="page-heading">
        <div>
          <p className="eyebrow">SECURITY OPERATIONS / AUDIT</p>
          <h1>Review activity</h1>
          <p>Authenticated actions are recorded so policy decisions remain traceable.</p>
        </div>
      </section>
      {error && <div className="notice error">{error}. Sign in to view review history.</div>}
      <section className="panel">
        <div className="table-wrap">
          <table>
            <thead><tr><th>Time</th><th>Action</th><th>Resource</th><th>Details</th></tr></thead>
            <tbody>
              {logs.length ? logs.map((log) => (
                <tr key={log.id}>
                  <td>{new Date(log.created_at).toLocaleString()}</td>
                  <td>{log.action}</td>
                  <td>{log.resource_type || 'workspace'} {log.resource_id ? `#${log.resource_id}` : ''}</td>
                  <td>{log.details || '—'}</td>
                </tr>
              )) : <tr><td colSpan="4">No review activity recorded yet.</td></tr>}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  )
}
