import { ChevronLeft, ChevronRight } from 'lucide-react'
import type { ReactNode } from 'react'

import { NEXT_ROW, PREVIOUS_ROW } from '@climb/core'

import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogTitle } from '@/components/ui/dialog'
import type { useRowDialog } from '@/lib/rowDialog'

// `wide` fills the window, for a problem read in two columns; otherwise the
// reading column's width
export function RowDialog({
  dialog,
  title,
  head,
  foot,
  wide = false,
  children,
}: {
  dialog: ReturnType<typeof useRowDialog>
  title: ReactNode
  head?: ReactNode
  foot?: ReactNode
  wide?: boolean
  children: ReactNode
}) {
  const shown = dialog.opened !== undefined
  return (
    <Dialog open={shown} onOpenChange={(now) => !now && dialog.close()}>
      {shown && (
        <DialogContent
          // j and k step inside this dialog: `lib/stepRows.ts`
          data-steps
          aria-describedby={undefined}
          // the dialog itself takes the focus, so no step button opens ringed
          onOpenAutoFocus={(event) => {
            event.preventDefault()
            ;(event.currentTarget as HTMLElement).focus()
          }}
          className={
            wide
              ? 'flex h-dvh w-screen max-w-none flex-col gap-0 rounded-none p-0 sm:max-w-none lg:h-[calc(100dvh-3rem)] lg:w-[calc(100vw-3rem)] lg:rounded-xl'
              : 'flex max-h-[calc(100dvh-3rem)] w-[calc(100vw-2rem)] max-w-(--container-reading) flex-col gap-0 p-0 sm:max-w-(--container-reading)'
          }
        >
          <header className="space-y-1 border-b px-5 py-3 pr-12">
            <div className="flex items-baseline gap-3">
              <span className="flex shrink-0 items-baseline gap-1 text-meta text-muted-foreground">
                <Button
                  variant="ghost"
                  size="icon-xs"
                  aria-label={PREVIOUS_ROW}
                  onClick={() => dialog.step(-1)}
                >
                  <ChevronLeft />
                </Button>
                <Button
                  variant="ghost"
                  size="icon-xs"
                  aria-label={NEXT_ROW}
                  onClick={() => dialog.step(1)}
                >
                  <ChevronRight />
                </Button>
                <span className="tabular-nums">{dialog.position}</span>
              </span>
              <DialogTitle className="min-w-0 truncate text-heading">{title}</DialogTitle>
            </div>
            {head}
          </header>
          <div
            className={
              wide
                ? 'min-h-0 flex-1 overflow-y-auto lg:overflow-hidden'
                : 'min-h-0 flex-1 space-y-stack overflow-y-auto p-5'
            }
          >
            {children}
          </div>
          {foot && <footer className="flex flex-wrap gap-2 border-t px-5 py-3">{foot}</footer>}
        </DialogContent>
      )}
    </Dialog>
  )
}
