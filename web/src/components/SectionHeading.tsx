import { ChevronDown } from 'lucide-react'
import type { ReactNode } from 'react'

import { cn } from '@/lib/utils'

// a section's heading and how many records it holds, the same on every page.
// `sub` heads a section inside another, as a module's lessons sit under the
// module; `aside` holds the section's own presses or reading, at the right.
// With `onToggle` the heading is the press that closes its own section
export function SectionHeading({
  title,
  count,
  aside,
  sub = false,
  closed,
  onToggle,
}: {
  title: ReactNode
  count?: number
  aside?: ReactNode
  sub?: boolean
  closed?: boolean
  onToggle?: () => void
}) {
  const Tag = sub ? 'h3' : 'h2'
  const text = (
    <>
      {onToggle && (
        // centred on the first line, where a long title wraps at phone width
        <span aria-hidden="true" className="flex h-lh shrink-0 items-center self-start">
          <ChevronDown className={cn('size-4 transition-transform', closed && '-rotate-90')} />
        </span>
      )}
      {title}
      {count !== undefined && (
        <span className="text-meta font-normal text-muted-foreground tabular-nums">{count}</span>
      )}
    </>
  )
  return (
    <div className="flex items-baseline gap-3">
      <Tag className={cn('min-w-0 font-medium', sub ? 'text-body' : 'text-heading')}>
        {onToggle ? (
          <button
            type="button"
            onClick={onToggle}
            aria-expanded={!closed}
            className="flex items-baseline gap-2 text-left"
          >
            {text}
          </button>
        ) : (
          <span className="flex items-baseline gap-2">{text}</span>
        )}
      </Tag>
      {aside && (
        <div className="ml-auto flex shrink-0 items-baseline gap-stack text-meta text-muted-foreground">
          {aside}
        </div>
      )}
    </div>
  )
}
