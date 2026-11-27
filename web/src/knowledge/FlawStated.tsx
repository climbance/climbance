import { FLAW_CLEAN, FLAW_TAP, flawFixShown, flawLines, type Question } from '@climb/core'

import { Panel } from '@/components/Panel'
import { WrappedText } from '@/components/PythonCode'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

/**
 * A spot-the-flaw drill's lines, each a tap target until answered, then the
 * flawed span marked and what it reads clean. `content-repo/ai-drills.md`
 */
export function FlawStated({
  q,
  tapped,
  answered,
  onTap,
}: {
  q: Question
  tapped: number | null
  answered: boolean
  onTap?: (line: number) => void
}) {
  if (!q.judge) return null
  const fix = answered ? flawFixShown(q) : null
  return (
    <div className="space-y-2">
      <Panel className="overflow-hidden p-0">
        <ol className="font-mono text-sm">
          {flawLines(q, tapped, answered).map((line) => (
            <li key={line.n}>
              <button
                type="button"
                disabled={!onTap}
                onClick={() => onTap?.(line.n)}
                className={cn(
                  'flex w-full gap-3 px-3 py-1 text-left disabled:cursor-default',
                  onTap && 'hover:bg-accent',
                  line.tapped && 'bg-accent',
                  line.flawed && 'border-l-4 border-verdict-wrong',
                )}
              >
                <span className="w-6 shrink-0 text-right text-muted-foreground select-none">
                  {line.n}
                </span>
                <span className="min-w-0 flex-1 whitespace-pre">
                  <WrappedText code={line.text || ' '} />
                </span>
              </button>
            </li>
          ))}
        </ol>
      </Panel>
      {fix && (
        <div>
          <p className="text-meta text-muted-foreground">{fix.label}</p>
          <pre className="font-mono text-sm whitespace-pre-wrap">{fix.code}</pre>
        </div>
      )}
    </div>
  )
}

/** Before the answer: the press calling the lines correct, beside the hint to tap instead. */
export function FlawCall({ on, onClean }: { on: boolean; onClean: () => void }) {
  return (
    <div className="flex flex-wrap items-center gap-stack">
      <Button variant={on ? 'default' : 'outline'} aria-pressed={on} onClick={onClean}>
        {FLAW_CLEAN}
      </Button>
      <p className="text-meta text-muted-foreground">{FLAW_TAP}</p>
    </div>
  )
}
