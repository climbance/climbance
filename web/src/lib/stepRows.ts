import { useEffect, useRef } from 'react'

// the row `by` away from `at`, held at either end; with no row at, the first or the last
export function stepKey(keys: string[], at: string | null, by: 1 | -1): string | undefined {
  const i = at === null ? -1 : keys.indexOf(at)
  if (i < 0) return by === 1 ? keys[0] : keys[keys.length - 1]
  return keys[Math.min(keys.length - 1, Math.max(0, i + by))]
}

// a key typed into a field, or into an open menu or dialog, belongs to it. A
// dialog marked `data-steps` is the opened row itself, so j and k still step
function typing(target: EventTarget | null) {
  return (
    target instanceof HTMLElement &&
    (target.isContentEditable ||
      target.closest(
        'input, textarea, select, [role=menu], [role=listbox], [role=dialog]:not([data-steps])',
      ) !== null)
  )
}

// `j` and `k` step to the next and the previous row: `web-app/pages/author/`
export function useStepKeys(step: (by: 1 | -1) => void, close?: () => void) {
  const latest = useRef({ step, close })
  useEffect(() => {
    latest.current = { step, close }
  })
  useEffect(() => {
    const down = (event: KeyboardEvent) => {
      if (event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey) return
      if (typing(event.target)) return
      const { step, close } = latest.current
      if (event.key === 'j' || event.key === 'k') step(event.key === 'j' ? 1 : -1)
      else if (event.key === 'Escape' && close) close()
      else return
      event.preventDefault()
    }
    window.addEventListener('keydown', down)
    return () => window.removeEventListener('keydown', down)
  }, [])
}
