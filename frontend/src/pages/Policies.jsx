import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import Icon from '../components/Icon'
import { apiRequest } from '../lib/api'
import { cloudProvider, policyRiskSummary } from '../lib/policyAnalysis'

const pageSize = 8
const severityRank = { critical: 0, high: 1, medium: 2, low: 3, unknown: 4 }

function policyUpdatedAt(policy) {
  return policy.updated_at || policy.created_at || null
}

function formatDate(value) {
  if (!value) return 'Not provided'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? 'Not provided' : date.toLocaleDateString()
}

function RiskBadge({ risk }) {
  const className = risk === 'critical' ? 'risk-tag critical' : risk === 'high' || risk === 'medium' ? 'risk-tag' : risk === 'low' ? 'safe-tag' : 'neutral-tag'
  return <span className={className}>{risk === 'unknown' ? 'Not assessed' : risk}</span>
}

export default function Policies() {
  const [policies, setPolicies] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [riskFilter, setRiskFilter] = useState('all')
  const [sortBy, setSortBy] = useState('updated')
  const [page, setPage] = useState(1)

  useEffect(() => {
    apiRequest('/api/policies')
      .then((data) => {
        if (!Array.isArray(data)) throw new Error('The policies endpoint returned an unexpected response.')
        setPolicies(data)
      })
      .catch((requestError) => setError(requestError.message))
      .finally(() => setLoading(false))
  }, [])

  const filteredPolicies = useMemo(() => {
    const searchTerm = search.trim().toLowerCase()
    return policies
      .map((policy) => ({ policy, analysis: policyRiskSummary(policy.policy_document), provider: cloudProvider(policy) }))
      .filter(({ policy, analysis, provider }) => {
        const searchable = `${policy.name || ''} ${provider} ${policy.resource_type || ''} ${policy.policy_type || ''}`.toLowerCase()
        return (!searchTerm || searchable.includes(searchTerm))
          && (statusFilter === 'all' || policy.status === statusFilter)
          && (riskFilter === 'all' || analysis.risk === riskFilter)
      })
      .sort((left, right) => {
        if (sortBy === 'name') return (left.policy.name || '').localeCompare(right.policy.name || '')
        if (sortBy === 'risk') return severityRank[left.analysis.risk] - severityRank[right.analysis.risk]
        if (sortBy === 'permissions') return right.analysis.permissions.length - left.analysis.permissions.length
        const leftTime = policyUpdatedAt(left.policy) ? new Date(policyUpdatedAt(left.policy)).getTime() : 0
        const rightTime = policyUpdatedAt(right.policy) ? new Date(policyUpdatedAt(right.policy)).getTime() : 0
        return rightTime - leftTime
      })
  }, [policies, riskFilter, search, sortBy, statusFilter])

  const pageCount = Math.max(1, Math.ceil(filteredPolicies.length / pageSize))
  const visiblePolicies = filteredPolicies.slice((page - 1) * pageSize, page * pageSize)

  function updateFilter(setter, value) {
    setter(value)
    setPage(1)
  }

  return (
    <main className="page-shell">
      <section className="page-heading">
        <div><p className="eyebrow">IDENTITY GOVERNANCE / POLICIES</p><h1>Policy inventory</h1><p>Search, assess, and review IAM policy documents. Risk labels flag broad grants for investigation; they are not provider simulation results.</p></div>
        <Link className="primary-button" to="/synthesis"><Icon name="plus" size={14} />Create policy draft</Link>
      </section>
      {error && <div className="notice error" role="alert"><Icon name="alert" size={15} />{error}</div>}

      <section className="panel page-panel">
        <div className="panel-heading">
          <div><p className="panel-kicker">POLICY REGISTER</p><h2>Saved policies</h2><span className="panel-subtitle">{loading ? 'Loading inventory…' : `${filteredPolicies.length} of ${policies.length} policies`}</span></div>
          <span className="neutral-tag"><Icon name="lock" size={12} />Review before deployment</span>
        </div>
        <div className="filter-row">
          <label className="search-field-wrap"><span className="sr-only">Search policies</span><Icon name="search" size={14} /><input className="search-field" value={search} onChange={(event) => updateFilter(setSearch, event.target.value)} placeholder="Search by name, provider, or resource" /></label>
          <label className="filter-select-wrap"><Icon name="filter" size={14} /><span className="sr-only">Filter by status</span><select className="filter-select" value={statusFilter} onChange={(event) => updateFilter(setStatusFilter, event.target.value)}><option value="all">All statuses</option><option value="draft">Draft</option><option value="active">Active</option><option value="inactive">Inactive</option><option value="archived">Archived</option></select></label>
          <label className="sr-only" htmlFor="risk-filter">Filter by risk</label><select id="risk-filter" className="filter-select" value={riskFilter} onChange={(event) => updateFilter(setRiskFilter, event.target.value)}><option value="all">All risk levels</option><option value="critical">Critical</option><option value="high">High</option><option value="medium">Moderate</option><option value="low">Scoped</option><option value="unknown">Not assessed</option></select>
          <label className="sr-only" htmlFor="policy-sort">Sort policies</label><select id="policy-sort" className="filter-select sort-select" value={sortBy} onChange={(event) => updateFilter(setSortBy, event.target.value)}><option value="updated">Recently updated</option><option value="name">Name A–Z</option><option value="risk">Highest risk</option><option value="permissions">Most permissions</option></select>
        </div>
        <div className="table-wrap inventory-table">
          <table><thead><tr><th>Policy name</th><th>Provider</th><th>Risk level</th><th>Permissions</th><th>Last updated</th><th>Status</th><th /></tr></thead>
            <tbody>
              {loading && <tr><td colSpan="7" className="table-empty">Loading policies…</td></tr>}
              {!loading && visiblePolicies.map(({ policy, analysis, provider }) => (
                <tr key={policy.id}>
                  <td><div className="policy-name-cell"><span className="policy-file-icon"><Icon name="file" size={15} /></span><span><strong>{policy.name}</strong><small>Policy #{policy.id} · {policy.policy_type || 'Type unspecified'}</small></span></div></td>
                  <td>{provider}</td><td><RiskBadge risk={analysis.risk} /></td><td>{analysis.permissions.length}</td>
                  <td>{formatDate(policyUpdatedAt(policy))}</td>
                  <td><span className={policy.status === 'active' ? 'safe-tag' : policy.status === 'draft' ? 'neutral-tag' : 'risk-tag'}>{policy.status || 'Unknown'}</span></td>
                  <td><Link className="table-action" to={`/policies/${policy.id}`}>Review <Icon name="chevron" size={12} /></Link></td>
                </tr>
              ))}
              {!loading && !error && filteredPolicies.length === 0 && <tr><td colSpan="7" className="table-empty">{policies.length ? 'No policies match these filters.' : 'No saved policies yet. Synthesize observed access to create a reviewable draft.'}</td></tr>}
              {!loading && error && !policies.length && <tr><td colSpan="7" className="table-empty">Policy inventory could not be loaded. Check the API connection and retry.</td></tr>}
            </tbody>
          </table>
        </div>
        <div className="pagination-row">
          <span>{filteredPolicies.length ? `Showing ${(page - 1) * pageSize + 1}–${Math.min(page * pageSize, filteredPolicies.length)} of ${filteredPolicies.length}` : 'No results'}</span>
          <div><button className="secondary-button" onClick={() => setPage((current) => Math.max(1, current - 1))} disabled={page <= 1 || loading}>Previous</button><span className="page-count">Page {page} of {pageCount}</span><button className="secondary-button" onClick={() => setPage((current) => Math.min(pageCount, current + 1))} disabled={page >= pageCount || loading}>Next</button></div>
        </div>
      </section>
      <p className="data-footnote">Provider, permission count, and risk level are derived from the saved policy document. The API currently omits update timestamps, so those are shown as unavailable.</p>
    </main>
  )
}
