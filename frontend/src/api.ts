export type Outcome =
  | 'VERIFIED'
  | 'PATCH_TESTED_NOT_VERIFIED'
  | 'DIAGNOSED'
  | 'INDETERMINATE'
  | 'ESCALATED'
  | 'FAILED'

export interface IncidentRow {
  id: string
  created_at: string
  updated_at: string
  phase: string
  outcome: Outcome | null
  mode: 'live' | 'deterministic'
  provider: string
  title: string
}

export interface TraceStep {
  n: number
  phase: string
  tool: string
  args: Record<string, unknown>
  rationale: string
  ok: boolean
  output: unknown
}

export interface Assertion {
  name: string
  expected: unknown
  observed: unknown
  passed: boolean
}

export interface Verification {
  outcome?: 'PASS' | 'FAIL' | 'INDETERMINATE'
  reason?: string
  assertions?: Assertion[]
}

export interface Hypothesis {
  id: string
  statement: string
  status: string
  evidence: string
}

export interface PatchAttempt {
  n: number
  edits: Record<string, unknown>[]
  rationale: string
  review?: { allowed: boolean; risk: string; findings: string[]; changed_lines: number }
  diff?: string
  tests?: {
    suite: { passed: boolean; output: string }
    regression_on_unpatched: { passed: boolean; output: string }
  }
  sandbox_verification?: { verification: Verification }
  regression_files?: string[]
  accepted?: boolean
}

export interface TimelineEvent {
  seq: number
  ts: string
  phase: string
  kind: string
  summary: string
  payload: unknown
}

export interface Incident {
  id: string
  phase: string
  outcome: Outcome | null
  mode: 'live' | 'deterministic'
  provider: string
  created_at: string
  running: boolean
  ticket: {
    title: string
    description: string
    severity?: string
    attachments?: { name: string; type: string; bytes: number; text?: string; note?: string }[]
    operator_notes?: string
  }
  faults: Record<string, unknown>
  trace: TraceStep[]
  hypotheses: Hypothesis[]
  diagnosis: {
    root_cause: string
    category: string
    evidence: string[]
    affected_files: string[]
    confidence: number
  } | null
  reproduction: { verification: Verification; replay: Record<string, unknown> } | null
  attempts: PatchAttempt[]
  patch: PatchAttempt | null
  approval: { approver: string; decision: string; reason?: string } | null
  verification: Verification
  report: { mode_label: string; limitations: string[]; usage: Record<string, unknown> } | null
  usage: Record<string, unknown>
  timeline: TimelineEvent[]
}

export interface Scenario {
  family: string
  description: string
  variants: string[]
  heldout_variants: string[]
}

export interface EvalSummary {
  runs: number
  correct_diagnosis_rate: number
  verified_rate: number
  outcome_matches_expected_rate: number
  false_verified: number
  duplicate_charges: number
  mean_tool_calls: number
  mean_duration_s: number
  by_family: Record<string, { runs: number; verified: number; correct_diagnosis: number; expected_outcome: number }>
}

export interface EvalResult {
  created_at: string
  provider: string
  seeds: number[]
  summary: EvalSummary
  rows: {
    family: string
    variant: string
    seed: number
    heldout: boolean
    outcome: string
    expected_outcome: string
    correct_diagnosis: boolean
    tool_calls: number
    duration_s: number
    false_verified: boolean
  }[]
  path: string
}

export interface Stats {
  total: number
  active: number
  awaiting_approval: number
  outcomes: Record<string, number>
  latest_eval: EvalSummary | null
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, init)
  if (!res.ok) {
    let detail = res.statusText
    try {
      detail = (await res.json()).detail ?? detail
    } catch {
      /* not json */
    }
    throw new Error(`${res.status}: ${detail}`)
  }
  return res.json() as Promise<T>
}

const post = <T,>(path: string, body: unknown) =>
  req<T>(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })

export const api = {
  health: () => req<{ status: string; live_model_configured: boolean; version: string }>('/api/health'),
  stats: () => req<Stats>('/api/stats'),
  incidents: () => req<IncidentRow[]>('/api/incidents'),
  incident: (id: string) => req<Incident>(`/api/incidents/${id}`),
  scenarios: () => req<Scenario[]>('/api/scenarios'),
  create: (body: Record<string, unknown>) => post<{ id: string }>('/api/incidents', body),
  run: (id: string) => post<{ started: boolean }>(`/api/incidents/${id}/run`, {}),
  approve: (id: string, approver: string) => post(`/api/incidents/${id}/approve`, { approver }),
  reject: (id: string, approver: string, reason: string) =>
    post(`/api/incidents/${id}/reject`, { approver, reason }),
  upload: (id: string, file: File) => {
    const fd = new FormData()
    fd.append('file', file)
    return req(`/api/incidents/${id}/evidence`, { method: 'POST', body: fd })
  },
  evalRun: (seeds: number[]) => post('/api/eval/run', { seeds, heldout: true }),
  evalResults: () => req<{ state: { running: boolean; error: string | null }; results: EvalResult[] }>(
    '/api/eval/results',
  ),
}
