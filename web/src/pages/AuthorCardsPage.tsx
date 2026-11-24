import { Link, useSearchParams } from 'react-router'

import {
  AUTHOR_TITLE,
  BANK_CLEAR_LABEL,
  CARD_BANK_NONE,
  CARD_BANK_NONE_MATCH,
  CARD_BANK_TITLE,
  CARD_FILTERS,
  CARD_SUBTOPICS,
  CLOSE_ALL,
  LADDER,
  NO_RUNG,
  OF,
  OPEN_ALL,
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
  cardShapeLine,
  cardSubtopics,
  difficultyLabel,
  edgeLine,
  problemRowLink,
  shortId,
  subtopicLabel,
  templateCountsLine,
  templateProblemsLink,
  WRITTEN_FOR,
  type AuthorCard,
  type CardFilter,
} from '@climb/core'

import { api } from '@/api/client'
import { useLoaded } from '@/api/useLoaded'
import { AuthorBar } from '@/components/AuthorBar'
import { Chips } from '@/components/Chips'
import { Loaded } from '@/components/Loaded'
import { Markdown } from '@/components/Markdown'
import { PageHeader } from '@/components/PageHeader'
import { SectionHeading } from '@/components/SectionHeading'
import { TemplatePanel } from '@/components/TemplatePanel'
import { useLearner } from '@/knowledge/learner'
import { link, useOpenRows } from '@/lib/openRows'
import { subtopicPath } from '@/knowledge/paths'
import { NotFoundPage } from '@/pages/NotFoundPage'

// every card at once, its forms revealed: `web-app/pages/author/cards/`
export function AuthorCardsPage() {
  const me = useLoaded((signal) => api.GET('/api/me', { signal }), 'me')
  const area = useLoaded((signal) => api.GET('/api/author', { signal }), 'author')
  const cards = useLoaded((signal) => api.GET('/api/author/cards', { signal }), 'author-cards')
  const [search, setSearch] = useSearchParams()
  if (me.data && !me.data.author) return <NotFoundPage />
  const state = me.data ? cards : { retry: me.retry, error: me.error, data: undefined }

  return (
    <section className="space-y-section">
      <PageHeader
        back={{ to: '/author', label: AUTHOR_TITLE }}
        title={CARD_BANK_TITLE}
        aside={area.data && <AuthorBar area={area.data} />}
      />
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
            go={(next) => setSearch(new URLSearchParams(cardQuery(next)))}
          />
        )}
      </Loaded>
    </section>
  )
}

function Shelf({
  cards,
  filter,
  go,
}: {
  cards: AuthorCard[]
  filter: CardFilter
  go: (next: CardFilter) => void
}) {
  const view = cardBankView(cards, filter)
  const { open, setOpen, flip } = useOpenRows(view.rows.map((one) => one.card.slug))
  return (
    <div className="space-y-section">
      <section className="space-y-2">
        <Chips
          label={CARD_FILTERS.module}
          chips={view.modules}
          counted
          onPress={(value) => go(cardPressed(filter, 'module', value))}
        />
        <Chips
          label={CARD_FILTERS.depth}
          chips={view.depths}
          counted
          onPress={(value) => go(cardPressed(filter, 'depth', value))}
        />
      </section>
      <section className="space-y-stack">
        <SectionHeading
          title={CARD_BANK_TITLE}
          count={view.rows.length}
          aside={
            <span className="flex gap-3 text-meta text-muted-foreground">
              {view.filtered && (
                <button
                  type="button"
                  className={link}
                  onClick={() => go({ module: null, depth: null })}
                >
                  {BANK_CLEAR_LABEL}
                </button>
              )}
              <button
                type="button"
                className={link}
                onClick={() => setOpen(new Set(view.rows.map((one) => one.card.slug)))}
              >
                {OPEN_ALL}
              </button>
              <button type="button" className={link} onClick={() => setOpen(new Set())}>
                {CLOSE_ALL}
              </button>
            </span>
          }
        />
        {view.rows.length === 0 ? (
          <p className="text-meta text-muted-foreground">{CARD_BANK_NONE_MATCH}</p>
        ) : (
          <ul className="divide-y rounded-xl border bg-card">
            {view.rows.map((one) => (
              <Row
                key={one.card.slug}
                one={one}
                open={open.has(one.card.slug)}
                onFlip={() => flip(one.card.slug)}
              />
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}

function Row({ one, open, onFlip }: { one: AuthorCard; open: boolean; onFlip: () => void }) {
  const { card } = one
  const { catalog } = useLearner()
  const subtopics = cardSubtopics(catalog?.courses ?? [], card)
  const counts = new Map(one.counts.map((c) => [c.template_id, c]))
  return (
    <li id={card.slug} className="scroll-mt-4">
      <button
        type="button"
        aria-expanded={open}
        onClick={onFlip}
        className="flex w-full items-baseline gap-3 px-4 py-2 text-left hover:bg-accent"
      >
        <span className="text-muted-foreground">{open ? '▾' : '▸'}</span>
        <span className="min-w-0 flex-1 space-y-0.5">
          <span className="flex items-baseline gap-3">
            <code className="shrink-0 text-meta">{card.slug}</code>
            <span className="min-w-0 flex-1 truncate">{card.title}</span>
            <span className="shrink-0 text-meta text-muted-foreground">{cardHeadLine(one)}</span>
          </span>
          <span className="block text-meta text-muted-foreground">{cardShapeLine(one)}</span>
        </span>
      </button>
      {open && (
        <div className="space-y-stack px-4 pb-4">
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
            edges={(card.requires ?? []).map((e) => [
              e.card,
              edgeLine(e.card, e.template, e.used_by),
            ])}
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
        </div>
      )}
    </li>
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
