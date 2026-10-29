export async function apiRequest(path, options) {
  const response = await fetch(path, options)
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
