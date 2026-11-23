import {
  BACK_BOARD,
  CLAIM_NOTE,
  CLAIM_TITLE,
  COLD_END_TITLE,
  COLD_KEEP,
  COLD_SOLVED_LINE,
  COLD_TITLE,
  type ColdRead,
  coldEndNote,
  coldOutcome,
  coldVerdict,
  endCold,
  OF,
  problemCards,
  readCold,
  revealedFacts,
  secondsLeft,
  SITTING_END,
  SUBMIT_HINT,
  sittingRefused,
  submitCold,
  submitLabel,
  timeLeft,
  TOUCH_MS,
  cardsOffered,
} from '@climb/core'
import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router'

import { api } from '@/api/client'
import { useLoaded } from '@/api/useLoaded'
import { BackLink } from '@/components/BackLink'
import { ClaimPrompt } from '@/components/ClaimPrompt'
import { CodeEditor } from '@/components/CodeEditor'
import { ErrorLine } from '@/components/ErrorLine'
import { Loaded } from '@/components/Loaded'
import { Markdown } from '@/components/Markdown'
import { Panel } from '@/components/Panel'
import { ReportProblem } from '@/components/ReportProblem'
import { Tag } from '@/components/Tag'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { useKnowledge } from '@/knowledge/context'
import { draftOf, keepDraft } from '@/lib/draft'
import { cn } from '@/lib/utils'
import { OUTCOME } from '@/lib/verdicts'

const now = () => performance.now()

// a cold sitting, running or ended: the drill loop's sitting with what a cold
// sitting withholds left out, `web-app/pages/practice/cold/`
export function ColdSittingView({ sittingId }: { sittingId: string }) {
  const { user } = useKnowledge()
  const loaded = useLoaded(async (signal) => {
    const answer = await api.GET('/api/cold-sittings/{sitting_id}', {
      params: { path: { sitting_id: sittingId } },
      signal,
    })
    return { ...answer, data: answer.data && { seated: answer.data, at: now() } }
  }, `cold:${sittingId}`)
  // the reading a touch, a submission or the end left, over the first one
  const [read, setRead] = useState<ColdRead | null>(null)
  const [running, setRunning] = useState(false)
  const [refused, setRefused] = useState<string | null>(null)
  const [answered, setAnswered] = useState(false)
  const code = useRef<string | null>(null)

  const current = read ?? loaded.data ?? null
  const ended = current?.seated.sitting.ended_at != null

  async function reread() {
    const again = await readCold(api, sittingId, now)
    if (again.ok) setRead(again.value)
  }

  // a read touches the sitting, so the idle bound does not end it while the
  // user thinks; the cold clock runs on a hidden page too
  useEffect(() => {
    if (current === null || ended) return
    const tick = setInterval(() => void reread(), TOUCH_MS)
    return () => clearInterval(tick)
    // `reread` is a new closure on every render, and it reads `sittingId` alone
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [current === null, ended, sittingId])

  // at 0:00 the engine has ended the sitting at its limit, and the page reads
  // that end rather than deciding one of its own
  const left = current
    ? secondsLeft(current.seated.sitting, current.seated.elapsed_sec ?? null, current.at, now())
    : null
  useEffect(() => {
    if (left === null || ended) return
    const limit = setTimeout(() => void reread(), (left + 1) * 1000)
    return () => clearTimeout(limit)
    // timed once per reading: `left` moves on every render
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [current, ended])

  const cards = useLoaded(
    (signal) => (ended ? api.GET('/api/cards', { signal }) : Promise.resolve({ data: [] })),
    `cards:${ended}`,
  )

  if (current === null || user === null)
    return (
      <Loaded of={OF.problem} state={{ ...loaded, data: undefined }}>
        {() => null}
      </Loaded>
    )

  const { seated } = current
  const problemId = seated.sitting.problem_id
  const last = seated.last ?? null
  const solved = last?.attempt.solved === true
  const kept = draftOf(user, problemId)
  const initial =
    kept !== null && kept.sitting === sittingId
      ? kept.code
      : (last?.attempt.code ?? (seated.signature ? `${seated.signature}\n    ` : ''))
  const revealed = seated.revealed ?? null

  async function submit() {
    if (running || ended) return
    setRunning(true)
    setRefused(null)
    const sent = await submitCold(api, sittingId, code.current ?? initial, now)
    // the reading carries the verdict as `last`, and the engine's clock
    if (sent.ok) await reread()
    else setRefused(sent.refused)
    setRunning(false)
  }

  async function end() {
    setRefused(null)
    const out = await endCold(api, sittingId, now)
    if (out.ok) await reread()
    else setRefused(out.refused)
  }

  const facts = revealed && revealedFacts(revealed)
  const offered = revealed ? problemCards(cards.data ?? [], revealed.techniques, null) : []

  return (
    <div className="space-y-stack">
      <div className="sticky top-0 z-10 -mx-gutter border-b bg-background px-gutter">
        <div className="flex flex-wrap items-center gap-x-3 gap-y-2 py-2">
          <BackLink to="/" label={BACK_BOARD} />
          <h1 className="min-w-0 truncate text-heading font-semibold">
            {revealed?.title ?? COLD_TITLE}
          </h1>
          <div className="flex items-center gap-3 sm:ml-auto">
            {ended ? (
              <span className="text-meta font-medium">{coldOutcome(last)}</span>
            ) : (
              <>
                <ColdClock read={current} />
                <AlertDialog>
                  <AlertDialogTrigger asChild>
                    <Button variant="outline" size="sm">
                      {SITTING_END}
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>{COLD_END_TITLE}</AlertDialogTitle>
                      <AlertDialogDescription>{coldEndNote(solved)}</AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel>{COLD_KEEP}</AlertDialogCancel>
                      <AlertDialogAction onClick={() => void end()}>
                        {SITTING_END}
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </>
            )}
          </div>
        </div>
      </div>
      {refused && <ErrorLine>{sittingRefused(refused)}</ErrorLine>}
      {solved && !ended && <p className="text-meta text-muted-foreground">{COLD_SOLVED_LINE}</p>}
      <div className="grid grid-cols-1 gap-gutter lg:grid-cols-2">
        <section className="space-y-stack">
          {facts && (
            <p className="flex flex-wrap items-center gap-x-4 gap-y-1 text-meta text-muted-foreground">
              <Tag>{facts.difficulty}</Tag>
              <span>{facts.techniques}</span>
              {offered.length > 0 && (
                <span>
                  {cardsOffered(offered.length)}{' '}
                  {offered.map((card, index) => (
                    <span key={card.slug}>
                      {index > 0 && ', '}
                      <Link
                        to={`/cards/${encodeURIComponent(card.slug)}`}
                        className="font-medium text-foreground underline-offset-4 hover:underline"
                      >
                        {card.title}
                      </Link>
                    </span>
                  ))}
                </span>
              )}
            </p>
          )}
          <Markdown>{seated.statement}</Markdown>
          {/* the retirement dialog names the problem, so it waits for the end */}
          {ended && <ReportProblem problemId={problemId} />}
        </section>
        <section className="flex flex-col gap-stack lg:sticky lg:top-6 lg:h-[calc(100vh-10rem)]">
          <div className="min-h-96 flex-1 lg:min-h-48">
            <CodeEditor
              // the end replaces the editor with the submitted code, read-only
              key={String(ended)}
              initial={ended ? (last?.attempt.code ?? initial) : initial}
              onChange={(typed) => {
                code.current = typed
                keepDraft(user, problemId, sittingId, typed)
              }}
              onSubmit={submit}
              readOnly={ended}
            />
          </div>
          <div className="flex flex-wrap items-center gap-stack">
            <Button onClick={submit} disabled={running || ended}>
              {submitLabel(running)}
            </Button>
            <span className="hidden text-meta text-muted-foreground sm:inline">{SUBMIT_HINT}</span>
          </div>
          {last && (
            <Panel>
              <p
                className={cn(
                  'font-medium',
                  OUTCOME[solved ? 'passed' : (last.failure?.outcome ?? 'wrong')].text,
                )}
              >
                {coldVerdict(last)}
              </p>
            </Panel>
          )}
        </section>
      </div>
      {/* the claim's candidates name techniques, so it is asked at the end alone */}
      <Dialog
        open={ended && last !== null && !answered}
        onOpenChange={(open) => open || setAnswered(true)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{CLAIM_TITLE}</DialogTitle>
            <DialogDescription>{CLAIM_NOTE}</DialogDescription>
          </DialogHeader>
          {ended && (
            <ClaimPrompt sittingId={sittingId} drilled={null} onDone={() => setAnswered(true)} />
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}

// its own component: it re-renders every second, and the editor beside it must not
function ColdClock({ read }: { read: ColdRead }) {
  const [at, setAt] = useState(() => now())
  useEffect(() => {
    const tick = setInterval(() => setAt(now()), 1000)
    return () => clearInterval(tick)
  }, [])
  const left = secondsLeft(read.seated.sitting, read.seated.elapsed_sec ?? null, read.at, at)
  return <span className="font-mono text-heading tabular-nums">{timeLeft(left)}</span>
}
