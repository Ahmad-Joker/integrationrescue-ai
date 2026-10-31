import { useEffect, useState } from 'react'
import { api } from './api'
import type { Incident, Scenario } from './api'
import type { Verification } from './api'
import { fmt, usePoll } from './hooks'
import { Diff, ModeBanner, OutcomeBadge, PhaseBadge } from './ui'

const go = (path: string) => {
  window.location.hash = path
}

// ----------------------------------------------------------------- Dashboard
export function Dashboard() {
  const stats = usePoll(api.stats, 3000, [])
  const list = usePoll(api.incidents, 3000, [])
  const s = stats.data
  const o = s?.outcomes ?? {}
  const cards: [string, number | string][] = [
    ['Total incidents', s?.total ?? '—'],
    ['Active investigations', s?.active ?? '—'],
    ['Awaiting approval', s?.awaiting_approval ?? '—'],
    ['Verified recoveries', o.VERIFIED ?? 0],
    ['Diagnosed only', o.DIAGNOSED ?? 0],
    ['Indeterminate', o.INDETERMINATE ?? 0],
    ['Escalated', o.ESCALATED ?? 0],
  ]
  const ev = s?.latest_eval
  return (
    <>
      <h1>Dashboard</h1>
      <p className="sub">Counts come from the incident store; evaluation figures from the latest recorded suite run.</p>
      {stats.error && <div className="err">Backend unreachable: {stats.error}</div>}
      <div className="grid cards">
        {cards.map(([k, v]) => (
          <div className="panel stat" key={k}>
            <div className="k">{k}</div>
            <div className="v">{v}</div>
          </div>
        ))}
      </div>
      <div className="grid two">
        <div className="panel">
          <div className="row">
            <h2>Incidents</h2>
            <span className="spacer" />
            <button className="primary" onClick={() => go('/new')}>
              New incident
            </button>
          </div>
          {list.data && list.data.length === 0 && <div className="empty">No incidents yet.</div>}
          {list.data && list.data.length > 0 && (
            <table>
              <thead>
                <tr>
                  <th>Incident</th>
                  <th>Phase</th>
                  <th>Outcome</th>
                  <th className="hide-sm">Mode</th>
                </tr>
              </thead>
              <tbody>
                {list.data.slice(0, 25).map((r) => (
                  <tr key={r.id} className="click" onClick={() => go(`/incident/${r.id}`)}>
                    <td>
                      <div>{r.title}</div>
                      <div className="mono muted">{r.id}</div>
                    </td>
                    <td>
                      <PhaseBadge phase={r.phase} />
                    </td>
                    <td>
                      <OutcomeBadge outcome={r.phase === 'done' ? r.outcome : null} />
                    </td>
                    <td className="hide-sm">
                      <span className={`badge ${r.mode === 'live' ? 'b-ok' : 'b-warn'}`}>{r.mode}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
        <div className="panel">
          <h2>Latest evaluation</h2>
          {!ev && <div className="empty">No evaluation recorded. Run one in the Evaluation lab.</div>}
          {ev && (
            <div className="kv">
              <span className="k">Runs</span>
              <span>{ev.runs}</span>
              <span className="k">Correct diagnosis</span>
              <span>{(ev.correct_diagnosis_rate * 100).toFixed(0)}%</span>
              <span className="k">Verified recovery</span>
              <span>{(ev.verified_rate * 100).toFixed(0)}%</span>
              <span className="k">Expected outcome</span>
              <span>{(ev.outcome_matches_expected_rate * 100).toFixed(0)}%</span>
              <span className="k">False VERIFIED</span>
              <span>{ev.false_verified}</span>
              <span className="k">Duplicate charges</span>
              <span>{ev.duplicate_charges}</span>
            </div>
          )}
        </div>
      </div>
    </>
  )
}

// ------------------------------------------------------------- New incident
const FAULTS: [string, string][] = [
  ['duplicate_delivery', 'Duplicate webhook delivery'],
  ['lost_ack', 'Lost acknowledgement after commit'],
  ['billing_ledger_unavailable', 'Billing ledger unavailable'],
]

export function NewIncident() {
  const [scenarios, setScenarios] = useState<Scenario[]>([])
  const [live, setLive] = useState(false)
  const [family, setFamily] = useState('payment_entitlement')
  const [variant, setVariant] = useState('')
  const [seed, setSeed] = useState(42)
  const [provider, setProvider] = useState('deterministic')
  const [faults, setFaults] = useState<Record<string, boolean>>({})
  const [notes, setNotes] = useState('')
  const [files, setFiles] = useState<File[]>([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.scenarios().then(setScenarios).catch((e) => setError(String(e)))
    api.health().then((h) => setLive(h.live_model_configured)).catch(() => undefined)
  }, [])
  const fam = scenarios.find((s) => s.family === family)
  const variants = fam ? [...fam.variants, ...fam.heldout_variants] : []
  const v = variants.includes(variant) ? variant : (variants[0] ?? '')

  const submit = async () => {
    setBusy(true)
    setError(null)
    try {
      const activeFaults = Object.fromEntries(Object.entries(faults).filter(([, on]) => on))
      const { id } = await api.create({
        family, variant: v, seed, provider, faults: activeFaults, description: notes || null, autorun: false,
      })
      for (const f of files) await api.upload(id, f)
      await api.run(id)
      go(`/incident/${id}`)
    } catch (e) {
      setError(String((e as Error).message ?? e))
      setBusy(false)
    }
  }

  return (
    <>
      <h1>New incident</h1>
      <p className="sub">
        Creates a fresh, isolated simulated environment that reproduces a reported integration failure, then starts
        the investigation. All data is fictional.
      </p>
      <div className="grid two">
        <div className="panel">
          <h2>Environment</h2>
          <label htmlFor="family">Integration environment</label>
          <select id="family" value={family} onChange={(e) => setFamily(e.target.value)}>
            {scenarios.map((s) => (
              <option key={s.family} value={s.family}>
                {s.description}
              </option>
            ))}
          </select>
          <label htmlFor="variant">Scenario variant (operator only; never shown to the agent)</label>
          <select id="variant" value={v} onChange={(e) => setVariant(e.target.value)}>
            {variants.map((x) => (
              <option key={x} value={x}>
                {x}
                {fam?.heldout_variants.includes(x) ? ' (held-out)' : ''}
              </option>
            ))}
          </select>
          <label htmlFor="seed">Seed</label>
          <input id="seed" type="number" value={seed} onChange={(e) => setSeed(Number(e.target.value))} />
          <label htmlFor="provider">Decision maker</label>
          <select id="provider" value={provider} onChange={(e) => setProvider(e.target.value)}>
            <option value="deterministic">Deterministic baseline (offline, no LLM)</option>
            <option value="claude" disabled={!live}>
              Live AI agent (Claude){live ? '' : ' — no API credentials configured'}
            </option>
          </select>
          <h3 style={{ marginTop: 18 }}>Fault injection</h3>
          {FAULTS.map(([k, label]) => (
            <label className="check" key={k}>
              <input
                type="checkbox"
                checked={!!faults[k]}
                onChange={(e) => setFaults({ ...faults, [k]: e.target.checked })}
              />
              {label}
            </label>
          ))}
        </div>
        <div className="panel">
          <h2>Evidence</h2>
          <label htmlFor="notes">Additional description (treated as untrusted)</label>
          <textarea id="notes" value={notes} onChange={(e) => setNotes(e.target.value)} />
          <label htmlFor="files">Logs, JSON or screenshots</label>
          <input
            id="files"
            type="file"
            multiple
            accept=".log,.txt,.json,.png,.jpg,.jpeg"
            onChange={(e) => setFiles(Array.from(e.target.files ?? []))}
          />
          {files.length > 0 && <p className="muted">{files.length} file(s) attached</p>}
          {error && <div className="err">{error}</div>}
          <div className="row" style={{ marginTop: 18 }}>
            <button className="primary" onClick={submit} disabled={busy || !v}>
              {busy ? 'Starting…' : 'Create and investigate'}
            </button>
          </div>
        </div>
      </div>
    </>
  )
}

// --------------------------------------------------------------- Incident
const PIPELINE = [
  ['intake', 'Intake'],
  ['investigate', 'Investigate'],
  ['reproduce', 'Reproduce'],
  ['patch', 'Patch & test'],
  ['awaiting_approval', 'Approval'],
  ['promote', 'Promote'],
  ['verify_live', 'Verify'],
  ['done', 'Report'],
]

type Tab = 'investigation' | 'repair' | 'verification' | 'report'

export function IncidentView({ id }: { id: string }) {
  const [tab, setTab] = useState<Tab>('investigation')
  const { data: inc, error, reload } = usePoll(
    () => api.incident(id), 1500, [id],
    (d) => !d.running && (d.phase === 'done' || d.phase === 'awaiting_approval'),
  )
  if (error && !inc) return <div className="err">{error}</div>
  if (!inc) return <div className="empty">Loading…</div>
  const idx = PIPELINE.findIndex(([p]) => p === inc.phase)

  return (
    <>
      <div className="row">
        <h1>{inc.ticket.title}</h1>
        <span className="spacer" />
        <PhaseBadge phase={inc.phase} running={inc.running} />
        {inc.phase === 'done' && <OutcomeBadge outcome={inc.outcome} />}
      </div>
      <p className="sub mono">{inc.id}</p>
      <ModeBanner mode={inc.mode} provider={inc.provider} />
      <div className="steps" aria-label="pipeline">
        {PIPELINE.map(([p, label], i) => (
          <span key={p} className={`step ${i < idx || inc.phase === 'done' ? 'done' : i === idx ? 'current' : ''}`}>
            {label}
          </span>
        ))}
      </div>
      <div className="tabs" role="tablist">
        {(['investigation', 'repair', 'verification', 'report'] as Tab[]).map((t) => (
          <button key={t} role="tab" className={`tab ${tab === t ? 'active' : ''}`} onClick={() => setTab(t)}>
            {t[0].toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>
      {tab === 'investigation' && <Investigation inc={inc} />}
      {tab === 'repair' && (
        <Repair
          inc={inc}
          onDecision={reload}
        />
      )}
      {tab === 'verification' && <VerificationView inc={inc} />}
      {tab === 'report' && <Report inc={inc} />}
    </>
  )
}

function Investigation({ inc }: { inc: Incident }) {
  return (
    <div className="grid two">
      <div>
        <div className="panel" style={{ marginBottom: 14 }}>
          <h2>Ticket (untrusted input)</h2>
          <p style={{ whiteSpace: 'pre-wrap', margin: 0 }}>{inc.ticket.description}</p>
          {inc.ticket.operator_notes && <p className="muted">Notes: {inc.ticket.operator_notes}</p>}
          {Object.keys(inc.faults).length > 0 && (
            <p>
              <span className="badge b-bad">Fault injection</span> {Object.keys(inc.faults).join(', ')}
            </p>
          )}
          {inc.ticket.attachments?.map((a) => (
            <details key={a.name} className="tool">
              <summary>
                <span className="badge">{a.type}</span> {a.name} <span className="muted">{a.bytes} bytes</span>
              </summary>
              <pre>{a.text ?? a.note}</pre>
            </details>
          ))}
        </div>
        <div className="panel">
          <h2>Tool calls ({inc.trace.length})</h2>
          {inc.trace.length === 0 && <div className="empty">Waiting for the first step…</div>}
          {inc.trace.map((s) => (
            <details key={s.n} className="tool">
              <summary>
                <span className="mono muted">#{s.n}</span>
                <span className={`badge ${s.ok ? 'b-accent' : 'b-bad'}`}>{s.ok ? s.phase : 'denied'}</span>
                <code>{s.tool}</code>
                <span className="why">{s.rationale}</span>
              </summary>
              <pre>{'args: ' + JSON.stringify(s.args, null, 2) + '\n\nresult: ' + JSON.stringify(s.output, null, 2)}</pre>
            </details>
          ))}
        </div>
      </div>
      <div>
        <div className="panel" style={{ marginBottom: 14 }}>
          <h2>Hypotheses</h2>
          {inc.hypotheses.length === 0 && <div className="muted">None recorded yet.</div>}
          {inc.hypotheses.map((h) => (
            <div key={h.id} style={{ marginBottom: 10 }}>
              <div className="row">
                <strong>{h.id}</strong>
                <span
                  className={`badge ${h.status === 'refuted' ? 'b-bad' : h.status === 'open' ? '' : 'b-ok'}`}
                >
                  {h.status}
                </span>
              </div>
              <div>{h.statement}</div>
              <div className="muted">{h.evidence}</div>
            </div>
          ))}
        </div>
        <div className="panel" style={{ marginBottom: 14 }}>
          <h2>Root cause</h2>
          {inc.diagnosis ? (
            <>
              <p style={{ marginTop: 0 }}>{inc.diagnosis.root_cause}</p>
              <div className="kv">
                <span className="k">Category</span>
                <span>{inc.diagnosis.category}</span>
                <span className="k">Files</span>
                <span className="mono">{inc.diagnosis.affected_files.join(', ') || '—'}</span>
                <span className="k">Confidence</span>
                <span>{inc.diagnosis.confidence}</span>
                <span className="k">Reproduced</span>
                <span>
                  {inc.reproduction ? <OutcomeBadge outcome={inc.reproduction.verification.outcome} /> : 'pending'}
                  {inc.reproduction?.verification.outcome === 'FAIL' && ' (failure reproduced in isolation)'}
                </span>
              </div>
            </>
          ) : (
            <div className="muted">Not established yet.</div>
          )}
        </div>
        <div className="panel">
          <h2>Evidence timeline</h2>
          <ul className="tl">
            {inc.timeline.map((e) => (
              <li key={e.seq}>
                <span className="kind">{e.kind}</span>
                <span>{e.summary}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}

function Repair({ inc, onDecision }: { inc: Incident; onDecision: () => void }) {
  const [approver, setApprover] = useState('')
  const [reason, setReason] = useState('')
  const [err, setErr] = useState<string | null>(null)
  const attempts = inc.attempts
  if (attempts.length === 0) return <div className="panel empty">No patch has been proposed yet.</div>
  const decide = async (ok: boolean) => {
    setErr(null)
    try {
      if (ok) await api.approve(inc.id, approver)
      else await api.reject(inc.id, approver, reason || 'rejected by reviewer')
      onDecision()
    } catch (e) {
      setErr(String((e as Error).message ?? e))
    }
  }
  return (
    <div className="grid">
      {inc.phase === 'awaiting_approval' && (
        <div className="panel">
          <h2>Human approval required</h2>
          <p className="muted" style={{ marginTop: 0 }}>
            The patch passed policy review, the test suite, a fail-before/pass-after regression test and sandbox
            replay verification. Approving applies it to the incident environment and redelivers the original
            event (no new charge).
          </p>
          <div className="row">
            <input
              aria-label="approver"
              placeholder="Your name or e-mail"
              value={approver}
              onChange={(e) => setApprover(e.target.value)}
              style={{ maxWidth: 260 }}
            />
            <input
              aria-label="rejection reason"
              placeholder="Reason (if rejecting)"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              style={{ maxWidth: 260 }}
            />
            <button className="primary" disabled={!approver} onClick={() => decide(true)}>
              Approve & promote
            </button>
            <button className="danger" disabled={!approver} onClick={() => decide(false)}>
              Reject
            </button>
          </div>
          {err && <div className="err">{err}</div>}
        </div>
      )}
      {inc.approval && (
        <div className="panel">
          <strong>Decision:</strong> {inc.approval.decision} by {inc.approval.approver}
          {inc.approval.reason ? ` — ${inc.approval.reason}` : ''}
        </div>
      )}
      {attempts.map((a) => (
        <div className="panel" key={a.n}>
          <div className="row">
            <h2>Patch attempt {a.n}</h2>
            <span className="spacer" />
            {a.accepted ? <span className="badge b-ok">accepted</span> : <span className="badge b-bad">rejected</span>}
          </div>
          <p style={{ marginTop: 0 }}>{a.rationale}</p>
          {a.review && (
            <div className="kv" style={{ marginBottom: 12 }}>
              <span className="k">Policy review</span>
              <span>
                {a.review.allowed ? 'allowed' : 'blocked'} · risk <strong>{a.review.risk}</strong>
              </span>
              <span className="k">Findings</span>
              <span>{a.review.findings.join('; ') || '—'}</span>
              {a.tests && (
                <>
                  <span className="k">Test suite</span>
                  <span>
                    <OutcomeBadge outcome={a.tests.suite.passed ? 'PASS' : 'FAIL'} />
                  </span>
                  <span className="k">Regression (unpatched)</span>
                  <span>
                    <OutcomeBadge outcome={a.tests.regression_on_unpatched.passed ? 'PASS' : 'FAIL'} />{' '}
                    <span className="muted">(must fail before the fix)</span>
                  </span>
                </>
              )}
              {a.sandbox_verification && (
                <>
                  <span className="k">Sandbox replay</span>
                  <span>
                    <OutcomeBadge outcome={a.sandbox_verification.verification.outcome} />
                  </span>
                </>
              )}
            </div>
          )}
          {a.diff ? <Diff text={a.diff} /> : <pre>{JSON.stringify(a.edits, null, 2)}</pre>}
          {a.tests && (
            <details className="tool" style={{ marginTop: 10 }}>
              <summary>Test output</summary>
              <pre>{a.tests.suite.output}</pre>
            </details>
          )}
        </div>
      ))}
    </div>
  )
}

function VerificationBlock({ title, v, note }: { title: string; v?: Verification; note: string }) {
  return (
    <div className="panel">
      <div className="row">
        <h2>{title}</h2>
        <span className="spacer" />
        <OutcomeBadge outcome={v?.outcome} />
      </div>
      <p className="muted" style={{ marginTop: 0 }}>{note}</p>
      {v?.reason && <p className="err">{v.reason}</p>}
      {v?.assertions && v.assertions.length > 0 ? (
        <table>
          <thead>
            <tr>
              <th>Assertion</th>
              <th>Expected</th>
              <th>Observed</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {v.assertions.map((a) => (
              <tr key={a.name}>
                <td className="mono">{a.name}</td>
                <td>{fmt(a.expected)}</td>
                <td>{fmt(a.observed)}</td>
                <td>{a.passed ? '✓' : '✗'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        !v?.reason && <div className="muted">Not run yet.</div>
      )}
    </div>
  )
}

function VerificationView({ inc }: { inc: Incident }) {
  const live = inc.verification
  const sandbox = inc.patch?.sandbox_verification?.verification
  const repro = inc.reproduction?.verification
  return (
    <div className="grid">
      <VerificationBlock
        title="Environment after promotion"
        v={live}
        note="Read-only verifier, independent of the agent. Expected state is derived from the billing ledger."
      />
      <VerificationBlock title="Sandbox replay with patch" v={sandbox} note="Cloned environment, patched code, original event." />
      <VerificationBlock title="Reproduction (unpatched)" v={repro} note="Cloned environment, original code: should FAIL." />
    </div>
  )
}

function Report({ inc }: { inc: Incident }) {
  const [md, setMd] = useState<string | null>(null)
  useEffect(() => {
    if (inc.phase !== 'done') return
    fetch(`/api/incidents/${inc.id}/report.md`).then((r) => (r.ok ? r.text() : null)).then(setMd)
  }, [inc.id, inc.phase])
  if (inc.phase !== 'done') return <div className="panel empty">The report is produced when the incident completes.</div>
  return (
    <div className="panel">
      <div className="row">
        <h2>Evidence report</h2>
        <span className="spacer" />
        <a className="btn" href={`/api/incidents/${inc.id}/report.md`} download={`${inc.id}.md`}>
          Download .md
        </a>
      </div>
      {inc.report?.usage && Object.keys(inc.report.usage).length > 0 && (
        <p className="muted">Model usage: {JSON.stringify(inc.report.usage)}</p>
      )}
      <pre style={{ maxHeight: 'none' }}>{md ?? 'Loading…'}</pre>
    </div>
  )
}

// ---------------------------------------------------------------- Eval lab
export function EvalLab() {
  const [running, setRunning] = useState(false)
  const { data, error, reload } = usePoll(api.evalResults, 2500, [])
  const busy = running || !!data?.state.running
  const start = async () => {
    setRunning(true)
    try {
      await api.evalRun([101])
    } finally {
      setRunning(false)
      reload()
    }
  }
  const latest = data?.results[0]
  return (
    <>
      <h1>Evaluation lab</h1>
      <p className="sub">
        Runs every scenario family (including held-out variants) end-to-end and scores against hidden ground truth.
        From the UI only the deterministic suite can be launched so no model credits are spent.
      </p>
      <div className="row" style={{ marginBottom: 16 }}>
        <button className="primary" onClick={start} disabled={busy}>
          {busy ? 'Running suite…' : 'Run deterministic suite'}
        </button>
        {data?.state.error && <span className="err">{data.state.error}</span>}
        {error && <span className="err">{error}</span>}
      </div>
      {!latest && <div className="panel empty">No recorded runs yet.</div>}
      {latest && (
        <div className="grid">
          <div className="panel">
            <h2>
              {latest.provider} · {latest.created_at}
            </h2>
            <div className="grid cards" style={{ marginBottom: 0 }}>
              {[
                ['Runs', latest.summary.runs],
                ['Correct diagnosis', `${(latest.summary.correct_diagnosis_rate * 100).toFixed(0)}%`],
                ['Verified recovery', `${(latest.summary.verified_rate * 100).toFixed(0)}%`],
                ['Expected outcome', `${(latest.summary.outcome_matches_expected_rate * 100).toFixed(0)}%`],
                ['False VERIFIED', latest.summary.false_verified],
                ['Duplicate charges', latest.summary.duplicate_charges],
                ['Mean tool calls', latest.summary.mean_tool_calls],
              ].map(([k, v]) => (
                <div className="stat" key={k}>
                  <div className="k">{k}</div>
                  <div className="v">{v}</div>
                </div>
              ))}
            </div>
          </div>
          <div className="panel" style={{ overflowX: 'auto' }}>
            <table>
              <thead>
                <tr>
                  <th>Family</th>
                  <th>Variant</th>
                  <th>Outcome</th>
                  <th>Expected</th>
                  <th>Diagnosis</th>
                  <th className="hide-sm">Tools</th>
                  <th className="hide-sm">Seconds</th>
                </tr>
              </thead>
              <tbody>
                {latest.rows.map((r, i) => (
                  <tr key={i}>
                    <td>{r.family}</td>
                    <td>
                      {r.variant} {r.heldout && <span className="badge">held-out</span>}
                    </td>
                    <td>
                      <OutcomeBadge outcome={r.outcome} />
                    </td>
                    <td className="muted">{r.expected_outcome}</td>
                    <td>{r.correct_diagnosis ? '✓' : '✗'}</td>
                    <td className="hide-sm">{r.tool_calls}</td>
                    <td className="hide-sm">{r.duration_s}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </>
  )
}
