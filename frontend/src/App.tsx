import { useEffect, useState } from 'react'
import { Dashboard, EvalLab, IncidentView, NewIncident } from './pages'

function useHash() {
  const [hash, setHash] = useState(() => window.location.hash.slice(1) || '/')
  useEffect(() => {
    const on = () => setHash(window.location.hash.slice(1) || '/')
    window.addEventListener('hashchange', on)
    return () => window.removeEventListener('hashchange', on)
  }, [])
  return hash
}

const NAV: [string, string][] = [
  ['/', 'Dashboard'],
  ['/new', 'New incident'],
  ['/eval', 'Evaluation lab'],
]

export default function App() {
  const route = useHash()
  const incident = route.match(/^\/incident\/([\w-]+)$/)
  let page = <Dashboard />
  if (route === '/new') page = <NewIncident />
  else if (route === '/eval') page = <EvalLab />
  else if (incident) page = <IncidentView id={incident[1]} key={incident[1]} />

  return (
    <div className="shell">
      <nav className="side" aria-label="primary">
        <div className="brand">
          <span className="brand-mark">IR</span> IntegrationRescue
        </div>
        {NAV.map(([href, label]) => (
          <a key={href} href={`#${href}`} className={`nav ${route === href ? 'active' : ''}`}>
            {label}
          </a>
        ))}
        <div className="side-foot">Prototype · simulated environments with fictional data</div>
      </nav>
      <main>{page}</main>
    </div>
  )
}
