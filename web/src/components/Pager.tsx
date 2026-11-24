import { PAGE_NEXT, PAGE_PREVIOUS, pageOf } from '@climb/core'

import { Button } from '@/components/ui/button'

// the previous and the next page, the same on every page read in pages; none for one page
export function Pager({
  page,
  pages,
  onPage,
}: {
  page: number
  pages: number
  onPage: (page: number) => void
}) {
  if (pages <= 1) return null
  return (
    <div className="flex items-center gap-stack pt-1 text-meta text-muted-foreground">
      <Button variant="outline" size="sm" disabled={page === 1} onClick={() => onPage(page - 1)}>
        {PAGE_PREVIOUS}
      </Button>
      <span className="tabular-nums">{pageOf(page, pages)}</span>
      <Button
        variant="outline"
        size="sm"
        disabled={page === pages}
        onClick={() => onPage(page + 1)}
      >
        {PAGE_NEXT}
      </Button>
    </div>
  )
}
