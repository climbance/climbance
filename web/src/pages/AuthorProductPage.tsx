import {
  ANSWERS,
  ATTEMPTS,
  AUTHOR_TITLE,
  DAY,
  DAYS,
  LEARNERS,
  OF,
  PRODUCT_TITLE,
  SITTINGS,
  dayLabel,
  retentionCells,
  retentionLabel,
  usersLine,
} from '@climb/core'
import { api, type ProductFigures } from '@/api/client'
import { useLoaded } from '@/api/useLoaded'
import { AuthorBar } from '@/components/AuthorBar'
import { FigureTable } from '@/components/FigureTable'
import { Loaded } from '@/components/Loaded'
import { PageHeader } from '@/components/PageHeader'
import { PageSection } from '@/components/PageSection'
import { NotFoundPage } from '@/pages/NotFoundPage'

// `web-app/pages/author/product/README.md`. The API's 403 guards it; a
// learner reads the not-found page, as on `/author`
export function AuthorProductPage() {
  const me = useLoaded((signal) => api.GET('/api/me', { signal }), 'me')
  const area = useLoaded((signal) => api.GET('/api/author', { signal }), 'author')
  const figures = useLoaded((signal) => api.GET('/api/author/product', { signal }), 'product')
  if (me.data && !me.data.author) return <NotFoundPage />
  const state = me.data ? figures : { retry: me.retry, error: me.error, data: undefined }

  return (
    <section className="space-y-section">
      <PageHeader
        back={{ to: '/author', label: AUTHOR_TITLE }}
        title={PRODUCT_TITLE}
        aside={area.data && <AuthorBar pages={area.data.pages} />}
      />
      <Loaded of={OF.author} state={state} blankWhen={() => false}>
        {(read) => <Product read={read} />}
      </Loaded>
    </section>
  )
}

function Product({ read }: { read: ProductFigures }) {
  return (
    <>
      <div className="space-y-1">
        <p>{usersLine(read.invited, read.signed_in, read.active, read.active_days)}</p>
        {read.retention.map((one) => {
          const [share, percent] = retentionCells(one)
          return (
            <p key={one.after_days} className="flex gap-4 tabular-nums">
              <span className="w-44">{retentionLabel(one.after_days)}</span>
              <span className="w-16">{share}</span>
              <span>{percent}</span>
            </p>
          )
        })}
      </div>

      <PageSection id="days" title={DAYS} body="bare">
        <FigureTable
          head={[DAY, LEARNERS, SITTINGS, ATTEMPTS, ANSWERS]}
          rows={read.days.map((one) => ({
            key: one.day,
            cells: [dayLabel(one.day), one.learners, one.sittings, one.attempts, one.answers],
          }))}
        />
      </PageSection>
    </>
  )
}
