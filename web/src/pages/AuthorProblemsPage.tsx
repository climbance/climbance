import { Copy } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link, useLocation, useNavigate, useSearchParams } from 'react-router'

import {
  AUTHOR_TITLE,
  BANK_CLEAR_LABEL,
  CASES,
  COPY,
  MENU_SORT,
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
  argsText,
  caseNote,
  counted,
  configurationLabel,
  cutLine,
  difficultyLabel,
  expectedText,
  flagCount,
  flagsLabel,
  generatorLabel,
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
import { Button } from '@/components/ui/button'
import { useMedia } from '@/lib/media'
import { link } from '@/lib/openRows'
import { cn } from '@/lib/utils'
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
  const location = useLocation()
  const navigate = useNavigate()
  // the panel needs the reading column's whole width beside a list of titles
  const beside = useMedia('(min-width: 64rem)')
  const anchor = decodeURIComponent(location.hash.slice(1))
  const opened = view.rows.find((one) => shortId(one.problem_id) === anchor)
  const press = (one: AuthorProblemRow) => {
    const next = shortId(one.problem_id)
    navigate({ search: location.search, hash: next === anchor ? '' : next }, { replace: true })
  }
  // a link to `#<id>` scrolls to its row on arrival, and a press leaves the scroll
  useEffect(() => {
    if (anchor) document.getElementById(anchor)?.scrollIntoView({ block: 'nearest' })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])
  const narrowed = beside && opened !== undefined
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
          <div className="flex items-start gap-4">
            <ul className={cn('divide-y rounded-xl border bg-card', narrowed ? 'w-56 shrink-0' : 'min-w-0 flex-1')}>
              {view.rows.map((one) => (
                <Row
                  key={one.problem_id}
                  one={one}
                  open={one === opened}
                  narrowed={narrowed}
                  onPress={() => press(one)}
                />
              ))}
            </ul>
            {narrowed && (
              // sticky, so the panel scrolls on its own and the list keeps its scroll
              <aside className="sticky top-4 max-h-[calc(100dvh-2rem)] min-w-0 flex-1 overflow-y-auto rounded-xl border bg-card p-4">
                <Panel key={opened.problem_id} one={opened} />
              </aside>
            )}
          </div>
        )}
      </section>
    </div>
  )
}

function Row({
  one,
  open,
  narrowed,
  onPress,
}: {
  one: AuthorProblemRow
  open: boolean
  narrowed: boolean
  onPress: () => void
}) {
  return (
    <li id={shortId(one.problem_id)} className="scroll-mt-4">
      <button
        type="button"
        aria-expanded={open}
        onClick={onPress}
        className={cn(
          'flex w-full items-baseline gap-3 px-4 py-2 text-left hover:bg-accent',
          open && 'bg-accent',
        )}
      >
        {/* beside the panel, the opened row stays closed in shape and reads marked */}
        <span className={open && narrowed ? 'text-foreground' : 'text-muted-foreground'}>
          {open && !narrowed ? '▾' : '▸'}
        </span>
        {narrowed ? (
          <span className="flex min-w-0 flex-1 items-baseline gap-2">
            <span className="min-w-0 flex-1 truncate">{one.title}</span>
            {flagCount(one) && <span className="shrink-0 text-meta tabular-nums">{flagCount(one)}</span>}
          </span>
        ) : (
          // narrow, the break puts the techniques, the cases and the flags on a second line, and the target too on a phone
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
        )}
      </button>
      {open && !narrowed && (
        <div className="px-4 pb-4">
          <Panel one={one} inPlace />
        </div>
      )}
    </li>
  )
}

// a case may weigh up to the ceiling, so an opened problem is read alone
function Panel({ one, inPlace = false }: { one: AuthorProblemRow; inPlace?: boolean }) {
  const read = useLoaded(
    (signal) =>
      api.GET('/api/author/problems/{problem_id}', {
        params: { path: { problem_id: one.problem_id } },
        signal,
      }),
    `author-problem:${one.problem_id}`,
  )
  return (
    <div className="space-y-stack">
      <header className="space-y-1">
        {/* in place, the row above already names the title, the target, the score and the flags */}
        {!inPlace && <h2 className="text-heading font-medium">{one.title}</h2>}
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
          {!inPlace && flagsLabel(one) && <span>{flagsLabel(one)}</span>}
        </p>
        {!inPlace && (
          <>
            <p className="text-meta text-muted-foreground">
              {[targetLabel(one), techniquesLabel(one)].filter(Boolean).join(' · ')}
            </p>
            <p className="text-meta text-muted-foreground tabular-nums">
              {difficultyLabel(one.score, one.difficulty, one.deviation)} · {counted(one.cases, 'case')}
            </p>
          </>
        )}
        {one.requests > 0 && (
          <Link to="/author#requests" className={`${link} block text-meta`}>
            {counted(one.requests, 'retirement request')}
          </Link>
        )}
      </header>
      <Loaded of={OF.author} state={read} blankWhen={() => false}>
        {(problem) => <Problem problem={problem} />}
      </Loaded>
      <footer className="flex flex-wrap gap-2">
        {problemCommands(one).map((command) => (
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
      </footer>
    </div>
  )
}

function Problem({ problem }: { problem: AuthorProblem }) {
  return (
    <>
      <p className="text-meta text-muted-foreground">{configurationLabel(problem.written_by)}</p>
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
