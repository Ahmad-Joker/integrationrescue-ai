import type { Outcome } from './api'

const OUTCOME_CLASS: Record<string, string> = {
  VERIFIED: 'b-ok',
  NO_ACTION_NEEDED: 'b-ok',
  PATCH_TESTED_NOT_VERIFIED: 'b-info',
  DIAGNOSED: 'b-accent',
  INDETERMINATE: 'b-warn',
  ESCALATED: 'b-warn',
  FAILED: 'b-bad',
  PASS: 'b-ok',
  FAIL: 'b-bad',
}

export function OutcomeBadge({ outcome }: { outcome: Outcome | string | null | undefined }) {
  if (!outcome) return <span className="badge">—</span>
  return <span className={`badge ${OUTCOME_CLASS[outcome] ?? ''}`}>{outcome.replaceAll('_', ' ')}</span>
}

export function PhaseBadge({ phase, running }: { phase: string; running?: boolean }) {
  const cls = phase === 'done' ? '' : phase === 'awaiting_approval' ? 'b-warn' : 'b-accent'
  return (
    <span className={`badge ${cls}`}>
      {running ? '● ' : ''}
      {phase.replaceAll('_', ' ')}
    </span>
  )
}

export function ModeBanner({ mode, provider }: { mode: string; provider: string }) {
  return mode === 'live' ? (
    <div className="mode-banner mode-live">
      <strong>LIVE AI AGENT</strong> Decisions made by a live model ({provider}).
    </div>
  ) : (
    <div className="mode-banner mode-det">
      <strong>DETERMINISTIC MODE</strong> Decisions made by a rule-based baseline ({provider}), not an LLM. Tool
      execution, sandboxing and verification are real.
    </div>
  )
}

const ERROR_TEXT: Record<string, string> = {
  infrastructure: 'The live model service was unavailable (quota or network). This is an infrastructure failure, not an agent decision.',
  budget: 'The agent hit its model-call budget before finishing.',
  model: 'The model returned an unusable answer (for example a refusal).',
}

export function ProviderErrorBanner({ error }: { error: { kind: string; message: string } }) {
  return (
    <div className="mode-banner mode-err" role="alert">
      <strong>MODEL UNAVAILABLE</strong>
      <span>
        {ERROR_TEXT[error.kind] ?? ERROR_TEXT.model} No repair was claimed. <span className="mono">{error.message}</span>
      </span>
    </div>
  )
}

export function Diff({ text }: { text: string }) {
  return (
    <pre className="diff" aria-label="patch diff">
      {text.split('\n').map((line, i) => {
        const cls = line.startsWith('+') && !line.startsWith('+++') ? 'add'
          : line.startsWith('-') && !line.startsWith('---') ? 'del'
          : line.startsWith('@@') ? 'hunk' : ''
        return (
          <div key={i} className={cls}>
            {line || ' '}
          </div>
        )
      })}
    </pre>
  )
}
