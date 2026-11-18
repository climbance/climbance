import { guide, BACK_BOARD } from '@climb/core'

import { Markdown } from '@/components/Markdown'
import { PageHeader } from '@/components/PageHeader'

const GUIDE = guide()

export function GuidePage() {
  return (
    <article className="space-y-section">
      {/* both starts the guide names begin on the board: `pages.md`, Sections */}
      <PageHeader back={{ to: '/', label: BACK_BOARD }} title={GUIDE.title} />
      <Markdown>{GUIDE.body}</Markdown>
    </article>
  )
}
