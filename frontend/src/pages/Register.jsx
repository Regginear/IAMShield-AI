import { Link } from 'react-router-dom'
import Icon from '../components/Icon'

export default function Register() {
  return (
    <main className="page-shell">
      <section className="panel auth-panel">
        <span className="brand-mark"><Icon name="shield" size={20} /></span>
        <p className="eyebrow">IAMSHIELD AI / RESEARCH PREVIEW</p>
        <h1>Account creation is not available</h1>
        <p>This prototype uses demonstration telemetry and does not create user accounts. Continue to the dashboard to explore the current security workflow.</p>
        <Link className="primary-button" to="/">Open security overview <Icon name="arrow" size={13} /></Link>
      </section>
    </main>
  )
}
