import { useState } from 'react'
import { Link, useSearchParams } from 'react-router'

import {
  AUTHOR_TITLE,
  BANK_CLEAR_LABEL,
  CASES,
  CLOSE_ALL,
  MENU_SORT,
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
  argsText,
  caseNote,
  counted,
  cutLine,
  difficultyLabel,
  expectedText,
  flagsLabel,
  generatorLabel,
  problemBankView,
  problemFilter,
  problemPicked,
  problemQuery,
  ratingLabel,
  shortId,
  solutionLine,
  targetLabel,
  techniquesLabel,
  type AuthorProblem,
  type AuthorProblemRow,
  type ProblemFilter,
} from '@climb/core'

import { api } from '@/api/client'
import { useLoaded } from '@/api/useLoaded'
import { AuthorBar } from '@/components/AuthorBar'
import { FilterMenu } from '@/components/FilterMenu'
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
        aside={area.data && <AuthorBar area={area.data} />}
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
  return (
    <div className="space-y-section">
      <div className="flex flex-wrap gap-2">
        {view.menus.map((menu) => (
          <FilterMenu
            key={menu.field}
            label={menu.label}
            options={menu.options}
            counted
            search={menu.search}
            onPick={(value) => go(problemPicked(filter, menu.field, value))}
          />
        ))}
      </div>
      <section className="space-y-stack">
        <SectionHeading
          title={PROBLEM_BANK_TITLE}
          count={view.rows.length}
          aside={
            <span className="flex items-baseline gap-3 text-meta text-muted-foreground">
              {view.filtered && (
                <button type="button" className={link} onClick={() => go({ ...PROBLEM_CLEARED, sort: filter.sort })}>
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
              {/* a sort leaves every row, so its options count nothing */}
              <FilterMenu
                label={`${MENU_SORT}: ${filter.sort}`}
                options={view.sorts}
                counted={false}
                onPick={(value) => go(problemPicked(filter, 'sort', value))}
              />
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
        {/* narrow, the break puts the techniques, the cases and the flags on a second line, and the target too on a phone */}
        <span className="flex min-w-0 flex-1 flex-wrap items-baseline gap-x-3 lg:flex-nowrap">
          <span className="order-1 min-w-32 flex-1 truncate">{one.title}</span>
          <span className="order-4 shrink-0 text-meta text-muted-foreground sm:order-2">{targetLabel(one)}</span>
          <span className="order-3 shrink-0 text-meta text-muted-foreground tabular-nums lg:order-4">
            {difficultyLabel(one.score, one.difficulty, one.deviation)}
          </span>
          <span className="order-3 basis-full lg:hidden" />
          <span className="order-4 min-w-0 truncate text-meta text-muted-foreground lg:order-3 lg:max-w-xs">
            {techniquesLabel(one)}
          </span>
          <span className="order-5 shrink-0 text-meta text-muted-foreground tabular-nums">
            {counted(one.cases, 'case')}
          </span>
          {flagsLabel(one) && (
            <span className="order-6 ml-auto shrink-0 text-meta lg:ml-0">{flagsLabel(one)}</span>
          )}
        </span>
      </button>
      {open && one.requests > 0 && (
        // a link inside the row's press would nest one press in another
        <Link to="/author#requests" className={`${link} block px-4 pb-2 text-meta`}>
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
              <Case key={one.id} problem={problem.problem_id} at={i + 1} one={one} />
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

function Case({ problem, at, one }: { problem: string; at: number; one: AuthorProblem['cases'][number] }) {
  const [whole, setWhole] = useState(false)
  return (
    <li>
      <button
        type="button"
        onClick={() => setWhole(!whole)}
        className="flex w-full items-baseline gap-3 text-left hover:bg-accent"
      >
        <span className="w-8 shrink-0 text-right tabular-nums text-muted-foreground">{at}</span>
        <code className="min-w-0 flex-1 truncate">
          {whole ? '' : `${cutLine(one.args)} → ${cutLine(one.expected, 24)}`}
        </code>
        <span className="shrink-0 text-muted-foreground">{caseNote(one)}</span>
      </button>
      {whole && <WholeCase problem={problem} id={one.id} />}
    </li>
  )
}

// the opened problem carries each case cut, so a pressed one reads whole alone
function WholeCase({ problem, id }: { problem: string; id: string }) {
  const read = useLoaded(
    (signal) =>
      api.GET('/api/author/problems/{problem_id}/cases/{case_id}', {
        params: { path: { problem_id: problem, case_id: id } },
        signal,
      }),
    `author-case:${problem}:${id}`,
  )
  return (
    <Loaded of={OF.author} state={read} blankWhen={() => false}>
      {(one) => <PlainCode wrap>{`${argsText(one.args)}\n→ ${expectedText(one.expected)}`}</PlainCode>}
    </Loaded>
  )
}
