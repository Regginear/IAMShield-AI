export function policyStatements(policyDocument) {
  const statements = policyDocument?.Statement
  if (Array.isArray(statements)) return statements.filter((statement) => statement && typeof statement === 'object')
  return statements && typeof statements === 'object' ? [statements] : []
}

function asValues(value) {
  if (typeof value === 'string') return [value]
  return Array.isArray(value) ? value.filter((item) => typeof item === 'string') : []
}

export function policyPermissions(policyDocument) {
  return policyStatements(policyDocument).flatMap((statement) => {
    const actions = asValues(statement.Action)
    const excludedActions = asValues(statement.NotAction)
    const resources = asValues(statement.Resource)
    const excludedResources = asValues(statement.NotResource)
    const representedActions = actions.length ? actions : excludedActions.map((action) => `NotAction: ${action}`)
    const representedResources = resources.length ? resources : excludedResources.map((resource) => `NotResource: ${resource}`)
    if (!representedActions.length || !representedResources.length) {
      return [{ effect: statement.Effect || 'Unknown', action: representedActions.join(', ') || 'Not specified', resource: representedResources.join(', ') || 'Not specified' }]
    }
    return representedActions.flatMap((action) => representedResources.map((resource) => ({
      effect: statement.Effect || 'Unknown',
      action,
      resource,
    })))
  })
}

export function policyFindings(policyDocument) {
  const findings = []
  policyStatements(policyDocument).forEach((statement, index) => {
    if (statement.Effect !== 'Allow') return
    const actions = asValues(statement.Action)
    const resources = asValues(statement.Resource)

    if (statement.NotAction !== undefined) {
      findings.push({
        id: `${index}-not-action`,
        severity: 'critical',
        title: 'Allow statement uses NotAction',
        description: 'An Allow statement with NotAction can grant every action except the listed exclusions.',
        recommendation: 'Replace NotAction with a reviewed list of explicitly allowed actions.',
      })
    }
    if (actions.some((action) => action === '*')) {
      findings.push({
        id: `${index}-all-actions`,
        severity: 'critical',
        title: 'All actions are allowed',
        description: 'This statement grants every action to its matching resources.',
        recommendation: 'Replace the action wildcard with only the operations required by the workload.',
      })
    } else if (actions.some((action) => action.endsWith(':*'))) {
      findings.push({
        id: `${index}-service-actions`,
        severity: 'high',
        title: 'Service-wide action wildcard',
        description: `This statement includes a service-wide action pattern (${actions.filter((action) => action.endsWith(':*')).join(', ')}).`,
        recommendation: 'Review observed usage and replace service-wide patterns with specific actions.',
      })
    } else if (actions.some((action) => action.includes('*'))) {
      findings.push({
        id: `${index}-pattern-actions`,
        severity: 'medium',
        title: 'Wildcard action pattern',
        description: 'This statement uses a partial wildcard in an action name.',
        recommendation: 'Replace the action pattern with the specific operations required by the workload.',
      })
    }

    if (resources.includes('*')) {
      findings.push({
        id: `${index}-all-resources`,
        severity: 'high',
        title: 'Unrestricted resource scope',
        description: 'This statement is not limited to a specific resource.',
        recommendation: 'Scope the grant to the resource ARNs required by the workload.',
      })
    }
    if (statement.NotResource !== undefined) {
      findings.push({
        id: `${index}-not-resource`,
        severity: 'high',
        title: 'Allow statement uses NotResource',
        description: 'This statement applies broadly to resources outside the listed exclusions.',
        recommendation: 'Prefer explicit Resource ARNs for the resources required by the workload.',
      })
    }
  })
  return findings
}

export function policyRisk(policyDocument) {
  const findings = policyFindings(policyDocument)
  if (findings.some((finding) => finding.severity === 'critical')) return 'critical'
  if (findings.some((finding) => finding.severity === 'high')) return 'high'
  if (findings.some((finding) => finding.severity === 'medium')) return 'medium'
  if (!policyStatements(policyDocument).length) return 'unknown'
  return 'low'
}

export function cloudProvider(policy) {
  const text = `${policy?.resource_type || ''} ${JSON.stringify(policy?.policy_document || {})}`.toLowerCase()
  if (text.includes('arn:aws:') || text.includes('aws iam') || text.includes('aws')) return 'AWS'
  if (text.includes('projects/') || text.includes('google') || text.includes('gcp')) return 'GCP'
  if (text.includes('azure') || text.includes('microsoft')) return 'Azure'
  return 'Not specified'
}

export function policyRiskSummary(policyDocument) {
  const permissions = policyPermissions(policyDocument)
  const findings = policyFindings(policyDocument)
  return {
    permissions,
    findings,
    risk: policyRisk(policyDocument),
    excessivePermissions: permissions.filter((permission) => {
      if (permission.effect !== 'Allow') return false
      return permission.action.includes('*')
        || permission.action.startsWith('NotAction:')
        || permission.resource === '*'
        || permission.resource.startsWith('NotResource:')
    }).length,
  }
}
