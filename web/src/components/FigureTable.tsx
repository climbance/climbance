import type { ReactNode } from 'react'

import { cn } from '@/lib/utils'

// an author page's figures: the first column names the row, the rest are counts
export function FigureTable({
  head,
  rows,
}: {
  head: string[]
  rows: { key: string; cells: ReactNode[] }[]
}) {
  return (
    <div className="overflow-x-auto rounded-xl border bg-card">
      <table className="w-full text-meta">
        <thead>
          <tr className="text-muted-foreground">
            {head.map((cell, i) => (
              <th
                key={i}
                className={cn('px-3 py-2 font-normal', i === 0 ? 'text-left' : 'text-right')}
              >
                {cell}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y">
          {rows.map((row) => (
            <tr key={row.key}>
              {row.cells.map((cell, i) => (
                <td
                  key={i}
                  className={cn('px-3 py-1.5', i === 0 ? 'text-left' : 'text-right tabular-nums')}
                >
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
