import { COLD_PANEL_NOTE, COLD_START, COLD_TITLE, ratingLine, serveCold, sittingRefused } from '@climb/core'
import { useState } from 'react'
import { useNavigate } from 'react-router'

import { api } from '@/api/client'
import { useLoaded } from '@/api/useLoaded'
import { ErrorLine } from '@/components/ErrorLine'
import { PickPanel, PickRow } from '@/components/PickRow'
import { Button } from '@/components/ui/button'
import { DEVICE } from '@/knowledge/copy'

// one press, serving a cold sitting or returning to the one running: the
// engine answers a second serve with it, `web-app/pages/practice/cold/`
export function ColdPanel() {
  const navigate = useNavigate()
  const [serving, setServing] = useState(false)
  const [refused, setRefused] = useState<string | null>(null)
  // a refused read leaves the line out and the press working
  const rating = ratingLine(useLoaded((signal) => api.GET('/api/rating', { signal }), 'rating').data ?? null)

  async function start() {
    setServing(true)
    setRefused(null)
    const served = await serveCold(api, DEVICE, () => performance.now())
    setServing(false)
    if (served.ok) void navigate(`/cold/${encodeURIComponent(served.value.seated.sitting.id)}`)
    else setRefused(served.refused)
  }

  return (
    <div className="space-y-stack">
      <PickPanel>
        <PickRow
          title={COLD_TITLE}
          note={COLD_PANEL_NOTE}
          stats={[]}
          aside={
            <Button size="sm" onClick={start} disabled={serving}>
              {COLD_START}
            </Button>
          }
        >
          {rating && <span className="mt-1 block text-meta text-muted-foreground">{rating}</span>}
        </PickRow>
      </PickPanel>
      {refused && <ErrorLine>{sittingRefused(refused)}</ErrorLine>}
    </div>
  )
}
