import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { apiRequest } from '../lib/api'

export default function PolicyDetail() {
  const { id } = useParams()
  const [policy, setPolicy] = useState(null)
  const [error, setError] = useState('')
  const [history, setHistory] = useState([])
  const [versions, setVersions] = useState([])

  useEffect(() => {
    apiRequest(`/api/policies/${id}`).then(setPolicy).catch((requestError) => setError(requestError.message))
    apiRequest(`/api/policies/${id}/history`).then(setHistory).catch(() => setHistory([]))
    apiRequest(`/api/policies/${id}/versions`).then(setVersions).catch(() => setVersions([]))
  }, [id])

  async function decide(status) {
    try {
      await apiRequest(`/api/policies/${id}/status`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ status, reason: `Reviewer selected ${status}.` }) })
      setPolicy({ ...policy, status })
    } catch (requestError) { setError(requestError.message) }
  }

  async function exportPolicy() {
    try {
      const data = await apiRequest(`/api/policies/${id}/export`)
      const blob = new Blob([JSON.stringify(data.policy_document, null, 2)], { type: 'application/json' })
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = data.filename
      link.click()
      URL.revokeObjectURL(link.href)
    } catch (requestError) { setError(requestError.message) }
  }

  if (error) return <main className="page-shell"><div className="notice error">{error}</div></main>
  if (!policy) return <main className="page-shell"><div className="panel">Loading policy...</div></main>
  return <main className="page-shell"><section className="page-heading"><div><p className="eyebrow">POLICY DETAIL / REVIEW RECORD</p><h1>{policy.name}</h1><p>{policy.description}</p></div><div className="button-group"><button className="secondary-button" onClick={exportPolicy}>Export JSON</button><Link className="secondary-button" to="/policies">Back to policies</Link></div></section><section className="content-grid"><div className="panel"><p className="eyebrow">POLICY DOCUMENT</p><pre className="policy-code">{JSON.stringify(policy.policy_document, null, 2)}</pre><h3>Versions</h3>{versions.map((version) => <p key={version.version_number}>Version {version.version_number} · {new Date(version.created_at).toLocaleString()}</p>)}</div><div className="panel"><p className="eyebrow">DECISION</p><h2>{policy.status}</h2><p>Approval is recorded as a review decision. Production deployment remains outside this MVP.</p>{policy.status === 'draft' && <div className="button-group"><button className="primary-button" onClick={() => decide('approved')}>Approve</button><button className="secondary-button" onClick={() => decide('rejected')}>Reject</button></div>}<h3>Audit history</h3>{history.length ? history.map((item) => <p key={item.id}>{item.change_type} · {new Date(item.created_at).toLocaleString()}</p>) : <p>No review actions recorded.</p>}</div></section></main>
}
