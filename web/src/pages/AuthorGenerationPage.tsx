import {
  AUTHOR_TITLE,
  CORPUS,
  DRAFTS,
  DRAFTS_NOW,
  GAP,
  GENERATION_TITLE,
  NO_CARD,
  NO_DRAFT,
  NO_STOP,
  OF,
  OLDEST,
  OPTIONAL,
  RETIRED,
  STOPPED_BY,
  UNLABELLED,
  WRITINGS,
  ageLine,
  gapsLine,
  periodLine,
  spendLine,
  stopLabel,
  uncostedLine,
  untemplatedLine,
  writingsLine,
} from '@climb/core'
import { api, type GenerationFigures } from '@/api/client'
import { useLoaded } from '@/api/useLoaded'
import { AuthorBar } from '@/components/AuthorBar'
import { FigureTable } from '@/components/FigureTable'
import { Loaded } from '@/components/Loaded'
import { PageHeader } from '@/components/PageHeader'
import { PageSection } from '@/components/PageSection'
import { NotFoundPage } from '@/pages/NotFoundPage'

const BANDS = ['easy', 'medium', 'hard'] as const

// `web-app/pages/author/generation/README.md`. The API's 403 guards it; a
// learner reads the not-found page, as on `/author`
export function AuthorGenerationPage() {
  const me = useLoaded((signal) => api.GET('/api/me', { signal }), 'me')
  const area = useLoaded((signal) => api.GET('/api/author', { signal }), 'author')
  const figures = useLoaded((signal) => api.GET('/api/author/generation', { signal }), 'generation')
  if (me.data && !me.data.author) return <NotFoundPage />
  const state = me.data ? figures : { retry: me.retry, error: me.error, data: undefined }

  return (
    <section className="space-y-section">
      <PageHeader
        back={{ to: '/author', label: AUTHOR_TITLE }}
        title={GENERATION_TITLE}
        aside={area.data && <AuthorBar pages={area.data.pages} />}
      />
      <Loaded of={OF.author} state={state} blankWhen={() => false}>
        {(read) => <Generation read={read} />}
      </Loaded>
    </section>
  )
}

function Generation({ read }: { read: GenerationFigures }) {
  const uncosted = uncostedLine(read.uncosted)
  const untemplated = untemplatedLine(read.untemplated)
  const unlabelled = read.corpus.some((row) => row.unlabelled > 0)
  return (
    <>
      <div className="space-y-1">
        <p className="text-meta text-muted-foreground">{periodLine(read.period_days)}</p>
        <p>{writingsLine(read.writings, read.landed)}</p>
        <p>{spendLine(read.spend_per_landed)}</p>
        {uncosted && <p className="text-meta text-muted-foreground">{uncosted}</p>}
      </div>

      <PageSection id="stopped" title={STOPPED_BY} body="bare">
        {read.stops.length ? (
          <FigureTable
            head={['', WRITINGS]}
            rows={read.stops.map((stop) => ({
              key: stopLabel(stop),
              cells: [stopLabel(stop), stop.writings],
            }))}
          />
        ) : (
          <p className="text-meta text-muted-foreground">{NO_STOP}</p>
        )}
      </PageSection>

      <PageSection id="drafts" title={DRAFTS_NOW} body="bare">
        {read.drafts.length ? (
          <FigureTable
            head={['', DRAFTS, OLDEST]}
            rows={read.drafts.map((one) => ({
              key: one.state,
              cells: [
                one.state,
                one.drafts,
                one.oldest_days == null ? '' : ageLine(one.oldest_days),
              ],
            }))}
          />
        ) : (
          <p className="text-meta text-muted-foreground">{NO_DRAFT}</p>
        )}
      </PageSection>

      <PageSection id="corpus" title={CORPUS} body="bare">
        {read.corpus.length ? (
          <FigureTable
            head={['', ...BANDS, ...(unlabelled ? [UNLABELLED] : []), RETIRED, '']}
            rows={read.corpus.map((row) => ({
              key: `${row.card_slug}/${row.template_slug}`,
              cells: [
                `${row.card_slug} / ${row.template_slug}`,
                ...BANDS.map((band) => row.counts[band] ?? 0),
                ...(unlabelled ? [row.unlabelled] : []),
                row.retired,
                row.gap ? GAP : row.optional ? OPTIONAL : '',
              ],
            }))}
          />
        ) : (
          <p className="text-meta text-muted-foreground">{NO_CARD}</p>
        )}
        {read.corpus.length > 0 && (
          <p className="text-meta text-muted-foreground">{gapsLine(read.corpus)}</p>
        )}
        {untemplated && <p className="text-meta text-muted-foreground">{untemplated}</p>}
      </PageSection>
    </>
  )
}
