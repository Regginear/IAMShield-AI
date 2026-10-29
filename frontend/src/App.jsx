import { BrowserRouter as Router, Link, Route, Routes, useLocation } from 'react-router-dom'
import { useEffect } from 'react'
import './App.css'
import Navbar from './components/Navbar'
import Icon from './components/Icon'
import Dashboard from './pages/Dashboard'
import Policies from './pages/Policies'
import PolicyDetail from './pages/PolicyDetail'
import PolicySynthesis from './pages/PolicySynthesis'
import Login from './pages/Login'
import Register from './pages/Register'

const routeTitles = {
  '/': 'Security overview',
  '/synthesis': 'Policy synthesis',
  '/policies': 'Policy inventory',
  '/login': 'Sign in',
  '/register': 'Create account',
}

function ApplicationShell() {
  const { pathname } = useLocation()
  const isStandaloneRoute = pathname === '/login' || pathname === '/register'
  const pageTitle = routeTitles[pathname] || (pathname.startsWith('/policies/') ? 'Policy review' : 'Security overview')

  useEffect(() => {
    document.title = `${pageTitle} · IAMShield AI`
  }, [pageTitle])

  if (isStandaloneRoute) {
    return (
      <main className="standalone-shell">
        <header className="standalone-header">
          <Link className="brand" to="/" aria-label="IAMShield AI home"><span className="brand-mark"><Icon name="shield" size={20} /></span><span className="brand-name">IAM<span>Shield</span></span><small>AI</small></Link>
          <span className="environment-tag">RESEARCH PREVIEW</span>
        </header>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
        </Routes>
      </main>
    )
  }

  return (
    <div className="app-shell">
      <Navbar />
      <div className="app-main">
        <header className="topbar">
          <div className="breadcrumb"><span>Workspace</span><Icon name="chevron" size={13} /><strong>{pageTitle}</strong></div>
          <div className="topbar-right"><span className="environment-tag">RESEARCH PREVIEW</span><span className="avatar" aria-label="Demo workspace">IA</span></div>
        </header>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/policies" element={<Policies />} />
          <Route path="/policies/:id" element={<PolicyDetail />} />
          <Route path="/synthesis" element={<PolicySynthesis />} />
          <Route path="*" element={<main className="page-shell"><section className="panel not-found"><Icon name="shield" size={24} /><h1>Page not found</h1><p>This workspace route does not exist.</p><Link className="primary-button" to="/">Return to overview</Link></section></main>} />
        </Routes>
      </div>
    </div>
  )
}

function App() {
  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <ApplicationShell />
    </Router>
  )
}

export default App
