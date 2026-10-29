import { useState } from 'react'

function sampleEvents() {
  return JSON.stringify([
    { resource: 'arn:aws:s3:::example-bucket/*', action: 's3:GetObject', access_count: 12, status: 'allowed' },
    { resource: 'arn:aws:s3:::example-bucket', action: 's3:ListBucket', access_count: 5, status: 'allowed' },
  ], null, 2)
}

export default function PolicySynthesis() {
  const [result, setResult] = useState(null)
  const [validation, setValidation] = useState(null)
  const [events, setEvents] = useState('')
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  async function importEvents() {
    setError('')
    setMessage('')
    try {
      const parsed = JSON.parse(events)
      if (!Array.isArray(parsed) || parsed.length === 0) throw new Error('Events must be a non-empty JSON array')
      const response = await fetch('/api/access-patterns/bulk', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ events: parsed }) })
      if (!response.ok) throw new Error('Event import failed')
      const data = await response.json()
      setMessage(`${data.imported} access events imported.`)
    } catch (requestError) { setError(requestError.message) }
  }

  async function runSynthesis() {
    setLoading(true)
    setError('')
    setMessage('')
    try {
      const response = await fetch('/api/synthesis/analyze', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ timeframe_days: 30 }) })
      if (!response.ok) throw new Error('Synthesis request failed')
      const data = await response.json()
      setResult(data)
      const validationResponse = await fetch('/api/synthesis/validate', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ policy_document: data.policy_document, policy_type: 'aws-iam' }) })
      setValidation(await validationResponse.json())
    } catch (requestError) { setError(requestError.message) } finally { setLoading(false) }
  }

  async function saveDraft() {
    if (!result) return
    setSaving(true)
    setError('')
    try {
      const response = await fetch('/api/policies', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: result.policy_name, description: 'Generated from observed access patterns for administrator review.', policy_type: 'aws-iam', resource_type: 'cloud-resource', policy_document: result.policy_document }) })
      if (!response.ok) throw new Error('Could not save policy draft')
      const data = await response.json()
      setMessage(`Draft saved with ID ${data.id}. Review it from the Policies page.`)
    } catch (requestError) { setError(requestError.message) } finally { setSaving(false) }
  }

  return <main className="page-shell">
    <section className="page-heading"><div><p className="eyebrow">SYNTHESIS ENGINE / EXPLAINABLE OUTPUT</p><h1>Generate a least-privilege policy</h1><p>Import access evidence, analyze the recent window, validate the result, and save a draft for review.</p></div><button className="primary-button" onClick={runSynthesis} disabled={loading}>{loading ? 'Analyzing...' : 'Analyze 30 days'}</button></section>
    <section className="panel import-panel"><div><p className="eyebrow">OPTIONAL SAMPLE IMPORT</p><h2>Bring your own normalized events</h2><p>Use a JSON array with resource, action, access_count, and status fields.</p></div><textarea className="event-input" value={events} onChange={(event) => setEvents(event.target.value)} placeholder={sampleEvents()} /><div className="button-group"><button className="secondary-button" onClick={() => setEvents(sampleEvents())}>Load example</button><button className="secondary-button" onClick={importEvents}>Import events</button></div></section>
    {error && <div className="notice error">{error}</div>}{message && <div className="notice success">{message}</div>}
    {result && <section className="content-grid synthesis-grid">
      <div className="panel"><div className="panel-heading"><div><p className="eyebrow">GENERATED POLICY</p><h2>{result.policy_name}</h2></div><span className="confidence">{Math.round(result.confidence_score * 100)}% confidence</span></div><pre className="policy-code">{JSON.stringify(result.policy_document, null, 2)}</pre><div className="recommendations"><h3>Recommendations</h3>{result.recommendations.map((item) => <p key={item}>◆ {item}</p>)}</div><button className="primary-button" onClick={saveDraft} disabled={saving}>{saving ? 'Saving...' : 'Save draft for review'}</button></div>
      <div className="panel"><p className="eyebrow">VALIDATION GATE</p><h2>{validation?.is_valid ? 'Ready for review' : 'Needs attention'}</h2><div className={validation?.is_valid ? 'validation-ok' : 'validation-warning'}>{validation?.is_valid ? 'Policy structure is valid. Review warnings before approval.' : validation?.errors?.join(' ')}</div><h3>Observed permissions</h3><div className="permission-list">{result.permissions.map((item) => <div className="permission" key={`${item.resource}-${item.action}`}><span>{item.action}</span><small>{item.resource} · {item.frequency} events</small></div>)}</div></div>
    </section>}
  </main>
}
