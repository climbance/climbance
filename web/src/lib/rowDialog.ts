import { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router'

import { pageHolding, pageNumber, pageQuery, positionLabel } from '@climb/core'

import { stepKey, useStepKeys } from '@/lib/stepRows'

// the item the anchor names, opened over the grid, and the grid's page:
// `web-app/pages/author/browser.md`. `keys` is every matching row, across pages
export function useRowDialog(keys: string[]) {
  const location = useLocation()
  const navigate = useNavigate()
  const anchor = decodeURIComponent(location.hash.slice(1))
  const at = keys.indexOf(anchor)
  const opened = at < 0 ? undefined : anchor
  const asked = pageNumber((name) => new URLSearchParams(location.search).get(name))
  // the page holding the opened row, so a link to an item lands on its page
  const page = at < 0 ? asked : pageHolding(at)
  // the row last opened stays marked once the dialog closes, and a step resumes from it
  const [last, setLast] = useState<string | null>(opened ?? null)
  if (opened && last !== opened) setLast(opened)
  const open = (key: string) =>
    navigate(
      {
        search: pageQuery(location.search, pageHolding(keys.indexOf(key))),
        hash: encodeURIComponent(key),
      },
      { replace: true },
    )
  const close = () => {
    navigate({ search: pageQuery(location.search, page), hash: '' }, { replace: true })
    // the grid scrolled under the dialog only on arrival, so the row is brought back into view
    if (last)
      requestAnimationFrame(() =>
        document.getElementById(last)?.scrollIntoView({ block: 'nearest' }),
      )
  }
  const turn = (to: number) => {
    navigate({ search: pageQuery(location.search, to), hash: '' })
    window.scrollTo({ top: 0 })
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
  return {
    opened,
    last,
    page,
    open,
    close,
    step,
    turn,
    position: positionLabel(at + 1, keys.length),
  }
}
