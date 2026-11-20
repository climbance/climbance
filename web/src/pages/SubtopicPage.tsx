import { useMemo } from 'react'
import { Link, useParams } from 'react-router'

import {
  lessonRow,
  lessonStats,
  OF,
  SUBTOPIC_CARDS,
  SUBTOPIC_LESSONS,
  SUBTOPIC_LEVELS,
  SUBTOPIC_MISSING,
  SUBTOPIC_NO_LESSONS,
  subtopicCards,
  subtopicView,
} from '@climb/core'

import { api } from '@/api/client'
import { useLoaded } from '@/api/useLoaded'
import { Loaded } from '@/components/Loaded'
import { PageHeader } from '@/components/PageHeader'
import { PickList, PickRow } from '@/components/PickRow'
import { SectionHeading } from '@/components/SectionHeading'
import { loadedFrom, useKnowledge } from '@/knowledge/context'
import { useLearner } from '@/knowledge/learner'
import { lessonPath, modulePath } from '@/knowledge/paths'

// a subtopic's levels, its lessons and its cards: `web-app/pages/knowledge/subtopic/`. Its
// presses stay on the module's page, so none drifts apart
export function SubtopicPage() {
  const { module = '', sub = '' } = useParams()
  const k = useKnowledge()
  const { catalog, board } = useLearner()
  // the cards add to the page, so a failed list reads as none
  const listed = useLoaded((signal) => api.GET('/api/cards', { signal }), 'cards')
  const page = useMemo(() => {
    const c = catalog?.courses.find((one) => one.slug === module)
    const b = board(null)
    if (!catalog || !b) return undefined
    return { c, view: c ? subtopicView(b, c, sub) : null, b }
  }, [catalog, board, module, sub])
  const c = page?.c

  return (
    <section className="space-y-section">
      <PageHeader
        back={{ to: modulePath(module), label: c?.title ?? module }}
        title={page?.view?.title ?? sub}
      />
      <Loaded
        of={OF.subtopic}
        state={loadedFrom(k, page)}
        blank={SUBTOPIC_MISSING}
        blankWhen={(one) => !one.view}
      >
        {({ c, view, b }) => {
          if (!c || !view) return null
          const cards = subtopicCards(c, sub, listed.data ?? [])
          return (
            <div className="space-y-section">
              {view.levels.length > 0 && (
                <section className="space-y-1">
                  <SectionHeading sub title={SUBTOPIC_LEVELS} />
                  {view.levels.map((line) => (
                    <p key={line} className="text-meta">
                      {line}
                    </p>
                  ))}
                </section>
              )}
              <section className="space-y-stack">
                <SectionHeading title={SUBTOPIC_LESSONS} count={view.lessons.length} />
                {view.lessons.length > 0 ? (
                  <PickList>
                    {view.lessons.map((x) => {
                      const row = lessonRow(b, c, x)
                      return (
                        <PickRow
                          key={x.slug}
                          to={lessonPath(c.slug, x.slug)}
                          title={x.title}
                          stats={lessonStats(row.status, row.minutes)}
                          dim={row.state === 'locked'}
                        />
                      )
                    })}
                  </PickList>
                ) : (
                  <p className="text-meta text-muted-foreground">{SUBTOPIC_NO_LESSONS}</p>
                )}
              </section>
              {cards.length > 0 && (
                <section className="space-y-1">
                  <SectionHeading sub title={SUBTOPIC_CARDS} />
                  <p className="flex flex-wrap gap-x-4">
                    {cards.map((card) => (
                      <Link
                        key={card.slug}
                        to={`/cards/${encodeURIComponent(card.slug)}`}
                        className="font-medium underline-offset-4 hover:underline"
                      >
                        {card.title}
                      </Link>
                    ))}
                  </p>
                </section>
              )}
            </div>
          )
        }}
      </Loaded>
    </section>
  )
}
