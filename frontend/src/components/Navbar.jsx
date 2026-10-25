import { NavLink } from 'react-router-dom'

export default function Navbar() {
  return <header className="navbar"><NavLink className="brand" to="/">IAM<span>Shield</span><small>AI</small></NavLink><nav><NavLink to="/">Overview</NavLink><NavLink to="/synthesis">Synthesis</NavLink><NavLink to="/policies">Policies</NavLink></nav><span className="nav-status">● Prototype mode</span></header>
}
