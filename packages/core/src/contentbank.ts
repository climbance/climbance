import type { components } from './api/schema';
import type { BankChip } from './bank';
import { DIFFICULTIES } from './listing';
import { counted } from './screens';

// the author's cards and problems pages: `web-app/pages/author/cards/` and
// `web-app/pages/author/problems/`

export type AuthorCard = components['schemas']['AuthorCard'];
export type AuthorRung = components['schemas']['AuthorRung'];
export type AuthorProblemRow = components['schemas']['AuthorProblemRow'];
export type AuthorProblem = components['schemas']['AuthorProblem'];
type TemplateCounts = components['schemas']['TemplateCounts'];

export const CARD_BANK_TITLE = 'Cards';
export const PROBLEM_BANK_TITLE = 'Problems';
export const CARD_BANK_NONE = 'No card is seeded.';
export const CARD_BANK_NONE_MATCH = 'No card matches these filters.';
export const PROBLEM_BANK_NONE = 'No problem is stored.';
export const PROBLEM_BANK_NONE_MATCH = 'No problem matches these filters.';
export const CARD_FILTERS = { module: 'Module', depth: 'Depth' };
export const PROBLEM_FILTERS = {
  technique: 'Technique',
  difficulty: 'Difficulty',
  status: 'Status',
  template: 'Template',
  landed: 'Landed',
  sort: 'Sort',
};
export const REQUIRES = 'Requires';
export const REQUIRED_BY = 'Required by';
export const LADDER = 'Ladder';
export const NO_RUNG = 'No problem fills a rung yet.';
export const CORE = 'core';
export const REQUIRED = 'required';
export const CASES = 'Cases';
export const DIFFICULTY = 'Difficulty';
export const STANDING = 'standing';
export const NO_RATING = 'no rating';
export const NO_SOLUTION = 'No solution is stored.';
export const NO_CASE = 'No case is stored.';
export const WRITTEN_FOR = 'problems written for it';

// ---- the cards

export interface CardFilter {
  module: string | null;
  depth: number | null;
}

export function cardFilter(get: (name: string) => string | null): CardFilter {
  const depth = get('depth');
  return { module: get('module'), depth: depth !== null && /^\d+$/.test(depth) ? Number(depth) : null };
}

export function cardQuery(f: CardFilter): string {
  const q = new URLSearchParams();
  if (f.module) q.set('module', f.module);
  if (f.depth !== null) q.set('depth', String(f.depth));
  return q.toString();
}

export interface CardBankView {
  modules: BankChip[];
  depths: BankChip[];
  filtered: boolean;
  rows: AuthorCard[];
}

const cardHas = (one: AuthorCard, f: CardFilter) =>
  (f.module === null || one.card.module === f.module) && (f.depth === null || one.depth === f.depth);

function chips<R, V extends string | number>(
  rows: R[],
  values: V[],
  on: V | null,
  keeps: (row: R, value: V) => boolean,
  label: (value: V) => string = String,
): BankChip[] {
  return values.map((value) => ({
    value,
    label: label(value),
    count: rows.filter((row) => keeps(row, value)).length,
    on: on === value,
  }));
}

const distinct = <V>(values: V[]) => [...new Set(values)];

/** Each chip counts what pressing it would leave: the other filter applied, and this value. */
export function cardBankView(cards: AuthorCard[], f: CardFilter): CardBankView {
  return {
    modules: chips(cards, distinct(cards.map((one) => one.card.module)).sort(), f.module, (one, module) =>
      cardHas(one, { ...f, module }),
    ),
    depths: chips(
      cards,
      distinct(cards.map((one) => one.depth)).sort((a, b) => a - b),
      f.depth,
      (one, depth) => cardHas(one, { ...f, depth }),
    ),
    filtered: f.module !== null || f.depth !== null,
    rows: cards.filter((one) => cardHas(one, f)),
  };
}

/** A press on the chip already on clears its filter. */
export function cardPressed(f: CardFilter, field: keyof CardFilter, value: string | number): CardFilter {
  return { ...f, [field]: f[field] === value ? null : value };
}

export const cardHeadLine = (one: AuthorCard) => `${one.card.technique} · ${one.card.module} · depth ${one.depth}`;

/** The templates by core and optional, the rungs against the selector's size, and the gaps. */
export function cardShapeLine(one: AuthorCard): string {
  const optional = one.card.templates.filter((t) => t.optional).length;
  const core = one.card.templates.length - optional;
  const forms = optional ? `${core} core + ${optional} optional` : `${core} core`;
  const rungs = `${one.rungs.length} of ${one.card.selector.size} rungs`;
  const gaps = one.gaps.length ? `${counted(one.gaps.length, 'gap')}: ${one.gaps.join(', ')}` : 'no gap';
  return [forms, rungs, gaps].join(' · ');
}

const countOf = (n: number, one: string, many: string) => (n ? `${n} ${n === 1 ? one : many}` : `no ${one}`);

export function templateCountsLine(counts: TemplateCounts | undefined): string {
  if (!counts) return '';
  return [
    countOf(counts.cases, 'case', 'cases'),
    countOf(counts.judgement_items, 'judgement item', 'judgement items'),
    countOf(counts.keyline_items, 'key-line item', 'key-line items'),
  ].join(' · ');
}

/** A standing score where a rating stands, else the band's label. */
export const difficultyLabel = (score: number | null | undefined, label: string | null | undefined) =>
  score != null ? `${Math.round(score)} ${label ?? ''}`.trim() : (label ?? 'unlabelled');

export const edgeLine = (card: string, template: string, usedBy: string) =>
  `${card}, its ${template} used by ${usedBy}`;

export const cardRowLink = (slug: string) => `/author/cards#${encodeURIComponent(slug)}`;

// ---- the problems

export type ProblemStatus = 'served' | 'retired' | 'defective' | 'copied' | 'all';
const STATUSES: Exclude<ProblemStatus, 'all'>[] = ['served', 'retired', 'defective', 'copied'];

export type ProblemLanded = '1d' | '7d' | '30d';
const LANDED: ProblemLanded[] = ['1d', '7d', '30d'];
const LANDED_DAYS: Record<ProblemLanded, number> = { '1d': 1, '7d': 7, '30d': 30 };
export type ProblemSort = 'newest' | 'score' | 'cases';
const SORTS: ProblemSort[] = ['newest', 'score', 'cases'];
const DAY_MS = 24 * 60 * 60 * 1000;

export interface ProblemFilter {
  technique: string | null;
  difficulty: string | null;
  status: ProblemStatus;
  template: string | null;
  landed: ProblemLanded | null;
  sort: ProblemSort;
}

/** `served` until another is named; `all` is the status filter pressed off. */
export function problemFilter(get: (name: string) => string | null): ProblemFilter {
  const status = get('status');
  return {
    technique: get('technique'),
    difficulty: get('difficulty'),
    status: [...STATUSES, 'all'].includes(status ?? '') ? (status as ProblemStatus) : 'served',
    template: get('template'),
    landed: LANDED.find((one) => one === get('landed')) ?? null,
    sort: SORTS.find((one) => one === get('sort')) ?? 'newest',
  };
}

export function problemQuery(f: ProblemFilter): string {
  const q = new URLSearchParams();
  if (f.technique) q.set('technique', f.technique);
  if (f.difficulty) q.set('difficulty', f.difficulty);
  if (f.status !== 'served') q.set('status', f.status);
  if (f.template) q.set('template', f.template);
  if (f.landed) q.set('landed', f.landed);
  if (f.sort !== 'newest') q.set('sort', f.sort);
  return q.toString();
}

const statusHas = (one: AuthorProblemRow, status: ProblemStatus) =>
  status === 'all' ||
  (status === 'served'
    ? !one.retired_reason
    : status === 'retired'
      ? !!one.retired_reason
      : one.retired_reason === status);

// dated by the first solution's `created_at`, since a problem stores no time
const landedHas = (one: AuthorProblemRow, landed: ProblemLanded | null, now: number) =>
  landed === null ||
  (one.landed_at != null && now - Date.parse(one.landed_at) <= LANDED_DAYS[landed] * DAY_MS);

const problemHas = (one: AuthorProblemRow, f: ProblemFilter, now: number) =>
  (f.technique === null || one.techniques.includes(f.technique)) &&
  (f.difficulty === null || one.difficulty === f.difficulty) &&
  statusHas(one, f.status) &&
  (f.template === null || one.target_template === f.template) &&
  landedHas(one, f.landed, now);

// the API sends the rows newest first; a sort keeps that order among ties
const sorted = (rows: AuthorProblemRow[], sort: ProblemSort) =>
  sort === 'score'
    ? [...rows].sort((a, b) => (b.score ?? -Infinity) - (a.score ?? -Infinity))
    : sort === 'cases'
      ? [...rows].sort((a, b) => b.cases - a.cases)
      : rows;

export interface ProblemBankView {
  techniques: BankChip[];
  difficulties: BankChip[];
  statuses: BankChip[];
  templates: BankChip[];
  landed: BankChip[];
  sorts: BankChip[];
  filtered: boolean;
  rows: AuthorProblemRow[];
}

export function problemBankView(
  rows: AuthorProblemRow[],
  f: ProblemFilter,
  now: number = Date.now(),
): ProblemBankView {
  const has = (one: AuthorProblemRow, g: ProblemFilter) => problemHas(one, g, now);
  const kept = rows.filter((one) => has(one, f));
  return {
    techniques: chips(rows, distinct(rows.flatMap((one) => one.techniques)).sort(), f.technique, (one, technique) =>
      has(one, { ...f, technique }),
    ),
    difficulties: chips(rows, [...DIFFICULTIES], f.difficulty, (one, difficulty) => has(one, { ...f, difficulty })),
    statuses: chips(rows, STATUSES, f.status === 'all' ? null : f.status, (one, status) => has(one, { ...f, status })),
    // a chip per form would bury the rows, so only the template a link named shows
    templates: f.template ? chips(rows, [f.template], f.template, (one, template) => has(one, { ...f, template })) : [],
    landed: chips(rows, LANDED, f.landed, (one, landed) => has(one, { ...f, landed })),
    sorts: chips(kept, SORTS, f.sort, () => true),
    filtered:
      f.technique !== null ||
      f.difficulty !== null ||
      f.status !== 'served' ||
      f.template !== null ||
      f.landed !== null,
    rows: sorted(kept, f.sort),
  };
}

export function problemPressed(f: ProblemFilter, field: keyof ProblemFilter, value: string | number): ProblemFilter {
  if (field === 'status') return { ...f, status: f.status === value ? 'all' : (value as ProblemStatus) };
  if (field === 'sort') return { ...f, sort: f.sort === value ? 'newest' : (value as ProblemSort) };
  return { ...f, [field]: f[field] === value ? null : value };
}

export const PROBLEM_CLEARED: ProblemFilter = {
  technique: null,
  difficulty: null,
  status: 'served',
  template: null,
  landed: null,
  sort: 'newest',
};

export const targetLabel = (one: AuthorProblemRow) => one.target_template ?? one.target_technique ?? '';

const ROLE_LETTER: Record<string, string> = { canonical: 'C', reference: 'R', naive: 'N' };
export const rolesLabel = (roles: string[]) => roles.map((one) => ROLE_LETTER[one] ?? '?').join('');

export function problemFactsLine(one: AuthorProblemRow): string {
  return [
    one.techniques.join(', ') || 'no technique',
    counted(one.cases, 'case'),
    rolesLabel(one.roles) || 'no solution',
    one.retired_reason && `retired: ${one.retired_reason}`,
    one.requests ? counted(one.requests, 'request') : null,
  ]
    .filter(Boolean)
    .join(' · ');
}

// a case may weigh up to the ceiling, so a closed one reads cut to a line
const CUT = 60;
export const cutLine = (text: string, at = CUT) => (text.length > at ? `${text.slice(0, at - 1)}…` : text);
export const argsText = (args: unknown[]) => `(${args.map((one) => JSON.stringify(one)).join(', ')})`;
export const expectedText = (expected: unknown) => JSON.stringify(expected) ?? 'null';

// the size names a case heavy enough that its cut line hides most of it
const KB = 1024;
export const sizeLabel = (bytes: number) =>
  bytes < KB * KB ? `${Math.round(bytes / KB)} KB` : `${(bytes / KB / KB).toFixed(1)} MB`;

export function caseNote(one: { round?: number | null; repeats: number; size?: number }): string {
  return [
    one.size && one.size >= KB ? sizeLabel(one.size) : null,
    one.round ? `round ${one.round}` : null,
    one.round == null ? 'separating' : null,
    one.repeats > 1 ? `repeats ${one.repeats}` : null,
  ]
    .filter(Boolean)
    .join(' · ');
}

export function solutionLine(one: AuthorProblem['solutions'][number]): string {
  return [
    one.displays.length ? `displays ${one.displays.join(', ')}` : null,
    one.claims.length ? `claims ${one.claims.join(', ')}` : null,
    one.outcome ?? 'not verified',
  ]
    .filter(Boolean)
    .join(' · ');
}

export function ratingLabel(one: AuthorProblem['ratings'][number]): string {
  const deviation = one.deviation != null ? ` ± ${Math.round(one.deviation)}` : '';
  return `${Math.round(one.score)}${deviation} ${one.source}${one.standing ? ` · ${STANDING}` : ''}`;
}

export const generatorLabel = (label: string | null | undefined) => `generator ${label ?? 'unlabelled'}`;

export const problemRowLink = (id: string) => `/author/problems?status=all#${id.slice(0, 8)}`;
export const templateProblemsLink = (template: string) =>
  `/author/problems?${new URLSearchParams({ template, status: 'all' }).toString()}`;
