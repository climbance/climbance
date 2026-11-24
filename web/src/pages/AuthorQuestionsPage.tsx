import { useEffect, useMemo, useState } from 'react'
import { useLocation, useSearchParams } from 'react-router'

import {
  AUTHOR_TITLE,
  BANK_CLEAR_LABEL,
  BANK_FILTERS,
  BANK_NONE,
  BANK_NONE_MATCH,
  CLOSE_ALL,
  CONCEPT,
  OF,
  OPEN_ALL,
  QUESTIONS_TITLE,
  bankCleared,
  bankFilter,
  bankPressed,
  bankQuery,
  bankView,
  codeLength,
  conceptLine,
  loadSnapshot,
  type BankFilter,
  type BankRow,
  type Course,
  type Snapshot,
} from '@climb/core'

import { api } from '@/api/client'
import { useLoaded } from '@/api/useLoaded'
import { AuthorBar } from '@/components/AuthorBar'
import { Chips } from '@/components/Chips'
import { Inline } from '@/components/Inline'
import { Loaded } from '@/components/Loaded'
import { PageHeader } from '@/components/PageHeader'
import { SectionHeading } from '@/components/SectionHeading'
import { Answered } from '@/knowledge/Ask'
import { loadedFrom, useKnowledge } from '@/knowledge/context'
import { cn } from '@/lib/utils'
import { NotFoundPage } from '@/pages/NotFoundPage'

type Concept = { slug: string; level: number; claim: string; source: string[] }

// one module's questions at once, each as the queue draws it answered:
// `web-app/pages/author/questions/`. The API's 403 guards the concepts; a
// learner reads the not-found page, as on `/author`
export function AuthorQuestionsPage() {
  const me = useLoaded((signal) => api.GET('/api/me', { signal }), 'me')
  const area = useLoaded((signal) => api.GET('/api/author', { signal }), 'author')
  const k = useKnowledge()
  // the whole snapshot, a paused or archived module's bank included
  const catalog = useMemo(
    () => (k.snapshot ? loadSnapshot(k.snapshot as Snapshot) : undefined),
    [k.snapshot],
  )
  const [search, setSearch] = useSearchParams()
  const filter = catalog ? bankFilter((name) => search.get(name), catalog) : null
  const author = me.data?.author === true
  const concepts = useLoaded(
    (signal) =>
      author && filter
        ? api.GET('/api/author/concepts', { params: { query: { module: filter.module } }, signal })
        : Promise.resolve({ data: { concepts: [] }, error: undefined }),
    `concepts-${author}-${filter?.module}`,
  )
  if (me.data && !me.data.author) return <NotFoundPage />
  const state = me.data
    ? loadedFrom(k, catalog ? filter : undefined)
    : { retry: me.retry, error: me.error, data: undefined }

  return (
    <section className="space-y-section">
      <PageHeader
        back={{ to: '/author', label: AUTHOR_TITLE }}
        title={QUESTIONS_TITLE}
        aside={area.data && <AuthorBar area={area.data} />}
      />
      <Loaded of={OF.author} state={state} blank={BANK_NONE} blankWhen={(f) => f === null}>
        {(filter) => (
          <Bank
            filter={filter!}
            view={bankView(catalog!, filter!)}
            concepts={concepts.data?.concepts ?? []}
            go={(next) => setSearch(new URLSearchParams(bankQuery(next)))}
          />
        )}
      </Loaded>
    </section>
  )
}

function Bank({
  filter,
  view,
  concepts,
  go,
}: {
  filter: BankFilter
  view: ReturnType<typeof bankView>
  concepts: Concept[]
  go: (next: BankFilter) => void
}) {
  // a link to `#<slug>` opens that row; the open rows stay out of the URL
  const { hash } = useLocation()
  const [open, setOpen] = useState(() => new Set(hash ? [decodeURIComponent(hash.slice(1))] : []))
  // the row is laid out only once the snapshot loads, after the browser's own scroll
  useEffect(() => {
    if (hash) document.getElementById(decodeURIComponent(hash.slice(1)))?.scrollIntoView()
  }, [hash])
  const bySlug = useMemo(() => new Map(concepts.map((c) => [c.slug, c])), [concepts])
  const shown = view.groups.flatMap((g) => g.rows.map((row) => row.q.id))
  const flip = (id: string) =>
    setOpen((now) => {
      const next = new Set(now)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })

  const rows = [
    ['module', view.modules],
    ['topic', view.topics],
    ['sub', view.subs],
    ['level', view.levels],
    ['kind', view.kinds],
    ['format', view.formats],
  ] as const

  return (
    <div className="space-y-section">
      <section className="space-y-2">
        {rows
          .filter(([, chips]) => chips.length > 0)
          .map(([field, chips]) => (
            <Chips
              key={field}
              label={BANK_FILTERS[field]}
              chips={chips}
              counted={field !== 'module'}
              onPress={(value) => go(bankPressed(filter, field, value))}
            />
          ))}
      </section>

      <section className="space-y-stack">
        <SectionHeading
          title={view.course.title}
          count={view.shown}
          aside={
            <span className="flex gap-3 text-meta text-muted-foreground">
              {view.filtered && (
                <button type="button" className={link} onClick={() => go(bankCleared(filter))}>
                  {BANK_CLEAR_LABEL}
                </button>
              )}
              <button type="button" className={link} onClick={() => setOpen(new Set(shown))}>
                {OPEN_ALL}
              </button>
              <button type="button" className={link} onClick={() => setOpen(new Set())}>
                {CLOSE_ALL}
              </button>
            </span>
          }
        />
        {view.shown === 0 && <p className="text-meta text-muted-foreground">{BANK_NONE_MATCH}</p>}
        {view.groups.map((g) => (
          <section key={g.key} className="space-y-1">
            <SectionHeading sub title={g.heading} count={g.rows.length} />
            <ul className="divide-y rounded-xl border bg-card">
              {g.rows.map((row) => (
                <Row
                  key={row.q.id}
                  row={row}
                  course={view.course}
                  concept={bySlug.get(row.q.concept)}
                  open={open.has(row.q.id)}
                  onFlip={() => flip(row.q.id)}
                />
              ))}
            </ul>
          </section>
        ))}
      </section>
    </div>
  )
}

const link = 'underline-offset-4 hover:underline'

function Row(props: {
  row: BankRow
  course: Course
  concept: Concept | undefined
  open: boolean
  onFlip: () => void
}) {
  const { q, format, first, lines } = props.row
  return (
    <li id={q.id} className="scroll-mt-4">
      <button
        type="button"
        aria-expanded={props.open}
        onClick={props.onFlip}
        className="flex w-full items-baseline gap-3 px-4 py-2 text-left hover:bg-accent"
      >
        <span className="text-muted-foreground">{props.open ? '▾' : '▸'}</span>
        <code className="shrink-0 text-meta">{q.id}</code>
        <span className="shrink-0 text-meta text-muted-foreground">
          {q.level} {q.kind} {format}
        </span>
        <span className="min-w-0 flex-1 truncate">
          <Inline text={first} />
        </span>
        <span className="shrink-0 text-meta text-muted-foreground tabular-nums">
          {codeLength(lines)}
        </span>
      </button>
      {props.open && (
        <div className="space-y-stack px-4 pb-4">
          <div className="rounded-xl border p-4">
            <Answered q={q} course={props.course} />
          </div>
          {props.concept && <ConceptLine concept={props.concept} />}
        </div>
      )}
    </li>
  )
}

function ConceptLine({ concept }: { concept: Concept }) {
  return (
    <div className="space-y-1 text-meta">
      <p>
        <span className="text-muted-foreground">{CONCEPT} </span>
        <code>{conceptLine(concept.slug, concept.level)}</code>
      </p>
      <p className="whitespace-pre-wrap">
        <Inline text={concept.claim} />
      </p>
      <ul className="space-y-0.5">
        {concept.source.map((one) => (
          <li key={one} className={cn('break-all text-muted-foreground')}>
            {/^https?:\/\//.test(one) ? (
              <a href={one} target="_blank" rel="noreferrer" className={link}>
                {one}
              </a>
            ) : (
              one
            )}
          </li>
        ))}
      </ul>
    </div>
  )
}
