import { NavLink, useLocation } from 'react-router-dom'
import { useEffect, useState } from 'react'
import Icon from './Icon'
import { apiRequest } from '../lib/api'

const primaryLinks = [
  { to: '/', label: 'Overview', icon: 'grid', end: true },
  { to: '/synthesis', label: 'Policy synthesis', icon: 'spark' },
  { to: '/policies', label: 'Policy inventory', icon: 'file' },
]

export default function Navbar() {
  const [apiAvailable, setApiAvailable] = useState(null)
  const [menuOpen, setMenuOpen] = useState(false)
  const { pathname } = useLocation()

  useEffect(() => {
    apiRequest('/health')
      .then(() => setApiAvailable(true))
      .catch(() => setApiAvailable(false))
  }, [])

  useEffect(() => {
    setMenuOpen(false)
  }, [pathname])

  useEffect(() => {
    function closeOnEscape(event) {
      if (event.key === 'Escape') setMenuOpen(false)
    }
    window.addEventListener('keydown', closeOnEscape)
    return () => window.removeEventListener('keydown', closeOnEscape)
  }, [])

  return (
    <aside className={`navbar${menuOpen ? ' mobile-open' : ''}`} aria-label="Main navigation">
      <NavLink className="brand" to="/" aria-label="IAMShield AI home">
        <span className="brand-mark"><Icon name="shield" size={20} /></span>
        <span className="brand-name">IAM<span>Shield</span></span>
        <small>AI</small>
      </NavLink>
      <button className="mobile-nav-toggle" type="button" aria-label={menuOpen ? 'Close navigation menu' : 'Open navigation menu'} aria-expanded={menuOpen} aria-controls="primary-navigation" onClick={() => setMenuOpen((isOpen) => !isOpen)}>
        <Icon name={menuOpen ? 'close' : 'menu'} size={18} />
      </button>
      <div className="nav-section-label">WORKSPACE</div>
      <nav id="primary-navigation">
        {primaryLinks.map(({ to, label, icon, end }) => (
          <NavLink key={to} to={to} end={end} onClick={() => setMenuOpen(false)}>
            <span className="nav-icon"><Icon name={icon} size={17} /></span>
            {label}
          </NavLink>
        ))}
      </nav>
      <div className="nav-spacer" />
      <div className="nav-section-label">SYSTEM</div>
      <div className="sidebar-status">
        <span className={`status-orb${apiAvailable === false ? ' offline' : ''}`} />
        <div><strong>{apiAvailable === null ? 'Checking connection' : apiAvailable ? 'Security API connected' : 'Security API unavailable'}</strong><span>{apiAvailable === null ? 'Checking backend status' : apiAvailable ? 'Telemetry endpoints reachable' : 'Check backend service'}</span></div>
      </div>
      <div className="sidebar-footer">IAMShield AI <span aria-hidden="true">·</span> Research preview</div>
    </aside>
  )
}
