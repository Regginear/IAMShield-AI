import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import Icon from '../components/Icon'
import { apiRequest } from '../lib/api'
import { policyRiskSummary } from '../lib/policyAnalysis'

const numberFormat = new Intl.NumberFormat()
const riskOrder = { critical: 0, high: 1, medium: 2, low: 3, unknown: 4 }

function Metric({ label, value, detail, icon, tone }) {
  return (
    <article className={`metric ${tone || ''}`}>
      <div className="metric-top"><span className="metric-label">{label}</span><span className="metric-icon"><Icon name={icon} size={15} /></span></div>
      <strong>{value}</strong>
      <div className="metric-foot">{detail}</div>
    </article>
  )
}

function isWildcardPattern(pattern) {
  return pattern.resource === '*' || pattern.action.includes('*')
}

function formatTimestamp(timestamp) {
  if (!timestamp) return 'Timestamp unavailable'
  const date = new Date(timestamp)
  return Number.isNaN(date.getTime()) ? 'Timestamp unavailable' : date.toLocaleString()
}

function RiskDistribution({ counts, total, source, loading }) {
  const sections = [
    { key: 'critical', label: 'Critical', color: '#c64e5b' },
    { key: 'high', label: 'High', color: '#cf8433' },
    { key: 'medium', label: 'Moderate', color: '#d7b34f' },
    { key: 'low', label: 'Scoped', color: '#36977c' },
    { key: 'unknown', label: 'Unclassified', color: '#a3a9b5' },
  ]
  let cursor = 0
  const gradient = sections.map(({ key, color }) => {
    const start = cursor
    cursor += total ? (counts[key] / total) * 100 : 0
    return `${color} ${start}% ${cursor}%`
  }).join(', ')

  return (
    <article className="panel risk-distribution-panel">
      <div className="panel-heading">
        <div><p className="panel-kicker">ACCESS RISK DISTRIBUTION</p><h2>Review signals</h2><span className="panel-subtitle">{source}</span></div>
      </div>
      {total ? (
        <div className="risk-distribution">
          <div className="risk-donut" style={{ background: `conic-gradient(${gradient})` }} role="img" aria-label={`${total} assessed items; ${counts.critical} critical, ${counts.high} high, ${counts.medium} moderate, ${counts.low} scoped, ${counts.unknown} unclassified`}>
            <span><strong>{numberFormat.format(total)}</strong><small>assessed</small></span>
          </div>
          <ul className="risk-legend">
            {sections.map(({ key, label, color }) => (
              <li key={key}><span className="legend-label"><i style={{ backgroundColor: color }} />{label}</span><strong>{numberFormat.format(counts[key])}</strong></li>
            ))}
          </ul>
        </div>
      ) : <div className="table-empty">{loading ? 'Loading risk signals…' : source === 'No live assessment data available' ? 'Risk distribution is unavailable because the API data could not be loaded.' : 'No policy documents or access patterns are available to assess.'}</div>}
    </article>
  )
}

export default function Dashboard() {
  const [policies, setPolicies] = useState([])
  const [patterns, setPatterns] = useState([])
  const [policiesAvailable, setPoliciesAvailable] = useState(null)
  const [patternsAvailable, setPatternsAvailable] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState(null)

  const refreshDashboard = useCallback(async () => {
    setLoading(true)
    setError('')
    const results = await Promise.allSettled([
      apiRequest('/api/policies'),
      apiRequest('/api/access-patterns'),
    ])
    const errors = []

    if (results[0].status === 'fulfilled' && Array.isArray(results[0].value)) {
      setPolicies(results[0].value)
      setPoliciesAvailable(true)
    } else {
      setPoliciesAvailable(false)
      errors.push(results[0].status === 'rejected' ? results[0].reason.message : 'Policy inventory returned an unexpected response.')
    }
    if (results[1].status === 'fulfilled' && Array.isArray(results[1].value)) {
      setPatterns(results[1].value)
      setPatternsAvailable(true)
    } else {
      setPatternsAvailable(false)
      errors.push(results[1].status === 'rejected' ? results[1].reason.message : 'Access telemetry returned an unexpected response.')
    }
    setError(errors.join(' '))
    if (errors.length < 2) setLastUpdated(new Date())
    setLoading(false)
  }, [])

  useEffect(() => {
    refreshDashboard()
  }, [refreshDashboard])

  const policyAssessments = useMemo(() => policies.map((policy) => ({
    policy,
    ...policyRiskSummary(policy.policy_document),
  })), [policies])
  const policyPermissionCount = policyAssessments.reduce((count, item) => count + item.permissions.filter((permission) => permission.effect === 'Allow').length, 0)
  const excessivePermissions = policyAssessments.reduce((count, item) => count + item.excessivePermissions, 0)
  const pendingReviews = policies.filter((policy) => policy.status === 'draft').length
  const riskCounts = useMemo(() => {
    const counts = { critical: 0, high: 0, medium: 0, low: 0, unknown: 0 }
    if (policiesAvailable && policyAssessments.length) {
      policyAssessments.forEach(({ risk }) => { counts[risk] += 1 })
      return { counts, source: 'Saved policies · wildcard/scope heuristics', total: policyAssessments.length }
    }
    if (patternsAvailable) {
      patterns.forEach((pattern) => { counts[isWildcardPattern(pattern) ? 'high' : 'low'] += 1 })
      return { counts, source: policiesAvailable ? 'Observed access patterns · no saved policies' : 'Observed access patterns · policy inventory unavailable', total: patterns.length }
    }
    return { counts, source: 'No live assessment data available', total: 0 }
  }, [patterns, patternsAvailable, policiesAvailable, policyAssessments])
  const riskScore = riskCounts.total
    ? Math.round(((riskCounts.counts.critical * 100 + riskCounts.counts.high * 65 + riskCounts.counts.medium * 35) / riskCounts.total))
    : null
  const patternEvents = patterns.reduce((total, pattern) => total + (Number(pattern.access_count) || 0), 0)
  const riskyPatterns = [...patterns].filter(isWildcardPattern).sort((left, right) => right.access_count - left.access_count)
  const recentActivity = [...patterns].sort((left, right) => new Date(right.last_accessed || 0) - new Date(left.last_accessed || 0)).slice(0, 5)
  const reviewQueue = [...policies]
    .filter((policy) => policy.status === 'draft')
    .sort((left, right) => riskOrder[policyRiskSummary(left.policy_document).risk] - riskOrder[policyRiskSummary(right.policy_document).risk])
    .slice(0, 4)
  const recommendations = [
    ...(policiesAvailable ? policyAssessments.flatMap(({ policy, findings }) => findings.map((finding) => ({ ...finding, policyName: policy.name }))) : []),
    ...(patternsAvailable ? riskyPatterns.map((pattern) => ({
      id: `pattern-${pattern.id}`,
      title: pattern.resource === '*' ? 'Review unrestricted resource observation' : 'Review wildcard action observation',
      description: `${pattern.action} on ${pattern.resource}`,
      recommendation: 'Confirm the workload need and scope the resulting policy explicitly.',
    })) : []),
  ].slice(0, 3)
  const scoreTone = riskScore === null ? '' : riskScore >= 65 ? 'danger' : riskScore >= 30 ? 'warning' : 'success'

  return (
    <main className="page-shell">
      <section className="page-heading">
        <div>
          <p className="eyebrow">IDENTITY SECURITY / OVERVIEW</p>
          <h1>Security overview</h1>
          <p>Review policy exposure, observed access activity, and drafts awaiting human review.</p>
        </div>
        <div className="heading-actions">
          <button className="secondary-button" onClick={refreshDashboard} disabled={loading}><Icon name="refresh" size={14} />{loading ? 'Refreshing' : 'Refresh'}</button>
          <Link className="primary-button" to="/synthesis"><Icon name="spark" size={14} />Analyze access</Link>
        </div>
      </section>

      <div className="notice demo-notice" role="note"><Icon name="database" size={15} /><span><strong>Research preview.</strong> Data below comes from the connected API; this backend may include seeded demonstration access patterns. Verify findings against your cloud provider before acting.</span></div>
      {error && <div className="notice error" role="alert"><Icon name="alert" size={15} />{error} Some dashboard sections may be unavailable.</div>}

      <section className="metrics-grid" aria-label="Identity security key performance indicators">
        <Metric label="IAM policies" value={policiesAvailable ? numberFormat.format(policies.length) : loading && policiesAvailable === null ? '…' : '—'} detail={policiesAvailable ? `${numberFormat.format(policyPermissionCount)} allow grants assessed` : 'Policy inventory unavailable'} icon="file" />
        <Metric label="Excessive grants flagged" value={policiesAvailable ? numberFormat.format(excessivePermissions) : loading && policiesAvailable === null ? '…' : '—'} detail={policiesAvailable ? 'Wildcard grants in saved policy documents' : 'Policy inventory unavailable'} icon="alert" tone={excessivePermissions ? 'warning' : 'success'} />
        <Metric label="Heuristic risk score" value={riskScore === null ? loading ? '…' : '—' : `${riskScore}/100`} detail="Review indicator · not a provider score" icon="shield" tone={scoreTone} />
        <Metric label="Pending policy reviews" value={policiesAvailable ? numberFormat.format(pendingReviews) : loading && policiesAvailable === null ? '…' : '—'} detail={policiesAvailable ? 'Saved drafts · no approval workflow configured' : 'Policy inventory unavailable'} icon="clock" tone={pendingReviews ? 'warning' : ''} />
      </section>

      <section className="dashboard-grid overview-analytics">
        <RiskDistribution counts={riskCounts.counts} total={riskCounts.total} source={riskCounts.source} loading={loading} />
        <article className="panel posture-panel">
          <div className="panel-heading"><div><p className="panel-kicker">OBSERVED ACCESS</p><h2>Telemetry snapshot</h2><span className="panel-subtitle">{lastUpdated ? `Retrieved ${lastUpdated.toLocaleTimeString()}` : 'Live API records'}</span></div><span className="status-pill"><span className="status-orb" />API data</span></div>
          <div className="telemetry-total"><strong>{patternsAvailable ? numberFormat.format(patternEvents) : loading && patternsAvailable === null ? '…' : '—'}</strong><span>access events represented by current records</span></div>
          <div className="posture-stats">
            <div className="posture-row"><span>Observed access patterns</span><strong>{patternsAvailable ? numberFormat.format(patterns.length) : '—'}</strong></div>
            <div className="posture-row"><span>Wildcard-pattern signals</span><strong className={riskyPatterns.length ? 'risk-text' : ''}>{patternsAvailable ? numberFormat.format(riskyPatterns.length) : '—'}</strong></div>
          </div>
          <p className="chart-note">Pattern counts are observations, not a complete cloud audit trail.</p>
        </article>
      </section>

      <section className="dashboard-grid review-grid">
        <article className="panel">
          <div className="panel-heading"><div><p className="panel-kicker">RECENT SECURITY ACTIVITY</p><h2>Latest observed access</h2><span className="panel-subtitle">Sorted by the API record’s last-accessed timestamp</span></div><Link className="table-action" to="/synthesis">Analyze patterns <Icon name="arrow" size={12} /></Link></div>
          <div className="table-wrap">
            <table><thead><tr><th>Resource</th><th>Action</th><th>Last observed</th><th>Events</th><th>Signal</th></tr></thead>
              <tbody>
                {recentActivity.map((pattern) => (
                  <tr key={pattern.id}><td className="mono" title={pattern.resource}>{pattern.resource}</td><td>{pattern.action}</td><td>{formatTimestamp(pattern.last_accessed)}</td><td>{numberFormat.format(pattern.access_count)}</td><td>{isWildcardPattern(pattern) ? <span className="risk-tag">Review</span> : <span className="safe-tag">Scoped</span>}</td></tr>
                ))}
                {!recentActivity.length && <tr><td colSpan="5" className="table-empty">{patternsAvailable === false ? 'Access records could not be loaded.' : loading ? 'Loading access records…' : 'No live access records are available.'}</td></tr>}
              </tbody>
            </table>
          </div>
        </article>

        <article className="panel">
          <div className="panel-heading"><div><p className="panel-kicker">POLICY REVIEW QUEUE</p><h2>Drafts awaiting review</h2></div><Link className="table-action" to="/policies">View inventory <Icon name="arrow" size={12} /></Link></div>
          <div className="review-queue">
            {reviewQueue.map((policy) => {
              const risk = policyRiskSummary(policy.policy_document).risk
              return <Link className="queue-item" to={`/policies/${policy.id}`} key={policy.id}><span className="queue-icon"><Icon name="file" size={14} /></span><span className="queue-copy"><strong>{policy.name}</strong><small>{policy.resource_type || 'Provider not specified'} · Draft</small></span><span className={`risk-tag ${risk === 'critical' ? 'critical' : ''}`}>{risk === 'unknown' ? 'Unassessed' : risk}</span><Icon name="chevron" size={14} /></Link>
            })}
            {!reviewQueue.length && <div className="table-empty">{policiesAvailable === false ? 'Policy review queue could not be loaded.' : loading ? 'Loading policy reviews…' : 'No draft policies are awaiting review.'}</div>}
          </div>
          <p className="review-note">Review queue reflects draft status only; the API does not currently expose approvals.</p>
        </article>
      </section>

      <section className="panel recommendations-panel">
        <div className="panel-heading"><div><p className="panel-kicker">RECOMMENDED ACTIONS</p><h2>Risk signals to investigate</h2></div><span className="neutral-tag">Heuristic findings · verify before changes</span></div>
        <div className="recommendation-list">
          {recommendations.map((item) => <article className="recommendation-item" key={item.id}><span className="finding-icon"><Icon name="alert" size={14} /></span><div><strong>{item.title}</strong><p>{item.policyName ? `${item.policyName}: ` : ''}{item.description}</p><small>{item.recommendation}</small></div></article>)}
          {!recommendations.length && <div className="table-empty">{loading ? 'Reviewing current API data…' : policiesAvailable === false && patternsAvailable === false ? 'No findings can be calculated because the API data is unavailable.' : policiesAvailable === false ? 'No wildcard findings in available access patterns. Saved policy documents could not be assessed.' : patternsAvailable === false ? 'No policy wildcard findings detected. Access telemetry could not be assessed.' : 'No wildcard findings in the available records. This is not a guarantee that all permissions are safe.'}</div>}
        </div>
      </section>
      <footer className="data-footnote">{lastUpdated ? `API data refreshed ${lastUpdated.toLocaleString()}` : 'Waiting for API data'} <span>·</span> Risk classifications are frontend heuristics, not a cloud-provider policy simulation.</footer>
    </main>
  )
}
