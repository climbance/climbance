import { useMemo } from 'react'

import {
  boardView,
  inProgress,
  BOARD_TITLE,
  BOARD_NOTE,
  OF,
  BOARD_NONE,
  BOARD_STUDYING,
  BOARD_NEXT,
  FILL_NOTE,
  FILL_TITLE,
  JUDGE_NOTE,
  JUDGE_TITLE,
  boardMoreCards,
  nextCards,
  BOARD_UNTOUCHED,
  BOARD_PRACTISED,
  MODULES_HEADING,
  orderedModuleRows,
  techniqueKnowledge,
  pickView,
  takePick,
  showsGuidePanel,
  GUIDE_LINK,
  GUIDE_PANEL_NOTE,
  GUIDE_PANEL_TITLE,
  type PickTarget,
} from '@climb/core'
import { Link } from 'react-router'

import { api, type TechniqueRow } from '@/api/client'
import { useLoaded } from '@/api/useLoaded'
import { CardPanel } from '@/components/CardPanel'
import { Loaded } from '@/components/Loaded'
import { PageHeader } from '@/components/PageHeader'
import { PageSection } from '@/components/PageSection'
import { PickList, PickPanel, PickRow } from '@/components/PickRow'
import { SectionHeading } from '@/components/SectionHeading'
import { useLearner } from '@/knowledge/learner'
import { KnowledgeNext } from '@/knowledge/KnowledgeNext'
import { ModuleRow } from '@/knowledge/ModuleRow'
import { counts } from '@/lib/format'

export function BoardPage() {
  const board = useLoaded((signal) => api.GET('/api/board', { signal }), 'board')
  // the cards in progress read as the cards list draws them, so one card reads
  // one way on both pages
  const cards = useLoaded((signal) => api.GET('/api/cards', { signal }), 'cards')
  // the pick only adds to the board, so a failed one reads as none
  const pick = useLoaded((signal) => api.GET('/api/pick', { signal }), 'pick')
  const studying = inProgress(cards.data ?? [])
  const next = nextCards(cards.data ?? [], pick.data?.card_slug ?? null)
  const { catalog, board: learnerBoard, order, now, acted, ready } = useLearner()
  const all = useMemo(() => (catalog ? learnerBoard(null) : null), [catalog, learnerBoard])
  const modules = useMemo(() => (all ? orderedModuleRows(all, order, now) : []), [all, order, now])
  // the knowledge reading, from the device's copy: `api/mastery.md`
  const known = (row: TechniqueRow) => (all ? techniqueKnowledge(all, row) : null)

  return (
    <section className="space-y-section">
      <PageHeader title={BOARD_TITLE} note={BOARD_NOTE} />
      {showsGuidePanel(board.data, { ready, acted }) && (
        <section className="space-y-stack">
          <SectionHeading title={GUIDE_PANEL_TITLE} />
          <PickPanel>
            <PickRow to="/start" title={GUIDE_LINK} note={GUIDE_PANEL_NOTE} stats={[]} />
          </PickPanel>
        </section>
      )}
      {/* the knowledge study first, from the device's copy, so it reads before
          and without the engine's answer: `web-app/pages/practice/board/` */}
      <KnowledgeNext controls={false} />
      {modules.length > 0 && (
        <section className="space-y-stack">
          <SectionHeading title={MODULES_HEADING} count={modules.length} />
          <PickPanel>
            {modules.map((row) => (
              <ModuleRow key={row.c.slug} row={row} from="board" />
            ))}
          </PickPanel>
        </section>
      )}
      <Loaded
        of={OF.board}
        state={board}
        blank={BOARD_NONE}
        blankWhen={(one) => one.rows.length === 0}
      >
        {(board) => {
          // a technique never practised ranks stalest, so the untouched ones
          // come first. As names alone they stay one glance rather than thirty
          // rows of zeros
          const { untouched, practised, foot } = boardView(board, known)

          return (
            <div className="space-y-section">
              {/* the schedule's one act, above every list: `flows.md`, The pick */}
              {pick.data && <BoardPick pick={pick.data} />}

              {/* the study the user declared, ahead of any staleness ranking */}
              {studying.length > 0 && (
                <section className="space-y-stack">
                  <SectionHeading title={BOARD_STUDYING} count={studying.length} />
                  <CardPanel technique={null} cards={studying} />
                </section>
              )}

              {/* the short exercises, across every card: `web-app/pages/cards/judging/` and `web-app/pages/cards/key-line/` */}
              <PickPanel>
                <PickRow to="/judge" title={JUDGE_TITLE} note={JUDGE_NOTE} stats={[]} />
                <PickRow to="/fill" title={FILL_TITLE} note={FILL_NOTE} stats={[]} />
              </PickPanel>

              {/* what the card graph opens next, the shallowest first */}
              {next.cards.length > 0 && (
                <section className="space-y-stack">
                  <SectionHeading title={BOARD_NEXT} count={next.cards.length + next.more} />
                  <CardPanel technique={null} cards={next.cards} />
                  {next.more > 0 && (
                    <Link
                      to="/cards"
                      className="text-meta text-muted-foreground underline-offset-4 hover:underline"
                    >
                      {boardMoreCards(next.more)}
                    </Link>
                  )}
                </section>
              )}

              {untouched.length > 0 && (
                <PageSection
                  id="untouched"
                  title={BOARD_UNTOUCHED}
                  count={untouched.length}
                  body="rows"
                >
                  {/* names rather than chips: a bordered chip is what the
                      listing's filters are, and these open a technique */}
                  <div className="flex flex-wrap gap-x-5 gap-y-1 px-4 py-3">
                    {untouched.map((row) => (
                      <Link
                        key={row.technique}
                        to={`/techniques/${encodeURIComponent(row.technique)}`}
                        className="font-medium underline-offset-4 hover:underline"
                      >
                        {row.technique}
                      </Link>
                    ))}
                  </div>
                </PageSection>
              )}

              {practised.length > 0 && (
                <PageSection
                  id="practised"
                  title={BOARD_PRACTISED}
                  count={practised.length}
                  body="rows"
                >
                  <PickList>
                    {practised.map((row) => (
                      <Practised key={row.technique} row={row} known={known(row)} />
                    ))}
                  </PickList>
                </PageSection>
              )}

              {/* the attempts no row holds, on one line under the lists */}
              {foot && <p className="text-meta text-muted-foreground">{foot}</p>}
            </div>
          )
        }}
      </Loaded>
    </section>
  )
}

function Practised({
  row,
  known,
}: {
  row: TechniqueRow
  known: ReturnType<typeof techniqueKnowledge>
}) {
  return (
    <PickRow
      to={`/techniques/${encodeURIComponent(row.technique)}`}
      title={row.technique}
      stats={counts(row, known)}
    />
  )
}

// a route per target, as the cards list and the card's page open the same acts
function pickPath(target: PickTarget): string {
  const card = encodeURIComponent(target.card)
  if (target.kind === 'recall')
    return `/cards/${card}/recall/${encodeURIComponent(target.template)}`
  if (target.kind === 'problem')
    return `/problems/${encodeURIComponent(target.problem)}?card=${card}`
  return `/cards/${card}`
}

function BoardPick({ pick }: { pick: Parameters<typeof pickView>[0] }) {
  const view = pickView(pick)
  return (
    <section className="space-y-stack">
      <SectionHeading title={view.heading} />
      {/* the prediction is stored as the link opens the act: `api/predictions.md` */}
      <div onClickCapture={() => void takePick(api, pick)}>
        <PickPanel>
          <PickRow to={pickPath(view.target)} title={view.title} note={view.note} stats={[]} />
        </PickPanel>
      </div>
    </section>
  )
}
