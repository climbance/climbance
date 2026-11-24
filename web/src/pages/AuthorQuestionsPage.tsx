import { useMemo } from 'react'
import { Link, useSearchParams } from 'react-router'

import {
  BANK_CLEAR_LABEL,
  BANK_FILTERS,
  BANK_NONE,
  BANK_NONE_MATCH,
  CONCEPT,
  OF,
  QUESTION_COLUMNS,
  QUESTIONS_TITLE,
  TAUGHT_BY,
  bankCleared,
  bankFilter,
  bankPressed,
  bankQuery,
  bankView,
  conceptLine,
  gridPage,
  gridQuery,
  gridSort,
  gridSorted,
  lessonRowOf,
  loadSnapshot,
  type BankFilter,
  type BankRow,
  type BankView,
  type Course,
  type GridSort,
  type Snapshot,
} from '@climb/core'

import { api } from '@/api/client'
import { useLoaded } from '@/api/useLoaded'
import { Chips } from '@/components/Chips'
import { DataGrid, type GridCells } from '@/components/DataGrid'
import { Inline } from '@/components/Inline'
import { Loaded } from '@/components/Loaded'
import { PageHeader } from '@/components/PageHeader'
import { Pager } from '@/components/Pager'
import { RowDialog } from '@/components/RowDialog'
import { SectionHeading } from '@/components/SectionHeading'
import { Answered } from '@/knowledge/Ask'
import { loadedFrom, useKnowledge } from '@/knowledge/context'
import { link } from '@/lib/openRows'
import { useRowDialog } from '@/lib/rowDialog'
import { cn } from '@/lib/utils'
import { NotFoundPage } from '@/pages/NotFoundPage'

// one module's questions, each opened as the queue draws it answered:
// `web-app/pages/author/questions/`. The API's 403 guards the concept; a
// learner reads the not-found page, as on `/author`
export function AuthorQuestionsPage() {
  const me = useLoaded((signal) => api.GET('/api/me', { signal }), 'me')
  const k = useKnowledge()
  // the whole snapshot, a paused or archived module's bank included
  const catalog = useMemo(
    () => (k.snapshot ? loadSnapshot(k.snapshot as Snapshot) : undefined),
    [k.snapshot],
  )
  const [search, setSearch] = useSearchParams()
  const filter = catalog ? bankFilter((name) => search.get(name), catalog) : null
  if (me.data && !me.data.author) return <NotFoundPage />
  const state = me.data
    ? loadedFrom(k, catalog ? filter : undefined)
    : { retry: me.retry, error: me.error, data: undefined }

  return (
    <section className="space-y-section">
      <PageHeader title={QUESTIONS_TITLE} />
      <Loaded of={OF.author} state={state} blank={BANK_NONE} blankWhen={(f) => f === null}>
        {(filter) => (
          <Bank
            filter={filter!}
            view={bankView(catalog!, filter!)}
            sort={gridSort((name) => search.get(name), QUESTION_COLUMNS)}
            go={(next, sort) =>
              setSearch(new URLSearchParams(gridQuery(bankQuery(next), sort, QUESTION_COLUMNS)))
            }
          />
        )}
      </Loaded>
    </section>
  )
}

const quiet = 'whitespace-nowrap text-muted-foreground'

const questionCells: GridCells<BankRow> = {
  // the whole slug reads in the dialog's head
  slug: { cell: (row) => <code>{row.q.id}</code>, className: 'max-w-56 truncate' },
  subtopic: { cell: (row) => row.subtopic, className: 'max-w-40 truncate text-muted-foreground' },
  level: { cell: (row) => row.q.level, className: quiet },
  kind: { cell: (row) => row.q.kind, className: quiet },
  format: { cell: (row) => row.format, className: quiet },
  prompt: { cell: (row) => <Inline text={row.first} />, grow: true },
  code: { cell: (row) => row.lines || '', className: quiet },
}

function Bank({
  filter,
  view,
  sort,
  go,
}: {
  filter: BankFilter
  view: BankView
  sort: GridSort | null
  go: (next: BankFilter, sort: GridSort | null) => void
}) {
  const shown = gridSorted(view.rows, QUESTION_COLUMNS, sort)
  const dialog = useRowDialog(shown.map((row) => row.q.id))
  const opened = shown.find((row) => row.q.id === dialog.opened)
  const paged = gridPage(shown, dialog.page)

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
              onPress={(value) => go(bankPressed(filter, field, value), sort)}
            />
          ))}
      </section>

      <section className="space-y-stack">
        <SectionHeading
          title={view.course.title}
          count={view.shown}
          aside={
            view.filtered && (
              <button
                type="button"
                className={cn(link, 'text-meta text-muted-foreground')}
                onClick={() => go(bankCleared(filter), sort)}
              >
                {BANK_CLEAR_LABEL}
              </button>
            )
          }
        />
        {view.shown === 0 ? (
          <p className="text-meta text-muted-foreground">{BANK_NONE_MATCH}</p>
        ) : (
          <>
            <DataGrid
              columns={QUESTION_COLUMNS}
              cells={questionCells}
              rows={paged.rows}
              rowKey={(row) => row.q.id}
              marked={dialog.last}
              onOpen={dialog.open}
              sort={sort}
              onSort={(next) => go(filter, next)}
            />
            <Pager page={paged.page} pages={paged.pages} onPage={dialog.turn} />
          </>
        )}
      </section>
      {opened && (
        <RowDialog
          dialog={dialog}
          title={<code>{opened.q.id}</code>}
          head={
            <p className="text-meta text-muted-foreground">
              {[opened.subtopic, `level ${opened.q.level}`, opened.q.kind, opened.format].join(
                ' · ',
              )}
            </p>
          }
        >
          <Opened key={opened.q.id} row={opened} course={view.course} />
        </RowDialog>
      )}
    </div>
  )
}

function Opened({ row, course }: { row: BankRow; course: Course }) {
  return (
    <>
      <div className="rounded-xl border p-4">
        <Answered q={row.q} course={course} />
      </div>
      {row.q.concept && <ConceptLine module={course.slug} slug={row.q.concept} />}
      {row.lessons.length > 0 && (
        <p className="flex flex-wrap gap-x-3 text-meta">
          <span className="text-muted-foreground">{TAUGHT_BY}</span>
          {row.lessons.map((x) => (
            <Link key={x.slug} to={lessonRowOf(course.slug, x.slug)} className={link}>
              {x.title}
            </Link>
          ))}
        </p>
      )}
    </>
  )
}

// one concept, read as its question opens: the snapshot carries none
function ConceptLine({ module, slug }: { module: string; slug: string }) {
  const read = useLoaded(
    (signal) =>
      api.GET('/api/author/concepts/{module}/{slug}', {
        params: { path: { module, slug } },
        signal,
      }),
    `concept:${module}:${slug}`,
  )
  const concept = read.data
  if (!concept) return null
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
          <li key={one} className="break-all text-muted-foreground">
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
