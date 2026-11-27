import { TRACE_TAP, traceCorrectedShown, traceRows, type Question, type TraceRow } from '@climb/core'

import { Panel } from '@/components/Panel'
import { cn } from '@/lib/utils'

/**
 * A read-the-trace drill's steps, each a tap target until answered, then the
 * first wrong step marked and the corrected run. `content-repo/ai-drills.md`
 */
export function TraceStated({
  q,
  tapped,
  answered,
  onTap,
}: {
  q: Question
  tapped: number | null
  answered: boolean
  onTap?: (step: number) => void
}) {
  if (!q.trace) return null
  const corrected = answered ? traceCorrectedShown(q) : null
  return (
    <div className="space-y-2">
      <Steps rows={traceRows(q, tapped, answered)} onTap={onTap} />
      {!answered && <p className="text-meta text-muted-foreground">{TRACE_TAP}</p>}
      {corrected && (
        <div className="space-y-1">
          <p className="text-meta text-muted-foreground">{corrected.label}</p>
          <Steps rows={corrected.rows} />
        </div>
      )}
    </div>
  )
}

function Steps({ rows, onTap }: { rows: TraceRow[]; onTap?: (step: number) => void }) {
  return (
    <Panel className="overflow-hidden p-0">
      <ol className="text-sm">
        {rows.map((row) => (
          <li key={row.n}>
            <button
              type="button"
              disabled={!onTap}
              onClick={() => onTap?.(row.n)}
              className={cn(
                'flex w-full gap-3 px-3 py-1.5 text-left disabled:cursor-default',
                onTap && 'hover:bg-accent',
                row.tapped && 'bg-accent',
                row.wrong && 'border-l-4 border-verdict-wrong',
              )}
            >
              <span className="w-6 shrink-0 text-right font-mono text-muted-foreground select-none">
                {row.n}
              </span>
              {row.call !== null ? (
                <span className="min-w-0 flex-1 font-mono">
                  <span className="block whitespace-pre-wrap">{row.call}</span>
                  <span className="block whitespace-pre-wrap text-muted-foreground">
                    → {row.result}
                  </span>
                </span>
              ) : (
                <span className="min-w-0 flex-1">{row.say}</span>
              )}
            </button>
          </li>
        ))}
      </ol>
    </Panel>
  )
}
