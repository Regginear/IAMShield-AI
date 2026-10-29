import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

export default function Policies() {
  const [policies, setPolicies] = useState([])
  const [message, setMessage] = useState('')

  async function loadPolicies() {
    const response = await fetch('/api/policies')
    if (response.ok) setPolicies(await response.json())
  }

  useEffect(() => { loadPolicies().catch(() => setPolicies([])) }, [])

  async function updateStatus(id, status) {
    const response = await fetch(`/api/policies/${id}/status`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ status, reason: `Reviewer selected ${status}.` }) })
    if (response.ok) { setMessage(`Policy ${status}.`); loadPolicies() }
  }

  return <main className="page-shell"><section className="page-heading"><div><p className="eyebrow">POLICY REVIEW</p><h1>Generated policies</h1><p>Review drafts created from observed access behavior and record a decision.</p></div></section><section className="panel">{message && <div className="notice success">{message}</div>}<div className="table-wrap"><table><thead><tr><th>Name</th><th>Type</th><th>Resource</th><th>Status</th><th>Review</th></tr></thead><tbody>{policies.length ? policies.map((policy) => <tr key={policy.id}><td><Link to={`/policies/${policy.id}`}>{policy.name}</Link></td><td>{policy.policy_type}</td><td>{policy.resource_type}</td><td><span className={policy.status === 'approved' ? 'safe-tag' : policy.status === 'rejected' ? 'risk-tag' : 'confidence'}>{policy.status}</span></td><td>{policy.status === 'draft' ? <span className="button-group"><button className="secondary-button" onClick={() => updateStatus(policy.id, 'approved')}>Approve</button><button className="secondary-button" onClick={() => updateStatus(policy.id, 'rejected')}>Reject</button></span> : 'Recorded'}</td></tr>) : <tr><td colSpan="5">No saved policies yet. Run synthesis and save a draft first.</td></tr>}</tbody></table></div></section></main>
}
