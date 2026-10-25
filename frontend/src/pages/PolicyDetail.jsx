import { useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import Icon from '../components/Icon'
import { apiRequest } from '../lib/api'
import { cloudProvider, policyRiskSummary } from '../lib/policyAnalysis'

function inferredResourceType(policy) {
  const resources = policyRiskSummary(policy.policy_document).permissions.map((permission) => permission.resource)
  const arn = resources.map((resource) => resource.match(/^arn:aws:([^:]+):/)).find(Boolean)
  if (arn) return arn[1]
  const declaredType = (policy.resource_type || '').toLowerCase()
  return declaredType && !declaredType.includes('aws iam') ? declaredType : ''
}

function permissionKey(permission) {
  return `${permission.effect}:${permission.action}:${permission.resource}`
}

function formatTimestamp(timestamp) {
  if (!timestamp) return 'Not provided by API'
  const date = new Date(timestamp)
  return Number.isNaN(date.getTime()) ? 'Not provided by API' : date.toLocaleString()
}

function FindingList({ findings }) {
  if (!findings.length) return <p className="detail-empty">No wildcard action or unrestricted-resource signals were found by the frontend heuristic.</p>
  return <ul className="detail-findings">{findings.map((finding) => (
    <li key={finding.id}><span className={`risk-tag ${finding.severity === 'critical' ? 'critical' : ''}`}>{finding.severity}</span><div><strong>{finding.title}</strong><p>{finding.description}</p><small>{finding.recommendation}</small></div></li>
  ))}</ul>
}

export default function PolicyDetail() {
  const { id } = useParams()
  const [policy, setPolicy] = useState(null)
  const [comparison, setComparison] = useState(null)
  const [loading, setLoading] = useState(true)
  const [comparisonLoading, setComparisonLoading] = useState(false)
  const [error, setError] = useState('')
  const [comparisonError, setComparisonError] = useState('')

  useEffect(() => {
    let cancelled = false
    async function loadPolicy() {
      setLoading(true)
      setError('')
      setComparison(null)
      setComparisonError('')
      try {
        const policies = await apiRequest('/api/policies')
        if (!Array.isArray(policies)) throw new Error('The policies endpoint returned an unexpected response.')
        const selectedPolicy = policies.find((item) => String(item.id) === id)
        if (!selectedPolicy) throw new Error('This policy could not be found in the current inventory.')
        if (cancelled) return
        setPolicy(selectedPolicy)
        setLoading(false)

        const resourceType = inferredResourceType(selectedPolicy)
        if (!resourceType) {
          setComparisonError('A matching cloud resource type could not be inferred; an observed-access draft comparison is unavailable.')
          return
        }
        setComparisonLoading(true)
        try {
          const suggestion = await apiRequest('/api/synthesis/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ timeframe_days: 30, resource_type: resourceType }),
          })
          if (!cancelled) setComparison(suggestion)
        } catch (requestError) {
          if (!cancelled) setComparisonError(`Observed-access comparison unavailable: ${requestError.message}`)
        } finally {
          if (!cancelled) setComparisonLoading(false)
        }
      } catch (requestError) {
        if (!cancelled) setError(requestError.message)
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    loadPolicy()
    return () => { cancelled = true }
  }, [id])

  const analysis = useMemo(() => policy ? policyRiskSummary(policy.policy_document) : null, [policy])
  const provider = policy ? cloudProvider(policy) : 'Not specified'
  const resources = analysis ? [...new Set(analysis.permissions.flatMap((permission) => permission.resource.split(',').map((resource) => resource.trim())).filter(Boolean))] : []
  const comparisonPermissions = comparison ? policyRiskSummary(comparison.policy_document).permissions.filter((permission) => permission.effect === 'Allow') : []
  const currentPermissionKeys = new Set(analysis?.permissions.filter((permission) => permission.effect === 'Allow').map(permissionKey) || [])
  const proposedPermissionKeys = new Set(comparisonPermissions.map(permissionKey))
  const proposedOnly = comparisonPermissions.filter((permission) => !currentPermissionKeys.has(permissionKey(permission)))
  const currentOnly = analysis?.permissions.filter((permission) => permission.effect === 'Allow' && !proposedPermissionKeys.has(permissionKey(permission))) || []
  const riskClass = analysis?.risk === 'critical' ? 'risk-tag critical' : analysis?.risk === 'high' ? 'risk-tag' : analysis?.risk === 'low' ? 'safe-tag' : 'neutral-tag'

  return (
    <main className="page-shell">
      <section className="page-heading">
        <div><p className="eyebrow">IDENTITY GOVERNANCE / POLICY REVIEW</p><h1>{policy?.name || 'Policy details'}</h1><p>Inspect document permissions and heuristic findings. Recommendations never modify a cloud policy.</p></div>
        <Link className="secondary-button" to="/policies"><Icon name="chevron" size={13} />Back to inventory</Link>
      </section>
      {error && <div className="notice error" role="alert"><Icon name="alert" size={15} />{error}</div>}
      {loading && <section className="panel analysis-loading" role="status"><span className="loading-spinner" /><strong>Loading policy details</strong></section>}
      {policy && analysis && (
        <>
          <section className="detail-metrics metrics-grid">
            <article className="metric"><div className="metric-top"><span className="metric-label">Cloud provider</span><span className="metric-icon"><Icon name="cloud" size={15} /></span></div><strong>{provider}</strong><div className="metric-foot">{policy.resource_type || 'Resource type not provided by API'}</div></article>
            <article className={`metric ${analysis.excessivePermissions ? 'warning' : 'success'}`}><div className="metric-top"><span className="metric-label">Wildcard grants</span><span className="metric-icon"><Icon name="alert" size={15} /></span></div><strong>{analysis.excessivePermissions}</strong><div className="metric-foot">Heuristic findings · review manually</div></article>
            <article className="metric"><div className="metric-top"><span className="metric-label">Permissions</span><span className="metric-icon"><Icon name="lock" size={15} /></span></div><strong>{analysis.permissions.length}</strong><div className="metric-foot">{resources.length} associated resources</div></article>
            <article className="metric"><div className="metric-top"><span className="metric-label">Policy status</span><span className="metric-icon"><Icon name="file" size={15} /></span></div><strong className="metric-status">{policy.status || 'Unknown'}</strong><div className="metric-foot">Approval actions are not configured</div></article>
          </section>

          <div className="notice demo-notice" role="note"><Icon name="alert" size={15} /><span>Risk labels only identify wildcard actions and unrestricted resource scopes. This frontend does not simulate effective IAM access or know the identity’s complete usage history.</span></div>

          <section className="detail-grid">
            <article className="panel">
              <div className="panel-heading"><div><p className="panel-kicker">POLICY DOCUMENT</p><h2>{policy.name}</h2><span className="panel-subtitle">Current saved document · no automatic changes</span></div><span className={policy.status === 'active' ? 'safe-tag' : 'neutral-tag'}>{policy.status || 'Unknown'}</span></div>
              <pre className="policy-code detail-json"><code>{JSON.stringify(policy.policy_document, null, 2)}</code></pre>
            </article>
            <aside className="panel">
              <div className="panel-heading"><div><p className="panel-kicker">RISK FINDINGS</p><h2>Review signals</h2></div><span className={riskClass}>{analysis.risk}</span></div>
              <FindingList findings={analysis.findings} />
              <h3 className="subsection-heading">Associated resources</h3>
              {resources.length ? <ul className="resource-list">{resources.map((resource) => <li key={resource}><Icon name="database" size={13} /><span title={resource}>{resource}</span></li>)}</ul> : <p className="detail-empty">No resource ARNs were present in the policy document.</p>}
              <h3 className="subsection-heading">Policy metadata</h3>
              <div className="detail-metadata">
                <div><span>Policy ID</span><strong>#{policy.id}</strong></div>
                <div><span>Provider</span><strong>{provider}</strong></div>
                <div><span>Type</span><strong>{policy.policy_type || 'Not provided'}</strong></div>
                <div><span>Last updated</span><strong>{formatTimestamp(policy.updated_at || policy.created_at)}</strong></div>
              </div>
            </aside>
          </section>

          <section className="panel permission-panel">
            <div className="panel-heading"><div><p className="panel-kicker">PERMISSION REVIEW</p><h2>Actions and resources</h2><span className="panel-subtitle">Explanations are based on the document only, not runtime authorization results.</span></div></div>
            <div className="table-wrap"><table><thead><tr><th>Effect</th><th>Action</th><th>Resource</th><th>Finding</th></tr></thead><tbody>
              {analysis.permissions.map((permission, index) => {
                const wildcard = permission.effect === 'Allow' && (permission.action.includes('*') || permission.resource === '*')
                const broadGrant = wildcard || permission.action.startsWith('NotAction:') || permission.resource.startsWith('NotResource:')
                return <tr key={`${permissionKey(permission)}-${index}`}><td>{permission.effect}</td><td className={broadGrant ? 'permission-risk' : ''}>{permission.action}</td><td className="mono" title={permission.resource}>{permission.resource}</td><td>{broadGrant ? <span className="risk-tag">Review scope</span> : <span className="safe-tag">No wildcard detected</span>}</td></tr>
              })}
              {!analysis.permissions.length && <tr><td colSpan="4" className="table-empty">No statements were available to review.</td></tr>}
            </tbody></table></div>
          </section>

          <section className="panel comparison-panel">
            <div className="panel-heading"><div><p className="panel-kicker">OBSERVED-ACCESS COMPARISON</p><h2>Current document vs. generated reference</h2><span className="panel-subtitle">A read-only comparison from the last 30 days of matching service telemetry. It is not an approval or deployment action.</span></div><span className="neutral-tag">No automatic policy changes</span></div>
            {comparisonLoading && <div className="analysis-loading comparison-loading" role="status"><span className="loading-spinner" /><strong>Preparing observed-access reference</strong></div>}
            {comparisonError && <div className="notice" role="status"><Icon name="alert" size={14} />{comparisonError}</div>}
            {comparison && (
              <div className="comparison-grid">
                <article className="comparison-column"><h3>Current saved policy <span>{analysis.permissions.filter((permission) => permission.effect === 'Allow').length} allow entries</span></h3><ul>{analysis.permissions.filter((permission) => permission.effect === 'Allow').map((permission, index) => { const unobserved = currentOnly.some((candidate) => permissionKey(candidate) === permissionKey(permission)); return <li key={`${permissionKey(permission)}-${index}`}><span className={`comparison-mark ${unobserved ? 'unobserved' : 'matched'}`}>{unobserved ? '−' : '='}</span><span><strong>{permission.action}</strong><small>{permission.resource}</small></span></li> })}{!currentPermissionKeys.size && <li className="detail-empty">No allow entries in this policy.</li>}</ul></article>
                <article className="comparison-column"><h3>Observed-access reference <span>{comparisonPermissions.length} allow entries</span></h3><p className="comparison-disclaimer">Generated from matching service events. This dataset is not identity-specific and may contain seeded demo patterns.</p><ul>{comparisonPermissions.map((permission) => <li key={permissionKey(permission)}><span className={`comparison-mark ${proposedOnly.some((candidate) => permissionKey(candidate) === permissionKey(permission)) ? 'proposed' : 'matched'}`}>{proposedOnly.some((candidate) => permissionKey(candidate) === permissionKey(permission)) ? '+' : '='}</span><span><strong>{permission.action}</strong><small>{permission.resource}</small></span></li>)}{!comparisonPermissions.length && <li className="detail-empty">No matching access was observed during the selected window.</li>}</ul></article>
                <div className="comparison-summary"><Icon name="alert" size={14} />{currentOnly.length} current allow entries were not observed in the reference window. Absence from telemetry is not proof that a permission is unnecessary. Review ownership and business requirements before proposing any change.</div>
              </div>
            )}
          </section>
        </>
      )}
    </main>
  )
}
