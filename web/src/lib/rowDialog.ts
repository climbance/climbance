import { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router'

import { positionLabel } from '@climb/core'

import { stepKey, useStepKeys } from '@/lib/stepRows'

// the item the anchor names, opened over the grid: `web-app/pages/author/browser.md`
export function useRowDialog(keys: string[]) {
  const location = useLocation()
  const navigate = useNavigate()
  const anchor = decodeURIComponent(location.hash.slice(1))
  const at = keys.indexOf(anchor)
  const opened = at < 0 ? undefined : anchor
  // the row last opened stays marked once the dialog closes, and a step resumes from it
  const [last, setLast] = useState<string | null>(opened ?? null)
  if (opened && last !== opened) setLast(opened)
  const open = (key: string) =>
    navigate({ search: location.search, hash: encodeURIComponent(key) }, { replace: true })
  const close = () => {
    navigate({ search: location.search, hash: '' }, { replace: true })
    // the grid scrolled under the dialog only on arrival, so the row is brought back into view
    if (last)
      requestAnimationFrame(() =>
        document.getElementById(last)?.scrollIntoView({ block: 'nearest' }),
      )
  }
  const step = (by: 1 | -1) => {
    const next = stepKey(keys, opened ?? last, by)
    if (next !== undefined) open(next)
  }
  useStepKeys(step)
  // a link to `#<key>` scrolls to its row on arrival
  useEffect(() => {
    if (anchor) document.getElementById(anchor)?.scrollIntoView({ block: 'center' })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])
  return { opened, last, open, close, step, position: positionLabel(at + 1, keys.length) }
}
