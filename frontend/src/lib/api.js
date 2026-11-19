export async function apiRequest(path, options) {
  const token = localStorage.getItem('iamshield_token')
  const headers = new Headers(options?.headers || {})
  if (token) headers.set('Authorization', `Bearer ${token}`)
  const response = await fetch(path, { ...options, headers })
  const contentType = response.headers.get('content-type') || ''
  const data = contentType.includes('application/json')
    ? await response.json()
    : await response.text()

  if (!response.ok) {
    const detail = typeof data === 'object' && data !== null ? data.detail : data
    const message = Array.isArray(detail)
      ? detail.map((issue) => typeof issue === 'string' ? issue : issue?.msg || JSON.stringify(issue)).join('; ')
      : typeof detail === 'string' ? detail : detail ? JSON.stringify(detail) : `Request failed with status ${response.status}`
    throw new Error(message)
  }

  if (!contentType.includes('application/json')) {
    throw new Error('The API returned an unexpected response.')
  }

  return data
}

export function saveToken(token) {
  localStorage.setItem('iamshield_token', token)
}

export function clearToken() {
  localStorage.removeItem('iamshield_token')
}

export function isAuthenticated() {
  return Boolean(localStorage.getItem('iamshield_token'))
}
