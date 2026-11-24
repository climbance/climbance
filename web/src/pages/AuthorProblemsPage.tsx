import { Copy } from 'lucide-react'
import { useState } from 'react'
import { Link, useSearchParams } from 'react-router'

import {
  BANK_CLEAR_LABEL,
  CASES,
  COPY,
  DIFFICULTY,
  NO_CASE,
  NO_RATING,
  NO_SITE,
  NO_SOLUTION,
  OF,
  PROBLEM_BANK_NONE,
  PROBLEM_BANK_NONE_MATCH,
  PROBLEM_BANK_TITLE,
  PROBLEM_CLEARED,
  PROBLEM_COLUMNS,
  argsText,
  caseNote,
  counted,
  configurationLabel,
  cutLine,
  dateLabel,
  difficultyLabel,
  expectedText,
  flagsLabel,
  generatorLabel,
  gridPage,
  gridQuery,
  gridSort,
  gridSorted,
  problemBankView,
  problemCommands,
  problemFilter,
  problemPicked,
  problemQuery,
  problemStatus,
  ratingLabel,
  shortId,
  siteLabel,
  SITES,
  solutionLine,
  targetLabel,
  techniquesLabel,
  type AuthorProblem,
  type AuthorProblemRow,
  type GridSort,
  type ProblemFilter,
} from '@climb/core'

import { api } from '@/api/client'
import { useLoaded } from '@/api/useLoaded'
import { DataGrid, type GridCells } from '@/components/DataGrid'
import { FilterMenu } from '@/components/FilterMenu'
import { Loaded } from '@/components/Loaded'
import { Markdown } from '@/components/Markdown'
import { PageHeader } from '@/components/PageHeader'
import { Pager } from '@/components/Pager'
import { PlainCode, PythonCode } from '@/components/PythonCode'
import { RowDialog } from '@/components/RowDialog'
import { SectionHeading } from '@/components/SectionHeading'
import { Button } from '@/components/ui/button'
import { link } from '@/lib/openRows'
import { useRowDialog } from '@/lib/rowDialog'
import { cn } from '@/lib/utils'
import { NotFoundPage } from '@/pages/NotFoundPage'

// every problem, served or retired: `web-app/pages/author/problems/`
export function AuthorProblemsPage() {
  const me = useLoaded((signal) => api.GET('/api/me', { signal }), 'me')
  const problems = useLoaded(
    (signal) => api.GET('/api/author/problems', { signal }),
    'author-problems',
  )
  const [search, setSearch] = useSearchParams()
  if (me.data && !me.data.author) return <NotFoundPage />
  const state = me.data ? problems : { retry: me.retry, error: me.error, data: undefined }

  return (
    <section className="space-y-section">
      <PageHeader title={PROBLEM_BANK_TITLE} />
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
            sort={gridSort((name) => search.get(name), PROBLEM_COLUMNS)}
            go={(next, sort) =>
              setSearch(new URLSearchParams(gridQuery(problemQuery(next), sort, PROBLEM_COLUMNS)))
            }
          />
        )}
      </Loaded>
    </section>
  )
}

const problemCells: GridCells<AuthorProblemRow> = {
  title: { cell: (one) => one.title, className: 'text-body', grow: true },
  target: { cell: targetLabel, className: 'max-w-32 truncate text-muted-foreground' },
  techniques: { cell: techniquesLabel, className: 'max-w-32 truncate text-muted-foreground' },
  score: {
    // the band reads in the difficulty filter; an unrated row names its label
    cell: (one) =>
      difficultyLabel(one.score, one.score == null ? one.difficulty : null, one.deviation),
    className: 'whitespace-nowrap text-muted-foreground',
  },
  cases: { cell: (one) => one.cases, className: 'text-muted-foreground' },
  // a retired row names its reason in the flags' column
  flags: { cell: flagsLabel, className: 'max-w-28 truncate' },
  landed: {
    cell: (one) => (one.landed_at ? dateLabel(one.landed_at) : ''),
    className: 'text-muted-foreground',
  },
}

function Shelf({
  rows,
  filter,
  sort,
  go,
}: {
  rows: AuthorProblemRow[]
  filter: ProblemFilter
  sort: GridSort | null
  go: (next: ProblemFilter, sort: GridSort | null) => void
}) {
  const view = problemBankView(rows, filter)
  const shown = gridSorted(view.rows, PROBLEM_COLUMNS, sort)
  const dialog = useRowDialog(shown.map((one) => shortId(one.problem_id)))
  const opened = shown.find((one) => shortId(one.problem_id) === dialog.opened)
  const paged = gridPage(shown, dialog.page)
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
            onPick={(value) => go(problemPicked(filter, menu.field, value), sort)}
          />
        ))}
      </div>
      <section className="space-y-stack">
        <SectionHeading
          title={PROBLEM_BANK_TITLE}
          count={shown.length}
          aside={
            view.filtered && (
              <button
                type="button"
                className={cn(link, 'text-meta text-muted-foreground')}
                onClick={() => go(PROBLEM_CLEARED, sort)}
              >
                {BANK_CLEAR_LABEL}
              </button>
            )
          }
        />
        {shown.length === 0 ? (
          <p className="text-meta text-muted-foreground">{PROBLEM_BANK_NONE_MATCH}</p>
        ) : (
          <>
            <DataGrid
              columns={PROBLEM_COLUMNS}
              cells={problemCells}
              rows={paged.rows}
              rowKey={(one) => shortId(one.problem_id)}
              marked={dialog.last}
              onOpen={dialog.open}
              sort={sort}
              onSort={(next) => go(filter, next)}
            />
            <Pager page={paged.page} pages={paged.pages} onPage={dialog.turn} />
          </>
        )}
      </section>
      {opened && <Opened key={opened.problem_id} one={opened} dialog={dialog} />}
    </div>
  )
}

// a case may weigh up to the ceiling, so an opened problem is read alone
function Opened({
  one,
  dialog,
}: {
  one: AuthorProblemRow
  dialog: ReturnType<typeof useRowDialog>
}) {
  const read = useLoaded(
    (signal) =>
      api.GET('/api/author/problems/{problem_id}', {
        params: { path: { problem_id: one.problem_id } },
        signal,
      }),
    `author-problem:${one.problem_id}`,
  )
  return (
    <RowDialog
      dialog={dialog}
      wide
      title={one.title}
      head={
        <>
          <p className="flex flex-wrap gap-x-3 text-meta">
            <button
              type="button"
              aria-label={`${COPY} ${one.problem_id}`}
              onClick={() => navigator.clipboard.writeText(one.problem_id)}
              className="inline-flex items-center gap-1 hover:bg-accent"
            >
              <code>{shortId(one.problem_id)}</code>
              <Copy className="size-3" />
            </button>
            <span className="text-muted-foreground">{problemStatus(one)}</span>
            <span className="text-muted-foreground">
              {[targetLabel(one), techniquesLabel(one)].filter(Boolean).join(' · ')}
            </span>
            <span className="text-muted-foreground tabular-nums">
              {difficultyLabel(one.score, one.difficulty, one.deviation)} ·{' '}
              {counted(one.cases, 'case')}
            </span>
            {flagsLabel(one) && <span>{flagsLabel(one)}</span>}
            {one.requests > 0 && (
              <Link to="/author#requests" className={link}>
                {counted(one.requests, 'retirement request')}
              </Link>
            )}
          </p>
          {read.data && (
            <p className="text-meta text-muted-foreground">
              {configurationLabel(read.data.written_by)}
            </p>
          )}
        </>
      }
      foot={problemCommands(one).map((command) => (
        <Button
          key={command.label}
          variant="outline"
          size="xs"
          title={command.command}
          onClick={() => navigator.clipboard.writeText(command.command)}
        >
          <Copy />
          {command.label}
        </Button>
      ))}
    >
      <Loaded of={OF.author} state={read} blankWhen={() => false}>
        {(problem) => <Problem problem={problem} />}
      </Loaded>
    </RowDialog>
  )
}

function Problem({ problem }: { problem: AuthorProblem }) {
  return (
    <div className="lg:grid lg:h-full lg:grid-cols-2">
      {/* the statement as the sitting serves it */}
      <div className="space-y-stack p-5 lg:overflow-y-auto lg:border-r">
        <Markdown>{problem.statement}</Markdown>
        {problem.signature && <PythonCode code={problem.signature} />}
      </div>
      <div className="space-y-stack p-5 lg:overflow-y-auto">
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
            <p className="text-meta text-muted-foreground">{configurationLabel(one.written_by)}</p>
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
        <section className="space-y-1">
          <SectionHeading sub title={SITES} count={problem.sites.length} />
          {problem.sites.length === 0 ? (
            <p className="text-meta text-muted-foreground">{NO_SITE}</p>
          ) : (
            <ol className="space-y-0.5 text-meta">
              {/* a resumed step wrote a second outcome, so a site may read twice */}
              {problem.sites.map((one, i) => (
                <li key={i} className="flex items-baseline gap-3">
                  <span className="w-28 shrink-0">{one.site}</span>
                  <span className="w-40 shrink-0 truncate text-muted-foreground">{one.model}</span>
                  <span className="min-w-0 flex-1">{siteLabel(one)}</span>
                </li>
              ))}
            </ol>
          )}
        </section>
      </div>
    </div>
  )
}

function Case({
  problem,
  at,
  one,
}: {
  problem: string
  at: number
  one: AuthorProblem['cases'][number]
}) {
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
      {(one) => (
        <PlainCode wrap>{`${argsText(one.args)}\n→ ${expectedText(one.expected)}`}</PlainCode>
      )}
    </Loaded>
  )
}
