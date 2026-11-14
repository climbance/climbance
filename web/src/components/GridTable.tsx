import { useRef, type ReactNode } from 'react'

import { GRID_FIRST, GRID_LEVEL_HEAD } from '@/lib/grid'
import { useEdgeFade } from '@/lib/overflow'
import { cn } from '@/lib/utils'

// a grid read by level, the module's groups and the certifications: one edge,
// one head row and one body, so a level reads in the same place on both
export function GridTable(props: {
  first: string
  levels: { key: string | number; head: ReactNode; faint?: boolean }[]
  children: ReactNode
}) {
  const box = useRef<HTMLDivElement>(null)
  // a grid wider than a phone scrolls, and its faded edge says so
  const fade = useEdgeFade(box, [], '1.5rem')
  return (
    <div ref={box} className="overflow-x-auto rounded-xl border bg-card" style={fade}>
      <table className="w-full text-meta">
        <thead>
          <tr className="text-meta text-muted-foreground">
            <th className={cn(GRID_FIRST, 'text-left font-normal')}>{props.first}</th>
            {props.levels.map((l) => (
              <th key={l.key} className={cn(GRID_LEVEL_HEAD, l.faint && 'opacity-60')}>
                {l.head}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y">{props.children}</tbody>
      </table>
    </div>
  )
}
