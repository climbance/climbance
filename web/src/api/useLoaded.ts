import { useEffect, useState } from 'react'

import { described } from '@climb/core'

export { described }

type Answer<T> = { data?: T; error?: unknown }
type State<T> = { key: string; data?: T; error?: string }

// `key` names what is loaded: a change reloads, and the answer for a key the
// page has moved past is never shown. A change of `version` reloads the same
// key and keeps the last answer shown until the new one arrives
export function useLoaded<T>(
  load: (signal: AbortSignal) => Promise<Answer<T>>,
  key: string,
  version = 0,
) {
  const [state, setState] = useState<State<T>>({ key })
  // bumped by `retry`, which asks again for the same key
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    const controller = new AbortController()
    load(controller.signal)
      .then(({ data, error }) =>
        setState(data !== undefined ? { key, data } : { key, error: described(error) }),
      )
      .catch((reason: unknown) => {
        if (!controller.signal.aborted) setState({ key, error: String(reason) })
      })
    return () => controller.abort()
    // `key`, `attempt` and `version` alone: `load` is a new closure on every
    // render, and `key` names what it loads
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key, attempt, version])

  function retry() {
    setState({ key })
    setAttempt((one) => one + 1)
  }

  return { ...(state.key === key ? state : { key }), retry }
}
