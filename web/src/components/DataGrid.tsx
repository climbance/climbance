import { ArrowDown, ArrowUp } from 'lucide-react'
import type { ReactNode } from 'react'

import { gridPressed, type GridColumn, type GridSort } from '@climb/core'

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { cn } from '@/lib/utils'

// `grow` takes the width the other columns leave, and truncates there
export type GridCells<R> = Record<
  string,
  { cell: (row: R) => ReactNode; className?: string; grow?: boolean }
>

// the content browser's grid, one row per item: `web-app/pages/author/browser.md`.
// `marked` is the row last opened; a press anywhere on a row opens it
export function DataGrid<R>({
  columns,
  cells,
  rows,
  rowKey,
  marked,
  onOpen,
  sort,
  onSort,
}: {
  columns: GridColumn<R>[]
  cells: GridCells<R>
  rows: R[]
  rowKey: (row: R) => string
  marked: string | null
  onOpen: (key: string) => void
  sort: GridSort | null
  onSort: (next: GridSort) => void
}) {
  return (
    <div className="rounded-xl border bg-card">
      <Table className="text-meta">
        <TableHeader>
          <TableRow className="hover:bg-transparent">
            {columns.map((column) => {
              const on = sort?.column === column.id ? sort.order : undefined
              return (
                <TableHead
                  key={column.id}
                  aria-sort={on === 'asc' ? 'ascending' : on === 'desc' ? 'descending' : undefined}
                  className={cn(
                    'h-9 px-3 font-normal text-muted-foreground',
                    column.numeric && 'text-right',
                    cells[column.id]?.grow && 'w-full min-w-40',
                  )}
                >
                  {column.sortBy ? (
                    <button
                      type="button"
                      onClick={() => onSort(gridPressed(sort, column))}
                      className="inline-flex items-center gap-1 hover:text-foreground"
                    >
                      {column.header}
                      {on === 'asc' && <ArrowUp className="size-3" />}
                      {on === 'desc' && <ArrowDown className="size-3" />}
                    </button>
                  ) : (
                    column.header
                  )}
                </TableHead>
              )
            })}
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((row) => {
            const key = rowKey(row)
            return (
              <TableRow
                key={key}
                id={key}
                onClick={() => onOpen(key)}
                className={cn(
                  'scroll-mt-4 cursor-pointer hover:bg-accent',
                  marked === key && 'bg-accent',
                )}
              >
                {columns.map((column, i) => (
                  <TableCell
                    key={column.id}
                    className={cn(
                      'px-3 py-1.5',
                      column.numeric && 'text-right tabular-nums',
                      cells[column.id]?.grow && 'w-full max-w-0 min-w-40 truncate',
                      cells[column.id]?.className,
                    )}
                  >
                    {i === 0 ? (
                      // the row's press for the keyboard; the pointer presses the whole row
                      <button
                        type="button"
                        aria-haspopup="dialog"
                        onClick={(event) => {
                          event.stopPropagation()
                          onOpen(key)
                        }}
                        className="max-w-full truncate text-left"
                      >
                        {cells[column.id]?.cell(row)}
                      </button>
                    ) : (
                      cells[column.id]?.cell(row)
                    )}
                  </TableCell>
                ))}
              </TableRow>
            )
          })}
        </TableBody>
      </Table>
    </div>
  )
}
