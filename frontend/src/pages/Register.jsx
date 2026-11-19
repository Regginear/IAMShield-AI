import { Link, useNavigate } from 'react-router-dom'
import Icon from '../components/Icon'
import { useState } from 'react'
import { apiRequest, saveToken } from '../lib/api'

export default function Register() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ username: '', email: '', full_name: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function submit(event) {
    event.preventDefault()
    setLoading(true)
    setError('')
    try {
      const data = await apiRequest('/api/auth/register', {
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
        <p className="eyebrow">IAMSHIELD AI / WORKSPACE SETUP</p>
        <h1>Create a reviewer account</h1>
        <p>Accounts protect policy decisions and keep an audit trail for this academic MVP.</p>
        {error && <div className="notice error">{error}</div>}
        <form className="auth-form" onSubmit={submit}>
          <label>Username<input required minLength="3" value={form.username} onChange={(event) => setForm({ ...form, username: event.target.value })} /></label>
          <label>Email<input required type="email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} /></label>
          <label>Full name<input value={form.full_name} onChange={(event) => setForm({ ...form, full_name: event.target.value })} /></label>
          <label>Password<input required minLength="8" type="password" placeholder="8+ chars, uppercase and number" value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} /></label>
          <button className="primary-button" disabled={loading}>{loading ? 'Creating...' : 'Create account'} <Icon name="arrow" size={13} /></button>
        </form>
        <p className="auth-link">Already registered? <Link to="/login">Sign in</Link></p>
      </section>
    </main>
  )
}
