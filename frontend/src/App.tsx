import { useEffect, useState } from 'react'
import { access, api } from './api'
import type { Health } from './api'
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

/** Public-demo banner and the judge access-code field (only shown when the server requires a code). */
function DemoBar() {
  const [health, setHealth] = useState<Health | null>(null)
  const [code, setCode] = useState(access.get())
  const [state, setState] = useState<'idle' | 'ok' | 'bad'>(access.get() ? 'ok' : 'idle')
  useEffect(() => {
    api.health().then(setHealth).catch(() => undefined)
  }, [])
  if (!health?.demo_mode && !health?.access_required) return null
  const save = async () => {
    access.set(code.trim())
    try {
      await api.checkAccess()
      setState('ok')
    } catch {
      setState('bad')
    }
  }
  return (
    <div className="demo-banner" role="note">
      <div className="access">
        <strong>Competition demo.</strong>
        <span>Every service, customer and payment here is simulated and fictional. A human approves every repair.</span>
        {health.access_required && state !== 'ok' && (
          <>
            <label htmlFor="access-code" className="sr-only">Access code</label>
            <input
              id="access-code"
              type="password"
              placeholder="Judge access code"
              autoComplete="off"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && save()}
            />
            <button onClick={save}>Unlock</button>
            {state === 'bad' && <span className="err">Code not accepted.</span>}
          </>
        )}
        {health.access_required && state === 'ok' && <span>Access code accepted.</span>}
      </div>
    </div>
  )
}

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
      <main>
        <DemoBar />
        {page}
      </main>
    </div>
  )
}
