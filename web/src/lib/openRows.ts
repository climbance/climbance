import { useEffect, useState } from 'react'
import { useLocation } from 'react-router'

// a link to `#<slug>` opens that row, on arrival and on a link within the page
export function useOpenRows() {
  const { hash } = useLocation()
  const [open, setOpen] = useState(() => new Set<string>())
  const [seen, setSeen] = useState('')
  if (hash !== seen) {
    setSeen(hash)
    if (hash) setOpen((now) => new Set(now).add(decodeURIComponent(hash.slice(1))))
  }
  useEffect(() => {
    if (hash) document.getElementById(decodeURIComponent(hash.slice(1)))?.scrollIntoView()
  }, [hash])
  const flip = (key: string) =>
    setOpen((now) => {
      const next = new Set(now)
      if (next.has(key)) next.delete(key)
      else next.add(key)
      return next
    })
  return { open, setOpen, flip }
}

export const link = 'underline-offset-4 hover:underline'
