import { useMemo } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router'

import {
  BANK_CLEAR_LABEL,
  BANK_NONE,
  LESSON_BANK_FILTERS,
  LESSON_BANK_NONE_MATCH,
  LESSON_COLUMNS,
  LESSON_NEEDED_BY,
  LESSON_NEEDS,
  LESSON_NO_TEXT,
  LESSON_QUESTIONS,
  LESSONS_TITLE,
  OF,
  bankCleared,
  bankPressed,
  bankQuery,
  gridQuery,
  gridSort,
  gridSorted,
  lessonBankView,
  lessonFilter,
  lessonRowLink,
  loadSnapshot,
  questionRowLink,
  taughtLabel,
  taughtLine,
  type BankFilter,
  type GridSort,
  type Lesson,
  type LessonBankRow,
  type LessonBankView,
  type Snapshot,
} from '@climb/core'

import { api } from '@/api/client'
import { useLoaded } from '@/api/useLoaded'
import { Chips } from '@/components/Chips'
import { DataGrid, type GridCells } from '@/components/DataGrid'
import { Loaded } from '@/components/Loaded'
import { PageHeader } from '@/components/PageHeader'
import { RowDialog } from '@/components/RowDialog'
import { SectionHeading } from '@/components/SectionHeading'
import { loadedFrom, useKnowledge } from '@/knowledge/context'
import { LessonText } from '@/knowledge/LessonText'
import { link } from '@/lib/openRows'
import { useRowDialog } from '@/lib/rowDialog'
import { cn } from '@/lib/utils'
import { NotFoundPage } from '@/pages/NotFoundPage'

// one module's lessons, each opened as the lesson page draws it:
// `web-app/pages/author/lessons/`. A learner reads the not-found page
export function AuthorLessonsPage() {
  const me = useLoaded((signal) => api.GET('/api/me', { signal }), 'me')
  const k = useKnowledge()
  const catalog = useMemo(
    () => (k.snapshot ? loadSnapshot(k.snapshot as Snapshot) : undefined),
    [k.snapshot],
  )
  const [search, setSearch] = useSearchParams()
  const filter = catalog ? lessonFilter((name) => search.get(name), catalog) : null
  if (me.data && !me.data.author) return <NotFoundPage />
  const state = me.data
    ? loadedFrom(k, catalog ? filter : undefined)
    : { retry: me.retry, error: me.error, data: undefined }

  return (
    <section className="space-y-section">
      <PageHeader title={LESSONS_TITLE} />
      <Loaded of={OF.author} state={state} blank={BANK_NONE} blankWhen={(f) => f === null}>
        {(filter) => (
          <Shelf
            filter={filter!}
            view={lessonBankView(catalog!, filter!)}
            sort={gridSort((name) => search.get(name), LESSON_COLUMNS)}
            go={(next, sort) =>
              setSearch(new URLSearchParams(gridQuery(bankQuery(next), sort, LESSON_COLUMNS)))
            }
          />
        )}
      </Loaded>
    </section>
  )
}

const quiet = 'whitespace-nowrap text-muted-foreground'

const lessonCells: GridCells<LessonBankRow> = {
  slug: { cell: (row) => <code>{row.x.slug}</code>, className: 'max-w-56 truncate' },
  title: { cell: (row) => row.x.title, className: 'text-body', grow: true },
  teaches: {
    cell: (row) => taughtLabel(row.taught),
    className: 'max-w-64 truncate text-muted-foreground',
  },
  minutes: { cell: (row) => row.minutes || '', className: quiet },
  pretest: { cell: (row) => row.x.pretest, className: quiet },
  questions: { cell: (row) => row.questions.length, className: quiet },
}

function Shelf({
  filter,
  view,
  sort,
  go,
}: {
  filter: BankFilter
  view: LessonBankView
  sort: GridSort | null
  go: (next: BankFilter, sort: GridSort | null) => void
}) {
  const shown = gridSorted(view.rows, LESSON_COLUMNS, sort)
  const dialog = useRowDialog(shown.map((row) => row.x.slug))
  const opened = shown.find((row) => row.x.slug === dialog.opened)

  const rows = [
    ['module', view.modules],
    ['topic', view.topics],
    ['sub', view.subs],
  ] as const

  return (
    <div className="space-y-section">
      <section className="space-y-2">
        {rows
          .filter(([, chips]) => chips.length > 0)
          .map(([field, chips]) => (
            <Chips
              key={field}
              label={LESSON_BANK_FILTERS[field]}
              chips={chips}
              counted={field !== 'module'}
              onPress={(value) => go(bankPressed(filter, field, value), sort)}
            />
          ))}
      </section>

      <section className="space-y-stack">
        <SectionHeading
          title={view.course.title}
          count={shown.length}
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
        {shown.length === 0 ? (
          <p className="text-meta text-muted-foreground">{LESSON_BANK_NONE_MATCH}</p>
        ) : (
          <DataGrid
            columns={LESSON_COLUMNS}
            cells={lessonCells}
            rows={shown}
            rowKey={(row) => row.x.slug}
            marked={dialog.last}
            onOpen={dialog.open}
            sort={sort}
            onSort={(next) => go(filter, next)}
          />
        )}
      </section>
      {opened && (
        <RowDialog
          dialog={dialog}
          title={opened.x.title}
          head={
            <>
              <p className="text-meta text-muted-foreground">
                <code>{opened.x.slug}</code> · {taughtLine(opened)}
              </p>
              {(opened.needs.length > 0 || opened.neededBy.length > 0) && (
                <p className="flex flex-wrap gap-x-4 text-meta">
                  <Lessons label={LESSON_NEEDS} items={opened.needs} view={view} filter={filter} />
                  <Lessons
                    label={LESSON_NEEDED_BY}
                    items={opened.neededBy}
                    view={view}
                    filter={filter}
                  />
                </p>
              )}
            </>
          }
        >
          <Opened row={opened} view={view} filter={filter} />
        </RowDialog>
      )}
    </div>
  )
}

// the snapshot holds the lesson's text, so an opened lesson makes no request
function Opened({
  row,
  view,
  filter,
}: {
  row: LessonBankRow
  view: LessonBankView
  filter: BankFilter
}) {
  const navigate = useNavigate()
  const body = view.course.lessonBodies[row.x.slug] ?? ''
  return (
    <>
      {body ? (
        <LessonText
          module={view.course.slug}
          text={body}
          // a linked lesson opens in this dialog, not as the learner's page
          onLesson={(slug) => void navigate(lessonRowLink(view, filter, slug))}
        />
      ) : (
        <p className="text-meta text-muted-foreground">{LESSON_NO_TEXT}</p>
      )}
      {row.questions.length > 0 && (
        <p className="flex flex-wrap gap-x-3 text-meta">
          <span className="text-muted-foreground">{LESSON_QUESTIONS}</span>
          {row.questions.map((q) => (
            <Link key={q.id} to={questionRowLink(view.course.slug, q.id)} className={link}>
              <code>{q.id}</code>
            </Link>
          ))}
        </p>
      )}
    </>
  )
}

function Lessons(props: {
  label: string
  items: Lesson[]
  view: LessonBankView
  filter: BankFilter
}) {
  if (!props.items.length) return null
  return (
    <span className="flex flex-wrap gap-x-2">
      <span className="text-muted-foreground">{props.label}</span>
      {props.items.map((y) => (
        <Link key={y.slug} to={lessonRowLink(props.view, props.filter, y.slug)} className={link}>
          <code>{y.slug}</code>
        </Link>
      ))}
    </span>
  )
}
