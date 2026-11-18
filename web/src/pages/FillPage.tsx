import {
  FILL_NEXT,
  FILL_NONE,
  FILL_NOTE,
  FILL_PICK,
  FILL_RIGHT,
  FILL_TITLE,
  FILL_WRONG,
  fill,
  filledLine,
  inBlank,
  judgeDepth,
  judgeExample,
  nextFilled,
  separatingLines,
} from '@climb/core'
import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router'

import { api } from '@/api/client'
import type { components } from '@climb/core'
import { ErrorLine } from '@/components/ErrorLine'
import { PageHeader } from '@/components/PageHeader'
import { Panel } from '@/components/Panel'
import { WrappedText } from '@/components/PythonCode'
import { Tag } from '@/components/Tag'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { exerciseBack } from '@/lib/paths'

type FilledItem = components['schemas']['FilledItem']
type FillDecided = components['schemas']['FillDecided']

// one item at a time: read the form, pick the blank's line, read the decision
// and a wrong choice's separating case, then Next. `pages.md`, Filling a key line
export function FillPage() {
  const [params] = useSearchParams()
  const card = params.get('card')
  const [item, setItem] = useState<FilledItem | null | undefined>(undefined)
  const [picked, setPicked] = useState<number | null>(null)
  const [decided, setDecided] = useState<FillDecided | null>(null)
  const [refused, setRefused] = useState<string | null>(null)
  const [round, setRound] = useState(0)

  useEffect(() => {
    let live = true
    void nextFilled(api, card).then((next) => {
      if (!live) return
      if (next.ok) setItem(next.value)
      else setRefused(next.refused)
    })
    return () => {
      live = false
    }
  }, [card, round])

  function another() {
    setPicked(null)
    setDecided(null)
    setRefused(null)
    setRound((one) => one + 1)
  }

  async function send(choice: number) {
    if (!item) return
    setPicked(choice)
    const answered = await fill(api, item.item_id, choice)
    if (answered.ok) setDecided(answered.value)
    else setRefused(answered.refused)
  }

  return (
    <section className="space-y-section">
      <PageHeader
        back={exerciseBack(card, item?.card_title)}
        title={item ? item.template_title : FILL_TITLE}
        note={item ? item.card_title : FILL_NOTE}
      />
      {refused && <ErrorLine>{refused}</ErrorLine>}
      {item === null && <p className="text-meta text-muted-foreground">{FILL_NONE}</p>}
      {item && (
        <div className="space-y-stack">
          <div className="flex items-center gap-2">
            <Tag>{judgeDepth(item.depth)}</Tag>
          </div>
          <p className="text-meta text-muted-foreground">{item.asks}</p>
          <p className="font-mono text-meta">{judgeExample(item.example)}</p>
          <Panel className="overflow-hidden p-0">
            <ol className="font-mono text-sm">
              {item.lines.map((_, index) => {
                const number = index + 1
                const blank = inBlank(item, index)
                return (
                  <li
                    key={number}
                    className={cn(
                      'flex gap-3 px-3 py-1',
                      blank && 'bg-muted',
                      blank &&
                        decided &&
                        (decided.right
                          ? 'border-l-4 border-verdict-passed'
                          : 'border-l-4 border-verdict-wrong'),
                    )}
                  >
                    <span className="w-6 shrink-0 text-right text-muted-foreground select-none">
                      {number}
                    </span>
                    {/* a wrap continues under the line's own indent: `pages.md` */}
                    <span className="min-w-0 flex-1 whitespace-pre">
                      <WrappedText code={filledLine(item, index, decided) || ' '} />
                    </span>
                  </li>
                )
              })}
            </ol>
          </Panel>

          {!decided && <p className="text-meta text-muted-foreground">{FILL_PICK}</p>}
          <div className="space-y-2">
            {item.choices.map((one) => (
              <Button
                key={one.choice}
                variant="outline"
                disabled={picked !== null}
                onClick={() => void send(one.choice)}
                className={cn(
                  'h-auto w-full justify-start py-2 text-left font-mono whitespace-pre-wrap',
                  picked === one.choice && 'bg-accent',
                )}
              >
                {one.text}
              </Button>
            ))}
          </div>

          {decided && (
            <Panel className="space-y-2">
              <p
                className={cn(
                  'font-medium',
                  decided.right ? 'text-verdict-passed' : 'text-verdict-wrong',
                )}
              >
                {decided.right ? FILL_RIGHT : FILL_WRONG}
              </p>
              {separatingLines(decided).map((line) => (
                <p key={line} className="font-mono text-meta">
                  {line}
                </p>
              ))}
              <Button onClick={another}>{FILL_NEXT}</Button>
            </Panel>
          )}
        </div>
      )}
    </section>
  )
}
