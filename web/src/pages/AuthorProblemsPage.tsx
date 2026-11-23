import { useState } from 'react'
import { Link, useSearchParams } from 'react-router'

import {
  AUTHOR_TITLE,
  BANK_CLEAR_LABEL,
  CASES,
  CLOSE_ALL,
  DIFFICULTY,
  NO_CASE,
  NO_RATING,
  NO_SOLUTION,
  OF,
  OPEN_ALL,
  PROBLEM_BANK_NONE,
  PROBLEM_BANK_NONE_MATCH,
  PROBLEM_BANK_TITLE,
  PROBLEM_CLEARED,
  PROBLEM_FILTERS,
  argsText,
  caseNote,
  counted,
  cutLine,
  difficultyLabel,
  expectedText,
  generatorLabel,
  problemBankView,
  problemFactsLine,
  problemFilter,
  problemPressed,
  problemQuery,
  ratingLabel,
  shortId,
  solutionLine,
  targetLabel,
  type AuthorProblem,
  type AuthorProblemRow,
  type ProblemFilter,
} from '@climb/core'

import { api } from '@/api/client'
import { useLoaded } from '@/api/useLoaded'
import { AuthorBar } from '@/components/AuthorBar'
import { Chips } from '@/components/Chips'
import { Loaded } from '@/components/Loaded'
import { Markdown } from '@/components/Markdown'
import { PageHeader } from '@/components/PageHeader'
import { PlainCode, PythonCode } from '@/components/PythonCode'
import { SectionHeading } from '@/components/SectionHeading'
import { link, useOpenRows } from '@/lib/openRows'
import { NotFoundPage } from '@/pages/NotFoundPage'

// every problem, served or retired: `web-app/pages/author/problems/`
export function AuthorProblemsPage() {
  const me = useLoaded((signal) => api.GET('/api/me', { signal }), 'me')
  const area = useLoaded((signal) => api.GET('/api/author', { signal }), 'author')
  const problems = useLoaded(
    (signal) => api.GET('/api/author/problems', { signal }),
    'author-problems',
  )
  const [search, setSearch] = useSearchParams()
  if (me.data && !me.data.author) return <NotFoundPage />
  const state = me.data ? problems : { retry: me.retry, error: me.error, data: undefined }

  return (
    <section className="space-y-section">
      <PageHeader
        back={{ to: '/author', label: AUTHOR_TITLE }}
        title={PROBLEM_BANK_TITLE}
        aside={area.data && <AuthorBar pages={area.data.pages} />}
      />
      <Loaded
        of={OF.author}
        state={state}
        blank={PROBLEM_BANK_NONE}
        blankWhen={(read) => !read.problems.length}
      >
        {(read) => (
          <Shelf
            rows={read.problems}
            filter={problemFilter((name) => search.get(name))}
            go={(next) => setSearch(new URLSearchParams(problemQuery(next)))}
          />
        )}
      </Loaded>
    </section>
  )
}

function Shelf({
  rows,
  filter,
  go,
}: {
  rows: AuthorProblemRow[]
  filter: ProblemFilter
  go: (next: ProblemFilter) => void
}) {
  const view = problemBankView(rows, filter)
  const { open, setOpen, flip } = useOpenRows()
  const filters = [
    ['technique', view.techniques],
    ['difficulty', view.difficulties],
    ['status', view.statuses],
    ['template', view.templates],
  ] as const
  return (
    <div className="space-y-section">
      <section className="space-y-2">
        {filters
          .filter(([, chips]) => chips.length > 0)
          .map(([field, chips]) => (
            <Chips
              key={field}
              label={PROBLEM_FILTERS[field]}
              chips={chips}
              counted
              onPress={(value) => go(problemPressed(filter, field, value))}
            />
          ))}
      </section>
      <section className="space-y-stack">
        <SectionHeading
          title={PROBLEM_BANK_TITLE}
          count={view.rows.length}
          aside={
            <span className="flex gap-3 text-meta text-muted-foreground">
              {view.filtered && (
                <button type="button" className={link} onClick={() => go(PROBLEM_CLEARED)}>
                  {BANK_CLEAR_LABEL}
                </button>
              )}
              <button
                type="button"
                className={link}
                onClick={() => setOpen(new Set(view.rows.map((one) => shortId(one.problem_id))))}
              >
                {OPEN_ALL}
              </button>
              <button type="button" className={link} onClick={() => setOpen(new Set())}>
                {CLOSE_ALL}
              </button>
            </span>
          }
        />
        {view.rows.length === 0 ? (
          <p className="text-meta text-muted-foreground">{PROBLEM_BANK_NONE_MATCH}</p>
        ) : (
          <ul className="divide-y rounded-xl border bg-card">
            {view.rows.map((one) => {
              const anchor = shortId(one.problem_id)
              return (
                <Row
                  key={one.problem_id}
                  one={one}
                  open={open.has(anchor)}
                  onFlip={() => flip(anchor)}
                />
              )
            })}
          </ul>
        )}
      </section>
    </div>
  )
}

function Row({ one, open, onFlip }: { one: AuthorProblemRow; open: boolean; onFlip: () => void }) {
  return (
    <li id={shortId(one.problem_id)} className="scroll-mt-4">
      <button
        type="button"
        aria-expanded={open}
        onClick={onFlip}
        className="flex w-full items-baseline gap-3 px-4 py-2 text-left hover:bg-accent"
      >
        <span className="text-muted-foreground">{open ? '▾' : '▸'}</span>
        <span className="min-w-0 flex-1 space-y-0.5">
          <span className="flex items-baseline gap-3">
            <code className="shrink-0 text-meta">{shortId(one.problem_id)}</code>
            <span className="min-w-0 flex-1 truncate">{one.title}</span>
            <span className="shrink-0 text-meta text-muted-foreground">{targetLabel(one)}</span>
            <span className="shrink-0 text-meta text-muted-foreground tabular-nums">
              {difficultyLabel(one.score, one.difficulty)}
            </span>
          </span>
          <span className="block text-meta text-muted-foreground">{problemFactsLine(one)}</span>
        </span>
      </button>
      {open && one.requests > 0 && (
        // a link inside the row's press would nest one press in another
        <Link to="/author/workflow#requests" className={`${link} block px-4 pb-2 text-meta`}>
          {counted(one.requests, 'retirement request')}
        </Link>
      )}
      {open && <Opened id={one.problem_id} />}
    </li>
  )
}

// a case may weigh up to the ceiling, so an opened row reads its problem alone
function Opened({ id }: { id: string }) {
  const read = useLoaded(
    (signal) =>
      api.GET('/api/author/problems/{problem_id}', {
        params: { path: { problem_id: id } },
        signal,
      }),
    `author-problem:${id}`,
  )
  return (
    <div className="space-y-stack px-4 pb-4">
      <Loaded of={OF.author} state={read} blankWhen={() => false}>
        {(problem) => <Problem problem={problem} />}
      </Loaded>
    </div>
  )
}

function Problem({ problem }: { problem: AuthorProblem }) {
  return (
    <>
      {/* the statement as the sitting serves it */}
      <div className="space-y-stack rounded-xl border p-4">
        <Markdown>{problem.statement}</Markdown>
        {problem.signature && <PythonCode code={problem.signature} />}
      </div>
      {problem.solutions.length === 0 && (
        <p className="text-meta text-muted-foreground">{NO_SOLUTION}</p>
      )}
      {problem.solutions.map((one) => (
        <section key={one.role} className="space-y-1">
          <SectionHeading
            sub
            title={one.role}
            aside={<span className="text-meta text-muted-foreground">{solutionLine(one)}</span>}
          />
          <PythonCode code={one.code} />
        </section>
      ))}
      <section className="space-y-1">
        <SectionHeading sub title={CASES} count={problem.cases.length} />
        {problem.cases.length === 0 ? (
          <p className="text-meta text-muted-foreground">{NO_CASE}</p>
        ) : (
          <ol className="space-y-0.5 text-meta">
            {problem.cases.map((one, i) => (
              <Case key={i} at={i + 1} one={one} />
            ))}
          </ol>
        )}
      </section>
      <p className="flex flex-wrap gap-x-4 text-meta">
        <span className="text-muted-foreground">{DIFFICULTY}</span>
        {problem.ratings.length === 0 && <span>{NO_RATING}</span>}
        {problem.ratings.map((one) => (
          <span key={one.created_at} className={one.standing ? 'font-medium' : undefined}>
            {ratingLabel(one)}
          </span>
        ))}
        <span className="text-muted-foreground">{generatorLabel(problem.generator)}</span>
      </p>
    </>
  )
}

function Case({ at, one }: { at: number; one: AuthorProblem['cases'][number] }) {
  const [whole, setWhole] = useState(false)
  const args = argsText(one.args)
  const expected = expectedText(one.expected)
  return (
    <li>
      <button
        type="button"
        onClick={() => setWhole(!whole)}
        className="flex w-full items-baseline gap-3 text-left hover:bg-accent"
      >
        <span className="w-8 shrink-0 text-right tabular-nums text-muted-foreground">{at}</span>
        <code className="min-w-0 flex-1 truncate">
          {whole ? '' : `${cutLine(args)} → ${cutLine(expected, 24)}`}
        </code>
        <span className="shrink-0 text-muted-foreground">{caseNote(one)}</span>
      </button>
      {whole && <PlainCode wrap>{`${args}\n→ ${expected}`}</PlainCode>}
    </li>
  )
}
