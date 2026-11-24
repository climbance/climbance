import { useSyncExternalStore } from 'react'

// whether the window holds `query` now, following it as the window resizes
export function useMedia(query: string) {
  return useSyncExternalStore(
    (moved) => {
      const media = matchMedia(query)
      media.addEventListener('change', moved)
      return () => media.removeEventListener('change', moved)
    },
    () => matchMedia(query).matches,
  )
}
