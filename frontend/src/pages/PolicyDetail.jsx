import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

export default function PolicyDetail() {
  const { id } = useParams()
  const [policy, setPolicy] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => { fetch(`/api/policies/${id}`).then((response) => { if (!response.ok) throw new Error('Policy not found'); return response.json() }).then(setPolicy).catch((requestError) => setError(requestError.message)) }, [id])

  async function decide(status) {
    const response = await fetch(`/api/policies/${id}/status`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ status, reason: `Reviewer selected ${status}.` }) })
    if (response.ok) setPolicy({ ...policy, status })
  }

  if (error) return <main className="page-shell"><div className="notice error">{error}</div></main>
  if (!policy) return <main className="page-shell"><div className="panel">Loading policy...</div></main>
  return <main className="page-shell"><section className="page-heading"><div><p className="eyebrow">POLICY DETAIL / REVIEW RECORD</p><h1>{policy.name}</h1><p>{policy.description}</p></div><Link className="secondary-button" to="/policies">Back to policies</Link></section><section className="content-grid"><div className="panel"><p className="eyebrow">POLICY DOCUMENT</p><pre className="policy-code">{JSON.stringify(policy.policy_document, null, 2)}</pre></div><div className="panel"><p className="eyebrow">DECISION</p><h2>{policy.status}</h2><p>Approval is recorded as a prototype review decision. Production deployment remains outside this MVP.</p>{policy.status === 'draft' && <div className="button-group"><button className="primary-button" onClick={() => decide('approved')}>Approve</button><button className="secondary-button" onClick={() => decide('rejected')}>Reject</button></div>}</div></section></main>
}
