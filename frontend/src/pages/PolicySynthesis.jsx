import { useState } from 'react'

const API = 'http://localhost:8000'

export default function PolicySynthesis() {
  const [result, setResult] = useState(null)
  const [validation, setValidation] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function runSynthesis() {
    setLoading(true)
    setError('')
    try {
      const response = await fetch(`${API}/api/synthesis/analyze`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ timeframe_days: 30 }) })
      if (!response.ok) throw new Error('Synthesis request failed')
      const data = await response.json()
      setResult(data)
      const validationResponse = await fetch(`${API}/api/synthesis/validate`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ policy_document: data.policy_document, policy_type: 'aws-iam' }) })
      setValidation(await validationResponse.json())
    } catch (requestError) { setError(requestError.message) } finally { setLoading(false) }
  }

  return <main className="page-shell">
    <section className="page-heading"><div><p className="eyebrow">SYNTHESIS ENGINE / EXPLAINABLE OUTPUT</p><h1>Generate a least-privilege policy</h1><p>IAMShield AI converts observed access patterns into a narrow, reviewable policy document.</p></div><button className="primary-button" onClick={runSynthesis} disabled={loading}>{loading ? 'Analyzing...' : 'Analyze 30 days'}</button></section>
    {error && <div className="notice error">{error}. Confirm the backend is running on port 8000.</div>}
    {result && <section className="content-grid synthesis-grid">
      <div className="panel"><div className="panel-heading"><div><p className="eyebrow">GENERATED POLICY</p><h2>{result.policy_name}</h2></div><span className="confidence">{Math.round(result.confidence_score * 100)}% confidence</span></div><pre className="policy-code">{JSON.stringify(result.policy_document, null, 2)}</pre><div className="recommendations"><h3>Recommendations</h3>{result.recommendations.map((item) => <p key={item}>◆ {item}</p>)}</div></div>
      <div className="panel"><p className="eyebrow">VALIDATION GATE</p><h2>{validation?.is_valid ? 'Ready for review' : 'Needs attention'}</h2><div className={validation?.is_valid ? 'validation-ok' : 'validation-warning'}>{validation?.is_valid ? 'Policy structure is valid.' : validation?.errors?.join(' ')}</div><h3>Observed permissions</h3><div className="permission-list">{result.permissions.map((item) => <div className="permission" key={`${item.resource}-${item.action}`}><span>{item.action}</span><small>{item.resource} · {item.frequency} events</small></div>)}</div></div>
    </section>}
  </main>
}
