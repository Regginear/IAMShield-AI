import { useEffect, useState } from 'react'

export default function Policies() {
  const [policies, setPolicies] = useState([])
  useEffect(() => { fetch('http://localhost:8000/api/policies').then((response) => response.json()).then(setPolicies).catch(() => setPolicies([])) }, [])
  return <main className="page-shell"><section className="page-heading"><div><p className="eyebrow">POLICY REVIEW</p><h1>Generated policies</h1><p>Reviewable drafts created from observed access behavior.</p></div></section><section className="panel"><div className="table-wrap"><table><thead><tr><th>Name</th><th>Type</th><th>Resource</th><th>Status</th></tr></thead><tbody>{policies.length ? policies.map((policy) => <tr key={policy.id}><td>{policy.name}</td><td>{policy.policy_type}</td><td>{policy.resource_type}</td><td><span className="safe-tag">{policy.status}</span></td></tr>) : <tr><td colSpan="4">No saved policies yet. Run synthesis to create a draft.</td></tr>}</tbody></table></div></section></main>
}
