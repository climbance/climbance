import {
  AUTHOR_TITLE,
  COST,
  NO_CALL,
  OF,
  SPEND,
  costLabel,
  periodLine,
  uncostedCallsLine,
} from '@climb/core'
import { api, type SpendFigures } from '@/api/client'
import { useLoaded } from '@/api/useLoaded'
import { AuthorBar } from '@/components/AuthorBar'
import { FigureTable } from '@/components/FigureTable'
import { Loaded } from '@/components/Loaded'
import { PageHeader } from '@/components/PageHeader'
import { PageSection } from '@/components/PageSection'
import { NotFoundPage } from '@/pages/NotFoundPage'

// `web-app/pages/author/spend/README.md`. The API's 403 guards it; a learner
// reads the not-found page, as on `/author`
export function AuthorSpendPage() {
  const me = useLoaded((signal) => api.GET('/api/me', { signal }), 'me')
  const area = useLoaded((signal) => api.GET('/api/author', { signal }), 'author')
  const figures = useLoaded((signal) => api.GET('/api/author/spend', { signal }), 'spend')
  if (me.data && !me.data.author) return <NotFoundPage />
  const state = me.data ? figures : { retry: me.retry, error: me.error, data: undefined }

  return (
    <section className="space-y-section">
      <PageHeader
        back={{ to: '/author', label: AUTHOR_TITLE }}
        title={SPEND}
        aside={area.data && <AuthorBar area={area.data} />}
      />
      <Loaded of={OF.author} state={state} blankWhen={() => false}>
        {(read) => <Spend read={read} />}
      </Loaded>
    </section>
  )
}

const quiet = 'text-meta text-muted-foreground'

function Spend({ read }: { read: SpendFigures }) {
  const uncosted = uncostedCallsLine(read.uncosted)
  return (
    <PageSection id="spend" title={periodLine(read.period_days)} body="bare">
      {read.spend.length ? (
        <FigureTable
          head={['', COST]}
          rows={read.spend.map((one) => ({
            key: one.part,
            cells: [one.part, costLabel(one.cost)],
          }))}
        />
      ) : (
        <p className={quiet}>{NO_CALL}</p>
      )}
      {uncosted && <p className={quiet}>{uncosted}</p>}
    </PageSection>
  )
}
