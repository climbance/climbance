import { Link, useSearchParams } from 'react-router'

import {
  BANK_CLEAR_LABEL,
  CARD_BANK_NONE,
  CARD_BANK_NONE_MATCH,
  CARD_BANK_TITLE,
  CARD_COLUMNS,
  CARD_FILTERS,
  CARD_SUBTOPICS,
  LADDER,
  NO_RUNG,
  OF,
  REQUIRED,
  REQUIRED_BY,
  REQUIRES,
  briefParts,
  cardBankView,
  cardFilter,
  cardHeadLine,
  cardPressed,
  cardQuery,
  cardRowLink,
  cardSubtopics,
  difficultyLabel,
  edgeLine,
  formsLabel,
  gridPage,
  gridQuery,
  gridSort,
  gridSorted,
  problemRowLink,
  rungsLabel,
  shortId,
  subtopicLabel,
  templateCountsLine,
  templateProblemsLink,
  WRITTEN_FOR,
  type AuthorCard,
  type AuthorCardRow,
  type CardFilter,
  type GridSort,
} from '@climb/core'

import { api } from '@/api/client'
import { useLoaded } from '@/api/useLoaded'
import { Chips } from '@/components/Chips'
import { DataGrid, type GridCells } from '@/components/DataGrid'
import { Loaded } from '@/components/Loaded'
import { Markdown } from '@/components/Markdown'
import { PageHeader } from '@/components/PageHeader'
import { Pager } from '@/components/Pager'
import { RowDialog } from '@/components/RowDialog'
import { SectionHeading } from '@/components/SectionHeading'
import { TemplatePanel } from '@/components/TemplatePanel'
import { useLearner } from '@/knowledge/learner'
import { subtopicPath } from '@/knowledge/paths'
import { link } from '@/lib/openRows'
import { useRowDialog } from '@/lib/rowDialog'
import { cn } from '@/lib/utils'
import { NotFoundPage } from '@/pages/NotFoundPage'

// every card at once, each opened with its forms revealed: `web-app/pages/author/cards/`
export function AuthorCardsPage() {
  const me = useLoaded((signal) => api.GET('/api/me', { signal }), 'me')
  const cards = useLoaded((signal) => api.GET('/api/author/cards', { signal }), 'author-cards')
  const [search, setSearch] = useSearchParams()
  if (me.data && !me.data.author) return <NotFoundPage />
  const state = me.data ? cards : { retry: me.retry, error: me.error, data: undefined }

  return (
    <section className="space-y-section">
      <PageHeader title={CARD_BANK_TITLE} />
      <Loaded
        of={OF.author}
        state={state}
        blank={CARD_BANK_NONE}
        blankWhen={(read) => !read.cards.length}
      >
        {(read) => (
          <Shelf
            cards={read.cards}
            filter={cardFilter((name) => search.get(name))}
            sort={gridSort((name) => search.get(name), CARD_COLUMNS)}
            go={(next, sort) =>
              setSearch(new URLSearchParams(gridQuery(cardQuery(next), sort, CARD_COLUMNS)))
            }
          />
        )}
      </Loaded>
    </section>
  )
}

const quiet = 'whitespace-nowrap text-muted-foreground'

const cardCells: GridCells<AuthorCardRow> = {
  slug: { cell: (one) => <code>{one.slug}</code>, className: 'max-w-56 truncate' },
  title: { cell: (one) => one.title, className: 'text-body', grow: true },
  technique: { cell: (one) => one.technique, className: quiet },
  module: { cell: (one) => one.module, className: quiet },
  depth: { cell: (one) => one.depth, className: quiet },
  templates: { cell: formsLabel, className: quiet },
  rungs: { cell: rungsLabel, className: quiet },
  gaps: { cell: (one) => one.gaps.length || '', className: 'whitespace-nowrap' },
}

function Shelf({
  cards,
  filter,
  sort,
  go,
}: {
  cards: AuthorCardRow[]
  filter: CardFilter
  sort: GridSort | null
  go: (next: CardFilter, sort: GridSort | null) => void
}) {
  const view = cardBankView(cards, filter)
  const shown = gridSorted(view.rows, CARD_COLUMNS, sort)
  const dialog = useRowDialog(shown.map((one) => one.slug))
  const opened = shown.find((one) => one.slug === dialog.opened)
  const paged = gridPage(shown, dialog.page)
  return (
    <div className="space-y-section">
      <section className="space-y-2">
        <Chips
          label={CARD_FILTERS.module}
          chips={view.modules}
          counted
          onPress={(value) => go(cardPressed(filter, 'module', value), sort)}
        />
        <Chips
          label={CARD_FILTERS.depth}
          chips={view.depths}
          counted
          onPress={(value) => go(cardPressed(filter, 'depth', value), sort)}
        />
      </section>
      <section className="space-y-stack">
        <SectionHeading
          title={CARD_BANK_TITLE}
          count={shown.length}
          aside={
            view.filtered && (
              <button
                type="button"
                className={cn(link, 'text-meta text-muted-foreground')}
                onClick={() => go({ module: null, depth: null }, sort)}
              >
                {BANK_CLEAR_LABEL}
              </button>
            )
          }
        />
        {shown.length === 0 ? (
          <p className="text-meta text-muted-foreground">{CARD_BANK_NONE_MATCH}</p>
        ) : (
          <>
            <DataGrid
              columns={CARD_COLUMNS}
              cells={cardCells}
              rows={paged.rows}
              rowKey={(one) => one.slug}
              marked={dialog.last}
              onOpen={dialog.open}
              sort={sort}
              onSort={(next) => go(filter, next)}
            />
            <Pager page={paged.page} pages={paged.pages} onPage={dialog.turn} />
          </>
        )}
      </section>
      {opened && (
        <RowDialog
          dialog={dialog}
          title={opened.title}
          head={<p className="text-meta text-muted-foreground">{cardHeadLine(opened)}</p>}
        >
          <Opened key={opened.slug} slug={opened.slug} />
        </RowDialog>
      )}
    </div>
  )
}

// the card's text, its code and its ladder are read for the opened card alone
function Opened({ slug }: { slug: string }) {
  const read = useLoaded(
    (signal) => api.GET('/api/author/cards/{slug}', { params: { path: { slug } }, signal }),
    `author-card:${slug}`,
  )
  return (
    <Loaded of={OF.author} state={read} blankWhen={() => false}>
      {(one) => <Card one={one} />}
    </Loaded>
  )
}

function Card({ one }: { one: AuthorCard }) {
  const { card } = one
  const { catalog } = useLearner()
  const subtopics = cardSubtopics(catalog?.courses ?? [], card)
  const counts = new Map(one.counts.map((c) => [c.template_id, c]))
  return (
    <>
      {subtopics.length > 0 && (
        <p className="flex flex-wrap gap-x-4 text-meta">
          <span className="text-muted-foreground">{CARD_SUBTOPICS}</span>
          {subtopics.map((sub) => (
            <Link
              key={`${sub.module}/${sub.sub}`}
              to={subtopicPath(sub.module, sub.sub)}
              className={link}
            >
              {subtopicLabel(sub)}
            </Link>
          ))}
        </p>
      )}
      <Markdown>{card.trigger}</Markdown>
      {briefParts(card.brief).map((part) => (
        <section key={part.id} className="space-y-1">
          <SectionHeading sub title={part.title} />
          <Markdown>{part.text}</Markdown>
        </section>
      ))}
      {card.templates.map((template) => (
        <div key={template.slug} className="space-y-1">
          <TemplatePanel template={template} card={card.slug} recalled={undefined} review />
          <p className="flex flex-wrap gap-x-3 text-meta text-muted-foreground">
            <span>{templateCountsLine(counts.get(template.id))}</span>
            <Link to={templateProblemsLink(template.slug)} className={link}>
              {WRITTEN_FOR}
            </Link>
          </p>
        </div>
      ))}
      <Edges
        label={REQUIRES}
        edges={(card.requires ?? []).map((e) => [e.card, edgeLine(e.card, e.template, e.used_by)])}
      />
      <Edges
        label={REQUIRED_BY}
        edges={one.required_by.map((e) => [e.card, edgeLine(e.card, e.template, e.used_by)])}
      />
      <section className="space-y-1">
        <SectionHeading sub title={LADDER} count={one.rungs.length} />
        {one.rungs.length === 0 ? (
          <p className="text-meta text-muted-foreground">{NO_RUNG}</p>
        ) : (
          <ul className="space-y-0.5 text-meta">
            {one.rungs.map((rung) => (
              <li key={rung.problem_id} className="flex items-baseline gap-3">
                <Link to={problemRowLink(rung.problem_id)} className={link}>
                  <code>{shortId(rung.problem_id)}</code>
                </Link>
                <span className="min-w-0 flex-1 truncate">{rung.title}</span>
                <span className="text-muted-foreground">{rung.templates.join(', ')}</span>
                <span className="tabular-nums text-muted-foreground">
                  {difficultyLabel(rung.score, rung.difficulty)}
                </span>
                {rung.required && <span className="text-muted-foreground">{REQUIRED}</span>}
              </li>
            ))}
          </ul>
        )}
      </section>
    </>
  )
}

function Edges({ label, edges }: { label: string; edges: [string, string][] }) {
  if (!edges.length) return null
  return (
    <p className="flex flex-wrap gap-x-4 text-meta">
      <span className="text-muted-foreground">{label}</span>
      {edges.map(([slug, line]) => (
        <Link key={line} to={cardRowLink(slug)} className={link}>
          {line}
        </Link>
      ))}
    </p>
  )
}
