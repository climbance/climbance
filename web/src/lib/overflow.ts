import { useEffect, useState, type RefObject } from 'react'

// a faded edge says the row goes on past it: `pages.md`
export function useEdgeFade(
  row: RefObject<HTMLElement | null>,
  deps: unknown[] = [],
  width = '2rem',
) {
  const [more, setMore] = useState({ left: false, right: false })

  useEffect(() => {
    const el = row.current
    if (!el) return
    const read = () =>
      setMore({
        left: el.scrollLeft > 1,
        right: el.scrollLeft + el.clientWidth < el.scrollWidth - 1,
      })
    read()
    el.addEventListener('scroll', read, { passive: true })
    const observer = new ResizeObserver(read)
    observer.observe(el)
    return () => {
      el.removeEventListener('scroll', read)
      observer.disconnect()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  const fade = `linear-gradient(to right, ${more.left ? 'transparent' : 'black'}, black ${width}, black calc(100% - ${width}), ${more.right ? 'transparent' : 'black'})`
  return { maskImage: fade, WebkitMaskImage: fade }
}
