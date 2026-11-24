import { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router'

import { stepKey, useStepKeys } from '@/lib/stepRows'

// a link to `#<slug>` opens that row, on arrival and on a link within the page;
// `j` and `k` close the row at the cursor, open the next and move the anchor there
export function useOpenRows(keys: string[]) {
  const { hash, search } = useLocation()
  const navigate = useNavigate()
  const [open, setOpen] = useState(() => new Set<string>())
  const [seen, setSeen] = useState('')
  const [at, setAt] = useState<string | null>(null)
  const [stepped, setStepped] = useState(0)
  if (hash !== seen) {
    setSeen(hash)
    if (hash) {
      const key = decodeURIComponent(hash.slice(1))
      setOpen((now) => new Set(now).add(key))
      setAt(key)
    }
  }
  useEffect(() => {
    if (hash) document.getElementById(decodeURIComponent(hash.slice(1)))?.scrollIntoView()
  }, [hash, stepped])
  const flip = (key: string) => {
    setAt(key)
    setOpen((now) => {
      const next = new Set(now)
      if (next.has(key)) next.delete(key)
      else next.add(key)
      return next
    })
  }
  useStepKeys((by) => {
    const next = stepKey(keys, at, by)
    if (next === undefined) return
    setOpen((now) => {
      const was = new Set(now)
      if (at !== null && at !== next) was.delete(at)
      return was.add(next)
    })
    setAt(next)
    setStepped((n) => n + 1)
    navigate({ search, hash: next }, { replace: true })
  })
  return { open, setOpen, flip }
}

export const link = 'underline-offset-4 hover:underline'
