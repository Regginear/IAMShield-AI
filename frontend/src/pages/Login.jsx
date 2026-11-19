import { Link, useNavigate } from 'react-router-dom'
import Icon from '../components/Icon'
import { apiRequest, saveToken } from '../lib/api'
import { useState } from 'react'

export default function Login() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ username: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function submit(event) {
    event.preventDefault()
    setLoading(true)
    setError('')
    try {
      const data = await apiRequest('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })
      saveToken(data.access_token)
      navigate('/')
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="page-shell">
      <section className="panel auth-panel">
        <span className="brand-mark"><Icon name="shield" size={20} /></span>
        <p className="eyebrow">SECURE WORKSPACE</p>
        <h1>Sign in to review policies</h1>
        <p>Use your IAMShield workspace account to save, approve, reject, and audit policy decisions.</p>
        {error && <div className="notice error">{error}</div>}
        <form className="auth-form" onSubmit={submit}>
          <label>Username<input required value={form.username} onChange={(event) => setForm({ ...form, username: event.target.value })} /></label>
          <label>Password<input required type="password" value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} /></label>
          <button className="primary-button" disabled={loading}>{loading ? 'Signing in...' : 'Sign in'} <Icon name="arrow" size={13} /></button>
        </form>
        <p className="auth-link">New workspace? <Link to="/register">Create an account</Link></p>
      </section>
    </main>
  )
}
