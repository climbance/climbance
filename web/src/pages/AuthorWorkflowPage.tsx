import {
  AUTHOR_TITLE,
  CALLS,
  COST,
  DAY,
  FEEDBACK,
  NO_CALL,
  NO_FAULT,
  NO_FEEDBACK,
  NO_REQUEST,
  OF,
  RETIRED_STATE,
  RETIREMENT_REQUESTS,
  RUN_FAULTS,
  SPEND,
  WAITING,
  WAITS,
  WORKFLOW_TITLE,
  costLabel,
  dateLabel,
  dayLabel,
  periodTitle,
  requestsWaitingLine,
  shortId,
  timeLabel,
  uncostedCallsLine,
  waitingLine,
} from '@climb/core'
import { api, type WorkflowFigures } from '@/api/client'
import { useLoaded } from '@/api/useLoaded'
import { AuthorBar } from '@/components/AuthorBar'
import { FigureTable } from '@/components/FigureTable'
import { Loaded } from '@/components/Loaded'
import { PageHeader } from '@/components/PageHeader'
import { PageSection } from '@/components/PageSection'
import { NotFoundPage } from '@/pages/NotFoundPage'

const KINDS = ['submission', 'recall'] as const

// `web-app/pages/author/workflow/README.md`. The API's 403 guards it; a
// learner reads the not-found page, as on `/author`
export function AuthorWorkflowPage() {
  const me = useLoaded((signal) => api.GET('/api/me', { signal }), 'me')
  const area = useLoaded((signal) => api.GET('/api/author', { signal }), 'author')
  const figures = useLoaded((signal) => api.GET('/api/author/workflow', { signal }), 'workflow')
  if (me.data && !me.data.author) return <NotFoundPage />
  const state = me.data ? figures : { retry: me.retry, error: me.error, data: undefined }

  return (
    <section className="space-y-section">
      <PageHeader
        back={{ to: '/author', label: AUTHOR_TITLE }}
        title={WORKFLOW_TITLE}
        aside={area.data && <AuthorBar pages={area.data.pages} />}
      />
      <Loaded of={OF.author} state={state} blankWhen={() => false}>
        {(read) => <Workflow read={read} />}
      </Loaded>
    </section>
  )
}

const quiet = 'text-meta text-muted-foreground'

function Workflow({ read }: { read: WorkflowFigures }) {
  const uncosted = uncostedCallsLine(read.uncosted)
  return (
    <>
      <PageSection id="waiting" title={WAITING} body="bare">
        <FigureTable
          head={['', '']}
          rows={read.waiting.map((one) => ({
            key: one.command,
            cells: [<code key="c">{one.command}</code>, waitingLine(one)],
          }))}
        />
      </PageSection>

      <PageSection id="requests" title={RETIREMENT_REQUESTS} body="bare">
        {read.requests.length ? (
          <>
            <p className={quiet}>{requestsWaitingLine(read.requests)}</p>
            <FigureTable
              head={[DAY, '', '', '', '', '']}
              rows={read.requests.map((one, i) => ({
                key: `${one.problem_id}-${i}`,
                cells: [
                  dateLabel(one.created_at),
                  <code key="i">{shortId(one.problem_id)}</code>,
                  one.title,
                  one.reason,
                  <span key="n" className="whitespace-pre-wrap">{one.note}</span>,
                  one.waits ? WAITS : RETIRED_STATE,
                ],
              }))}
            />
          </>
        ) : (
          <p className={quiet}>{NO_REQUEST}</p>
        )}
      </PageSection>

      <PageSection id="feedback" title={FEEDBACK} body="bare">
        {read.feedback.length ? (
          <FigureTable
            head={[DAY, '', '']}
            rows={read.feedback.map((one, i) => ({
              key: `${one.created_at}-${i}`,
              cells: [
                dateLabel(one.created_at),
                `${one.client} · ${one.page}`,
                <span key="n" className="whitespace-pre-wrap">{one.note}</span>,
              ],
            }))}
          />
        ) : (
          <p className={quiet}>{NO_FEEDBACK}</p>
        )}
      </PageSection>

      <PageSection id="faults" title={periodTitle(RUN_FAULTS, read.period_days)} body="bare">
        {read.fault_days.length ? (
          <>
            <FigureTable
              head={[DAY, ...KINDS]}
              rows={read.fault_days.map((one) => ({
                key: one.day,
                cells: [dayLabel(one.day), ...KINDS.map((kind) => one.counts[kind] ?? 0)],
              }))}
            />
            <FigureTable
              head={['', '', '']}
              rows={read.faults.map((one, i) => ({
                key: `${one.created_at}-${i}`,
                cells: [
                  timeLabel(one.created_at),
                  one.kind,
                  <span key="d" className="whitespace-pre-wrap">{one.detail}</span>,
                ],
              }))}
            />
          </>
        ) : (
          <p className={quiet}>{NO_FAULT}</p>
        )}
      </PageSection>

      <PageSection id="spend" title={periodTitle(SPEND, read.period_days)} body="bare">
        {read.spend.length ? (
          <FigureTable
            head={['', CALLS, COST]}
            rows={read.spend.map((one) => ({
              key: one.part,
              cells: [one.part, one.calls, costLabel(one.cost)],
            }))}
          />
        ) : (
          <p className={quiet}>{NO_CALL}</p>
        )}
        {uncosted && <p className={quiet}>{uncosted}</p>}
      </PageSection>
    </>
  )
}
