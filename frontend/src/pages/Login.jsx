import { Link } from 'react-router-dom'
import Icon from '../components/Icon'

export default function Login() {
  return (
    <main className="page-shell">
      <section className="panel auth-panel">
        <span className="brand-mark"><Icon name="shield" size={20} /></span>
        <p className="eyebrow">SECURE WORKSPACE</p>
        <h1>Authentication is not enabled</h1>
        <p>This research preview does not yet provide sign-in or account management. No credentials are collected or stored by this screen.</p>
        <Link className="primary-button" to="/">Continue to security overview <Icon name="arrow" size={13} /></Link>
      </section>
    </main>
  )
}
