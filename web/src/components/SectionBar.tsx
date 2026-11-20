import { useEffect, useRef } from 'react'

import type { Item } from '@/lib/sections'
import { useEdgeFade } from '@/lib/overflow'
import { cn } from '@/lib/utils'

// the sections of a long page, in one row that stays at the top as the page
// scrolls: a card's brief runs past a screen, and the ladder under it is
// otherwise reached by scrolling through the whole of it
export function SectionBar({
  items,
  current,
  onJump,
}: {
  items: Item[]
  current: string | null
  onJump: (id: string) => void
}) {
  const row = useRef<HTMLDivElement>(null)

  // the row follows the marked section, as the navigation does: `web-app/areas.md`
  useEffect(() => {
    const el = row.current
    const marked = el?.querySelector<HTMLElement>('[aria-current="true"]')
    if (!el || !marked) return
    const pad = 24
    // the row alone scrolls: scrollIntoView would move the page sideways too
    const left = marked.offsetLeft - pad
    const right = marked.offsetLeft + marked.offsetWidth + pad - el.clientWidth
    if (el.scrollLeft > left) el.scrollTo({ left, behavior: 'smooth' })
    else if (el.scrollLeft < right) el.scrollTo({ left: right, behavior: 'smooth' })
  }, [current])

  const fade = useEdgeFade(row, [items])

  // one section has nothing to jump between
  if (items.length < 2) return null
  return (
    <nav className="sticky top-0 z-10 -mx-gutter border-b bg-background px-gutter">
      <div
        ref={row}
        className="relative flex gap-1 overflow-x-auto py-2 [scrollbar-width:none]"
        style={fade}
      >
        {items.map((item) => (
          <button
            key={item.id}
            type="button"
            onClick={() => onJump(item.id)}
            aria-current={current === item.id ? 'true' : undefined}
            className={cn(
              'rounded-lg px-2.5 py-1 text-meta whitespace-nowrap transition-colors',
              current === item.id
                ? 'bg-secondary text-secondary-foreground'
                : 'text-muted-foreground hover:bg-accent',
            )}
          >
            {item.label}
          </button>
        ))}
      </div>
    </nav>
  )
}
