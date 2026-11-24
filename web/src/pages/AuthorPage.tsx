import {
  ANSWERED_REQUESTS,
  BACK_BOARD,
  CLEAR,
  COPY,
  DAY,
  FEEDBACK,
  INBOX_TITLE,
  NO_ANSWERED,
  NO_FAULT,
  NO_FEEDBACK,
  OF,
  OPEN,
  RUN_FAULTS,
  WAITING,
  WAITING_REQUESTS,
  dateLabel,
  dayLabel,
  periodTitle,
  recentLine,
  shortId,
  timeLabel,
  waitingLine,
} from '@climb/core'
import { Copy } from 'lucide-react'
import { Link } from 'react-router'

import { api, type InboxFigures } from '@/api/client'
import { useLoaded } from '@/api/useLoaded'
import { AuthorBar } from '@/components/AuthorBar'
import { FigureTable } from '@/components/FigureTable'
import { Loaded } from '@/components/Loaded'
import { PageHeader } from '@/components/PageHeader'
import { PageSection } from '@/components/PageSection'
import { Button } from '@/components/ui/button'
import { link } from '@/lib/openRows'
import { NotFoundPage } from '@/pages/NotFoundPage'

const KINDS = ['submission', 'recall'] as const

// the author area's home, the inbox: `web-app/pages/author/inbox/README.md`.
// The API's 403 guards it; a learner reads the not-found page rather than a refusal
export function AuthorPage() {
  const me = useLoaded((signal) => api.GET('/api/me', { signal }), 'me')
  const area = useLoaded((signal) => api.GET('/api/author', { signal }), 'author')
  const figures = useLoaded((signal) => api.GET('/api/author/inbox', { signal }), 'inbox')
  if (me.data && !me.data.author) return <NotFoundPage />
  // held at loading until the session is read, so a learner never sees the refusal
  const state = me.data ? figures : { retry: me.retry, error: me.error, data: undefined }

  return (
    <section className="space-y-section">
      <PageHeader
        back={{ to: '/', label: BACK_BOARD }}
        title={INBOX_TITLE}
        aside={area.data && <AuthorBar pages={area.data.pages} />}
      />
      <Loaded of={OF.author} state={state} blankWhen={() => false}>
        {(read) => <Inbox read={read} />}
      </Loaded>
    </section>
  )
}

const quiet = 'text-meta text-muted-foreground'

type Request = InboxFigures['waiting_requests'][number]

const requestCells = (one: Request) => [
  dateLabel(one.created_at),
  <code key="i">{shortId(one.problem_id)}</code>,
  one.title,
  one.reason,
  <span key="n" className="whitespace-pre-wrap">{one.note}</span>,
]

function Inbox({ read }: { read: InboxFigures }) {
  return (
    <>
      <PageSection id="waiting" title={WAITING} body="bare">
        <FigureTable
          head={['', '', '']}
          rows={read.waiting.map((one) => ({
            key: one.command,
            cells: [
              <code key="c">{one.command}</code>,
              waitingLine(one),
              one.count ? (
                <Button
                  key="b"
                  variant="ghost"
                  size="icon-xs"
                  aria-label={`${COPY} ${one.command}`}
                  onClick={() => navigator.clipboard.writeText(one.command)}
                >
                  <Copy />
                </Button>
              ) : (
                ''
              ),
            ],
          }))}
        />
      </PageSection>

      <PageSection id="requests" title={WAITING_REQUESTS} body="bare">
        {read.waiting_requests.length ? (
          <FigureTable
            head={[DAY, '', '', '', '', '']}
            rows={read.waiting_requests.map((one, i) => ({
              key: `${one.problem_id}-${i}`,
              cells: [
                ...requestCells(one),
                <Link key="o" to={`/author/problems#${shortId(one.problem_id)}`} className={link}>
                  {OPEN}
                </Link>,
              ],
            }))}
          />
        ) : (
          <p className={quiet}>{CLEAR}</p>
        )}
      </PageSection>

      <PageSection id="feedback" title={FEEDBACK} body="bare">
        {read.feedback.length ? (
          <>
            <p className={quiet}>{recentLine(read.feedback_recent, read.feedback_days)}</p>
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
          </>
        ) : (
          <p className={quiet}>{NO_FEEDBACK}</p>
        )}
      </PageSection>

      <PageSection id="answered" title={ANSWERED_REQUESTS} body="bare">
        {read.answered_requests.length ? (
          <FigureTable
            head={[DAY, '', '', '', '', '']}
            rows={read.answered_requests.map((one, i) => ({
              key: `${one.problem_id}-${i}`,
              cells: [...requestCells(one), one.status],
            }))}
          />
        ) : (
          <p className={quiet}>{NO_ANSWERED}</p>
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
    </>
  )
}
