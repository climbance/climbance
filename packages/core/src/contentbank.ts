import type { components } from './api/schema';
import { NEEDS_ATTENTION } from './author';
import type { BankChip } from './bank';
import type { GridColumn } from './grid';
import { DIFFICULTIES } from './listing';
import { counted } from './screens';

// the author's cards and problems pages: `web-app/pages/author/cards/` and
// `web-app/pages/author/problems/`

export type AuthorCard = components['schemas']['AuthorCard'];
export type AuthorCardRow = components['schemas']['AuthorCardRow'];
export type AuthorRung = components['schemas']['AuthorRung'];
export type AuthorProblemRow = components['schemas']['AuthorProblemRow'];
export type AuthorProblem = components['schemas']['AuthorProblem'];
type TemplateCounts = components['schemas']['TemplateCounts'];
export type AttentionFlag = components['schemas']['AttentionFlag'];

export const CARD_BANK_TITLE = 'Cards';
export const PROBLEM_BANK_TITLE = 'Problems';
export const CARD_BANK_NONE = 'No card is seeded.';
export const CARD_BANK_NONE_MATCH = 'No card matches these filters.';
export const PROBLEM_BANK_NONE = 'No problem is stored.';
export const PROBLEM_BANK_NONE_MATCH = 'No problem matches these filters.';
export const CARD_FILTERS = { module: 'Module', depth: 'Depth' };
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
export const SITES = 'Sites';
export const NO_SITE = 'no site outcome';
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
  rows: AuthorCardRow[];
}

const cardHas = (one: AuthorCardRow, f: CardFilter) =>
  (f.module === null || one.module === f.module) && (f.depth === null || one.depth === f.depth);

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
export function cardBankView(cards: AuthorCardRow[], f: CardFilter): CardBankView {
  return {
    modules: chips(cards, distinct(cards.map((one) => one.module)).sort(), f.module, (one, module) =>
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

export const cardHeadLine = (one: AuthorCardRow) =>
  [`${one.technique} · ${one.module} · depth ${one.depth}`, gapsLabel(one.gaps)].join(' · ');

/** The templates by core and optional, as `2 + 1`. */
export const formsLabel = (one: AuthorCardRow) => (one.optional ? `${one.core} + ${one.optional}` : `${one.core}`);
/** The ladder's rungs against the selector's size, as `5/6`. */
export const rungsLabel = (one: AuthorCardRow) => `${one.rungs}/${one.size}`;
export const gapsLabel = (gaps: string[]) => (gaps.length ? `${counted(gaps.length, 'gap')}: ${gaps.join(', ')}` : 'no gap');

export const CARD_COLUMNS: GridColumn<AuthorCardRow>[] = [
  { id: 'slug', header: 'Slug' },
  { id: 'title', header: 'Title' },
  { id: 'technique', header: 'Technique' },
  { id: 'module', header: 'Module' },
  { id: 'depth', header: 'Depth', sortBy: (one) => one.depth, numeric: true },
  { id: 'templates', header: 'Templates' },
  // the share of the ladder filled, so a short ladder of a small selector reads full
  { id: 'rungs', header: 'Rungs', sortBy: (one) => one.rungs / one.size, numeric: true },
  { id: 'gaps', header: 'Gaps', sortBy: (one) => one.gaps.length, numeric: true },
];

const countOf = (n: number, one: string, many: string) => (n ? `${n} ${n === 1 ? one : many}` : `no ${one}`);

export function templateCountsLine(counts: TemplateCounts | undefined): string {
  if (!counts) return '';
  return [
    countOf(counts.cases, 'case', 'cases'),
    countOf(counts.judgement_items, 'judgement item', 'judgement items'),
    countOf(counts.keyline_items, 'key-line item', 'key-line items'),
  ].join(' · ');
}

/** A standing score, with its deviation where one is named, else the band's label. */
export const difficultyLabel = (
  score: number | null | undefined,
  label: string | null | undefined,
  deviation?: number | null,
) =>
  score != null
    ? `${Math.round(score)}${deviation != null ? ` ± ${Math.round(deviation)}` : ''} ${label ?? ''}`.trim()
    : (label ?? 'unlabelled');

export const edgeLine = (card: string, template: string, usedBy: string) =>
  `${card}, its ${template} used by ${usedBy}`;

export const cardRowLink = (slug: string) => `/author/cards#${encodeURIComponent(slug)}`;

// ---- the problems

type ProblemStatus = 'served' | 'retired';
const STATUSES: ProblemStatus[] = ['served', 'retired'];
type RetirementReason = components['schemas']['RetirementReason'];
const REASONS: RetirementReason[] = ['defective', 'copied'];

export type ProblemLanded = '1d' | '7d' | '30d';
const LANDED: ProblemLanded[] = ['1d', '7d', '30d'];
const LANDED_DAYS: Record<ProblemLanded, number> = { '1d': 1, '7d': 7, '30d': 30 };
// `any` is every flagged row: the inbox links to it
export type ProblemFlag = 'any' | AttentionFlag;
const FLAGS: ProblemFlag[] = ['any', 'untagged', 'titled', 'unrated', 'off-band', 'requested'];
const DAY_MS = 24 * 60 * 60 * 1000;

export interface ProblemFilter {
  status: ProblemStatus;
  reason: RetirementReason | null;
  technique: string | null;
  template: string | null;
  difficulty: string | null;
  landed: ProblemLanded | null;
  flag: ProblemFlag | null;
}

export const PROBLEM_CLEARED: ProblemFilter = {
  status: 'served',
  reason: null,
  technique: null,
  template: null,
  difficulty: null,
  landed: null,
  flag: null,
};

const among = <V extends string>(values: V[], value: string | null) => values.find((one) => one === value) ?? null;

/** A reason divides the retired problems, so it reads only under `retired`. */
export function problemFilter(get: (name: string) => string | null): ProblemFilter {
  const status = among(STATUSES, get('status')) ?? 'served';
  return {
    status,
    reason: status === 'retired' ? among(REASONS, get('reason')) : null,
    technique: get('technique'),
    template: get('template'),
    difficulty: get('difficulty'),
    landed: among(LANDED, get('landed')),
    flag: among(FLAGS, get('flag')),
  };
}

export function problemQuery(f: ProblemFilter): string {
  const q = new URLSearchParams();
  if (f.status !== 'served') q.set('status', f.status);
  if (f.reason) q.set('reason', f.reason);
  if (f.technique) q.set('technique', f.technique);
  if (f.template) q.set('template', f.template);
  if (f.difficulty) q.set('difficulty', f.difficulty);
  if (f.landed) q.set('landed', f.landed);
  if (f.flag) q.set('flag', f.flag);
  return q.toString();
}

// dated by the first solution's `created_at`, since a problem stores no time
const landedHas = (one: AuthorProblemRow, landed: ProblemLanded | null, now: number) =>
  landed === null ||
  (one.landed_at != null && now - Date.parse(one.landed_at) <= LANDED_DAYS[landed] * DAY_MS);

const flagHas = (one: AuthorProblemRow, flag: ProblemFlag | null) =>
  flag === null || (flag === 'any' ? one.flags.length > 0 : one.flags.includes(flag));

const problemHas = (one: AuthorProblemRow, f: ProblemFilter, now: number) =>
  (f.status === 'served' ? !one.retired_reason : !!one.retired_reason) &&
  (f.reason === null || one.retired_reason === f.reason) &&
  (f.technique === null || one.techniques.includes(f.technique)) &&
  (f.template === null || one.target_template === f.template) &&
  (f.difficulty === null || one.difficulty === f.difficulty) &&
  landedHas(one, f.landed, now) &&
  flagHas(one, f.flag);

export type ProblemMenuField = keyof ProblemFilter;

/** `value` null is the option clearing the filter. */
export interface MenuOption {
  value: string | null;
  label: string;
  count: number;
  on: boolean;
}

export interface ProblemMenu {
  field: ProblemMenuField;
  /** The trigger: the field's name, and its value once one is picked. */
  label: string;
  options: MenuOption[];
  search: boolean;
}

export const MENU_ANY = 'any';
export const MENU_SEARCH = 'Search';
const MENU_NAMES: Record<ProblemMenuField, string> = {
  status: 'status',
  reason: 'reason',
  technique: 'technique',
  template: 'target',
  difficulty: 'difficulty',
  landed: 'landed',
  flag: 'flag',
};

export interface ProblemBankView {
  menus: ProblemMenu[];
  filtered: boolean;
  rows: AuthorProblemRow[];
}

/** Each option counts what picking it would leave: the other filters applied, and this value. */
export function problemBankView(
  rows: AuthorProblemRow[],
  f: ProblemFilter,
  now: number = Date.now(),
): ProblemBankView {
  const menu = (field: ProblemMenuField, values: string[], clears = true, search = false): ProblemMenu => {
    const option = (value: string | null): MenuOption => {
      const g = problemPicked(f, field, value);
      return {
        value,
        label: value === null ? MENU_ANY : field === 'flag' && value === 'any' ? NEEDS_ATTENTION : value,
        count: rows.filter((one) => problemHas(one, g, now)).length,
        on: f[field] === value,
      };
    };
    const on = f[field];
    return {
      field,
      label: field === 'status' ? f.status : on === null ? MENU_NAMES[field] : `${MENU_NAMES[field]}: ${on}`,
      options: [...(clears ? [option(null)] : []), ...values.map(option)],
      search,
    };
  };
  // the URL may name a template no problem targets, and its option reads greyed
  const templates = distinct([
    ...rows.flatMap((one) => (one.target_template ? [one.target_template] : [])),
    ...(f.template ? [f.template] : []),
  ]).sort();
  const kept = rows.filter((one) => problemHas(one, f, now));
  return {
    menus: [
      menu('status', STATUSES, false),
      ...(f.status === 'retired' ? [menu('reason', REASONS)] : []),
      menu('technique', distinct(rows.flatMap((one) => one.techniques)).sort(), true, true),
      menu('template', templates, true, true),
      menu('difficulty', [...DIFFICULTIES]),
      menu('landed', LANDED),
      menu('flag', FLAGS),
    ],
    filtered: problemQuery(f) !== '',
    // newest first, as the API sends them, until a header is pressed
    rows: kept,
  };
}

/** Picking `served` clears the reason, which reads only under `retired`. */
export function problemPicked(f: ProblemFilter, field: keyof ProblemFilter, value: string | null): ProblemFilter {
  if (field === 'status') return { ...f, status: value as ProblemStatus, reason: value === 'retired' ? f.reason : null };
  return { ...f, [field]: value };
}

export const targetLabel = (one: AuthorProblemRow) => one.target_template ?? one.target_technique ?? '';

export const techniquesLabel = (one: AuthorProblemRow) => one.techniques.join(', ') || 'no technique';

// a retired row names its reason in place of the flags
export const flagsLabel = (one: AuthorProblemRow) =>
  one.retired_reason ? `retired: ${one.retired_reason}` : one.flags.length ? `⚑ ${one.flags.join(' ')}` : '';


export const problemStatus = (one: AuthorProblemRow) => (one.retired_reason ? 'retired' : 'served');

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

// as `climb` printed it: a temperature nobody set reads `default`
export function configurationLabel(one: AuthorProblem['written_by']): string {
  const at = one.temperature == null ? 'default' : String(one.temperature);
  return `${one.model ?? 'no model'}, ${one.effort ?? 'no effort'} @${at}, ${one.prompt_hash ?? 'no hash'} @ ${one.pin ?? 'no pin'}`;
}

const COUNTERS = ['mutants', 'survived', 'killed', 'won', 'proposed', 'misdeclared'] as const;

// a counter reads only where it is not zero: most sites carry none
export function siteLabel(one: AuthorProblem['sites'][number]): string {
  return [
    one.gate ? `gate ${one.gate}${one.detail ? `: ${one.detail}` : ''}` : null,
    ...COUNTERS.map((name) => (one[name] ? `${name} ${one[name]}` : null)),
    one.rounds.length ? `rounds ${one.rounds.join(', ')}` : null,
    one.separating != null
      ? `separating at ${one.separating}${one.repeats > 1 ? ` × ${one.repeats}` : ''}`
      : null,
    one.unseparated ? `unseparated: ${one.unseparated}` : null,
    one.largest != null ? `up to ${one.largest}` : null,
  ]
    .filter(Boolean)
    .join(' · ');
}

export const generatorLabel = (label: string | null | undefined) => `generator ${label ?? 'unlabelled'}`;

// a rung is a served problem, so its row reads under the default status
export const PROBLEM_COLUMNS: GridColumn<AuthorProblemRow>[] = [
  { id: 'title', header: 'Title' },
  { id: 'target', header: 'Target' },
  { id: 'techniques', header: 'Techniques' },
  { id: 'score', header: 'Score', sortBy: (one) => one.score ?? null, numeric: true },
  { id: 'cases', header: 'Cases', sortBy: (one) => one.cases, numeric: true },
  { id: 'flags', header: 'Flags' },
  {
    id: 'landed',
    header: 'Landed',
    sortBy: (one) => (one.landed_at ? Date.parse(one.landed_at) : null),
    numeric: true,
  },
];

export const problemRowLink = (id: string) => `/author/problems#${id.slice(0, 8)}`;
export const templateProblemsLink = (template: string) =>
  `/author/problems?${new URLSearchParams({ template }).toString()}`;

export interface ProblemCommand {
  label: string;
  command: string;
}

// as `climb problem` takes them; a retired problem has nothing left to retire
export function problemCommands(one: AuthorProblemRow): ProblemCommand[] {
  const id = one.problem_id;
  const retire = one.retired_reason
    ? []
    : (['defective', 'copied'] as const).map((reason) => ({
        label: `retire ${reason}`,
        command: `climb problem --retire ${id} --reason ${reason}`,
      }));
  // the standing score, to be edited; unrated, the command ends where the score is typed
  const score = one.score != null ? `${Math.round(one.score)}` : '';
  return [...retire, { label: 'rate by hand', command: `climb problem ${id} --rate ${score}` }];
}
