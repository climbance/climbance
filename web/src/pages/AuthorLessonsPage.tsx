import { useMemo } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router'

import {
  BANK_CLEAR_LABEL,
  BANK_NONE,
  CLOSE_ALL,
  LESSON_BANK_FILTERS,
  LESSON_BANK_NONE_MATCH,
  LESSON_NEEDED_BY,
  LESSON_NEEDS,
  LESSON_NO_TEXT,
  LESSON_QUESTIONS,
  LESSONS_TITLE,
  OF,
  OPEN_ALL,
  bankCleared,
  bankPressed,
  bankQuery,
  lessonBankView,
  lessonFilter,
  lessonMinutesLabel,
  lessonRowLink,
  loadSnapshot,
  pretestLabel,
  questionRowLink,
  taughtLine,
  type BankFilter,
  type Course,
  type Lesson,
  type LessonBankRow,
  type LessonBankView,
  type Snapshot,
} from '@climb/core'

import { api } from '@/api/client'
import { useLoaded } from '@/api/useLoaded'
import { Chips } from '@/components/Chips'
import { Loaded } from '@/components/Loaded'
import { PageHeader } from '@/components/PageHeader'
import { SectionHeading } from '@/components/SectionHeading'
import { loadedFrom, useKnowledge } from '@/knowledge/context'
import { LessonText } from '@/knowledge/LessonText'
import { link, useOpenRows } from '@/lib/openRows'
import { NotFoundPage } from '@/pages/NotFoundPage'

// one module's lessons at once, each drawn as the lesson page draws it:
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
            go={(next) => setSearch(new URLSearchParams(bankQuery(next)))}
          />
        )}
      </Loaded>
    </section>
  )
}

function Shelf({
  filter,
  view,
  go,
}: {
  filter: BankFilter
  view: LessonBankView
  go: (next: BankFilter) => void
}) {
  const shown = view.groups.flatMap((g) => g.rows.map((row) => row.x.slug))
  const { open, setOpen, flip } = useOpenRows([...new Set(shown)])
  // a lesson under several subtopics anchors at its first row alone
  const anchored = new Set<string>()

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
        {view.shown === 0 && (
          <p className="text-meta text-muted-foreground">{LESSON_BANK_NONE_MATCH}</p>
        )}
        {view.groups.map((g) => (
          <section key={g.key} className="space-y-1">
            <SectionHeading sub title={g.heading} count={g.rows.length} />
            <ul className="divide-y rounded-xl border bg-card">
              {g.rows.map((row) => {
                const anchor = !anchored.has(row.x.slug)
                anchored.add(row.x.slug)
                return (
                  <Row
                    key={row.x.slug}
                    row={row}
                    course={view.course}
                    anchor={anchor}
                    open={open.has(row.x.slug)}
                    onFlip={() => flip(row.x.slug)}
                    rowLink={(slug) => lessonRowLink(view, filter, slug)}
                  />
                )
              })}
            </ul>
          </section>
        ))}
      </section>
    </div>
  )
}

function Row(props: {
  row: LessonBankRow
  course: Course
  anchor: boolean
  open: boolean
  onFlip: () => void
  rowLink: (slug: string) => string
}) {
  const { x, minutes, taught, questions, needs, neededBy } = props.row
  const navigate = useNavigate()
  const body = props.course.lessonBodies[x.slug] ?? ''
  return (
    <li id={props.anchor ? x.slug : undefined} className="scroll-mt-4">
      <button
        type="button"
        aria-expanded={props.open}
        onClick={props.onFlip}
        className="flex w-full items-baseline gap-3 px-4 py-2 text-left hover:bg-accent"
      >
        <span className="text-muted-foreground">{props.open ? '▾' : '▸'}</span>
        <span className="min-w-0 flex-1 space-y-0.5">
          <span className="flex items-baseline gap-3">
            <code className="shrink-0 text-meta">{x.slug}</code>
            <span className="min-w-0 flex-1 truncate">{x.title}</span>
            <span className="shrink-0 text-meta text-muted-foreground tabular-nums">
              {[lessonMinutesLabel(minutes), pretestLabel(x.pretest)].filter(Boolean).join('  ')}
            </span>
          </span>
          <span className="block text-meta text-muted-foreground">
            {taughtLine(taught, questions.length)}
          </span>
        </span>
      </button>
      {props.open && (
        <div className="space-y-stack px-4 pb-4">
          {(needs.length > 0 || neededBy.length > 0) && (
            <p className="flex flex-wrap gap-x-4 text-meta">
              <Lessons label={LESSON_NEEDS} items={needs} rowLink={props.rowLink} />
              <Lessons label={LESSON_NEEDED_BY} items={neededBy} rowLink={props.rowLink} />
            </p>
          )}
          <div className="rounded-xl border p-4">
            {body ? (
              <LessonText
                module={props.course.slug}
                text={body}
                // a linked lesson opens as its row here, not as the learner's page
                onLesson={(slug) => void navigate(props.rowLink(slug))}
              />
            ) : (
              <p className="text-meta text-muted-foreground">{LESSON_NO_TEXT}</p>
            )}
          </div>
          {questions.length > 0 && (
            <p className="flex flex-wrap gap-x-3 text-meta">
              <span className="text-muted-foreground">{LESSON_QUESTIONS}</span>
              {questions.map((q) => (
                <Link key={q.id} to={questionRowLink(props.course.slug, q.id)} className={link}>
                  <code>{q.id}</code>
                </Link>
              ))}
            </p>
          )}
        </div>
      )}
    </li>
  )
}

function Lessons(props: { label: string; items: Lesson[]; rowLink: (slug: string) => string }) {
  if (!props.items.length) return null
  return (
    <span className="flex flex-wrap gap-x-2">
      <span className="text-muted-foreground">{props.label}</span>
      {props.items.map((y) => (
        <Link key={y.slug} to={props.rowLink(y.slug)} className={link}>
          <code>{y.slug}</code>
        </Link>
      ))}
    </span>
  )
}
