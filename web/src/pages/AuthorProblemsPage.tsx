import { ChevronLeft, ChevronRight, Copy } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link, useLocation, useNavigate, useSearchParams } from 'react-router'

import {
  BANK_CLEAR_LABEL,
  CASES,
  COPY,
  MENU_SORT,
  DIFFICULTY,
  NO_CASE,
  NO_RATING,
  NEXT_PROBLEM,
  NO_SITE,
  NO_SOLUTION,
  OF,
  PREVIOUS_PROBLEM,
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
  flagsLabel,
  generatorLabel,
  problemBankView,
  problemCommands,
  problemFilter,
  problemPicked,
  problemQuery,
  positionLabel,
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
import { FilterMenu } from '@/components/FilterMenu'
import { Loaded } from '@/components/Loaded'
import { Markdown } from '@/components/Markdown'
import { PageHeader } from '@/components/PageHeader'
import { PlainCode, PythonCode } from '@/components/PythonCode'
import { SectionHeading } from '@/components/SectionHeading'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogTitle } from '@/components/ui/dialog'
import { link } from '@/lib/openRows'
import { stepKey, useStepKeys } from '@/lib/stepRows'
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
  const anchor = decodeURIComponent(location.hash.slice(1))
  const keys = view.rows.map((one) => shortId(one.problem_id))
  const at = keys.indexOf(anchor)
  const opened = at < 0 ? undefined : view.rows[at]
  // the row last opened stays marked once the dialog closes, and a step resumes from it
  const [last, setLast] = useState<string | null>(opened ? anchor : null)
  if (opened && last !== anchor) setLast(anchor)
  const open = (key: string) => navigate({ search: location.search, hash: key }, { replace: true })
  const close = () => {
    navigate({ search: location.search, hash: '' }, { replace: true })
    // the list scrolled under the dialog only on arrival, so the row is brought back into view
    if (last)
      requestAnimationFrame(() =>
        document.getElementById(last)?.scrollIntoView({ block: 'nearest' }),
      )
  }
  const step = (by: 1 | -1) => {
    const next = stepKey(keys, opened ? anchor : last, by)
    if (next !== undefined) open(next)
  }
  useStepKeys(step)
  // a link to `#<id>` scrolls to its row on arrival
  useEffect(() => {
    if (anchor) document.getElementById(anchor)?.scrollIntoView({ block: 'center' })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])
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
                <button
                  type="button"
                  className={link}
                  onClick={() => go({ ...PROBLEM_CLEARED, sort: filter.sort })}
                >
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
          <ul className="divide-y rounded-xl border bg-card">
            {view.rows.map((one) => (
              <Row
                key={one.problem_id}
                one={one}
                marked={shortId(one.problem_id) === last}
                onPress={() => open(shortId(one.problem_id))}
              />
            ))}
          </ul>
        )}
      </section>
      <Dialog open={opened !== undefined} onOpenChange={(now) => !now && close()}>
        {opened && (
          <DialogContent
            // j and k step inside this dialog: `lib/stepRows.ts`
            data-steps
            aria-describedby={undefined}
            // the dialog itself takes the focus, so no step button opens ringed
            onOpenAutoFocus={(event) => {
              event.preventDefault()
              ;(event.currentTarget as HTMLElement).focus()
            }}
            className="flex h-dvh w-screen max-w-none flex-col gap-0 rounded-none p-0 sm:max-w-none lg:h-[calc(100dvh-3rem)] lg:w-[calc(100vw-3rem)] lg:rounded-xl"
          >
            <Opened
              key={opened.problem_id}
              one={opened}
              position={positionLabel(at + 1, keys.length)}
              step={step}
            />
          </DialogContent>
        )}
      </Dialog>
    </div>
  )
}

function Row({
  one,
  marked,
  onPress,
}: {
  one: AuthorProblemRow
  marked: boolean
  onPress: () => void
}) {
  return (
    <li id={shortId(one.problem_id)} className="scroll-mt-4">
      <button
        type="button"
        aria-haspopup="dialog"
        onClick={onPress}
        className={cn(
          'flex w-full items-baseline gap-3 px-4 py-2 text-left hover:bg-accent',
          marked && 'bg-accent',
        )}
      >
        {/* narrow, the break puts the techniques, the cases and the flags on a second line, and the target too on a phone */}
        <span className="flex min-w-0 flex-1 flex-wrap items-baseline gap-x-3 lg:flex-nowrap">
          <span className="order-1 min-w-32 flex-1 truncate">{one.title}</span>
          <span className="order-4 shrink-0 text-meta text-muted-foreground sm:order-2">
            {targetLabel(one)}
          </span>
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
    </li>
  )
}

// a case may weigh up to the ceiling, so an opened problem is read alone
function Opened({
  one,
  position,
  step,
}: {
  one: AuthorProblemRow
  position: string
  step: (by: 1 | -1) => void
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
    <>
      <header className="space-y-1 border-b px-5 py-3 pr-12">
        <div className="flex items-baseline gap-3">
          <span className="flex shrink-0 items-baseline gap-1 text-meta text-muted-foreground">
            <Button
              variant="ghost"
              size="icon-xs"
              aria-label={PREVIOUS_PROBLEM}
              onClick={() => step(-1)}
            >
              <ChevronLeft />
            </Button>
            <Button
              variant="ghost"
              size="icon-xs"
              aria-label={NEXT_PROBLEM}
              onClick={() => step(1)}
            >
              <ChevronRight />
            </Button>
            <span className="tabular-nums">{position}</span>
          </span>
          <DialogTitle className="min-w-0 truncate text-heading">{one.title}</DialogTitle>
        </div>
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
      </header>
      <div className="min-h-0 flex-1 overflow-y-auto lg:overflow-hidden">
        <Loaded of={OF.author} state={read} blankWhen={() => false}>
          {(problem) => <Problem problem={problem} />}
        </Loaded>
      </div>
      <footer className="flex flex-wrap gap-2 border-t px-5 py-3">
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
    </>
  )
}

// two columns, each scrolling on its own, in a wide window; stacked below 64rem
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
