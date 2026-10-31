import { useEffect, useRef, useState } from 'react'

/** Poll an async loader every `ms` until `done(data)` returns true; `reload()` restarts polling. */
export function usePoll<T>(load: () => Promise<T>, ms: number, deps: unknown[], done?: (d: T) => boolean) {
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [tick, setTick] = useState(0)
  const loadRef = useRef(load)
  const doneRef = useRef(done)
  useEffect(() => {
    loadRef.current = load
    doneRef.current = done
  })
  useEffect(() => {
    let alive = true
    let timer: number | undefined
    const run = async () => {
      let finished = false
      try {
        const d = await loadRef.current()
        if (!alive) return
        setData(d)
        setError(null)
        finished = doneRef.current?.(d) ?? false
      } catch (e) {
        if (alive) setError(String((e as Error).message ?? e))
      }
      if (alive && !finished) timer = window.setTimeout(run, ms)
    }
    run()
    return () => {
      alive = false
      window.clearTimeout(timer)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...deps, tick])
  return { data, error, reload: () => setTick((t) => t + 1) }
}

export function fmt(v: unknown): string {
  if (v === null || v === undefined) return '—'
  return typeof v === 'string' ? v : JSON.stringify(v)
}
