import type { components } from './api/schema';
import { counted } from './screens';

type Stop = components['schemas']['Stop'];
type Retention = components['schemas']['Retention'];
type WaitingPass = components['schemas']['WaitingPass'];

// the author area's pages, by the last segment of each path:
// `web-app/pages/author/README.md`
export const AUTHOR_PAGES: Record<string, string> = {
  inbox: 'Inbox',
  product: 'Product',
  generation: 'Generation',
  spend: 'Spend',
  questions: 'Questions',
  lessons: 'Lessons',
  cards: 'Cards',
  problems: 'Problems',
};

// the navigation's groups, drawn before `/api/author` answers: `web-app/pages/author/README.md`
export const AUTHOR_GROUPS: { title: string | null; pages: string[] }[] = [
  { title: null, pages: ['inbox'] },
  { title: 'Content', pages: ['questions', 'lessons', 'cards', 'problems'] },
  { title: 'Figures', pages: ['product', 'generation', 'spend'] },
];

// the path each page answers at; the inbox is the area's home
export const authorPath = (page: string) => (page === 'inbox' ? '/author' : `/author/${page}`);

export const PRODUCT_TITLE = 'Product';
export const DAYS = 'Days';
export const DAY = 'Day';
export const LEARNERS = 'learners';
export const SITTINGS = 'sittings';
export const ATTEMPTS = 'attempts';
export const ANSWERS = 'answers';

export function usersLine(invited: number, signedIn: number, active: number, days: number): string {
  return `${invited} invited · ${signedIn} signed in · ${active} active in the last ${days} days`;
}

export const retentionLabel = (days: number) => `Retention at ${days} days`;

/** `m of n` and the share, or `none yet` before any user is old enough to count. */
export function retentionCells(one: Retention): [string, string] {
  if (!one.counted) return ['none yet', ''];
  return [`${one.retained} of ${one.counted}`, `${Math.round((100 * one.retained) / one.counted)}%`];
}

// `2026-11-23` reads as `11-23`: the table spans 30 days, never a year
export const dayLabel = (day: string) => day.slice(5);

export const GENERATION_TITLE = 'Generation';
export const STOPPED_BY = 'Stopped by';
export const DRAFTS_NOW = 'Drafts now';
export const CORPUS = 'Corpus';
export const WRITINGS = 'writings';
export const DRAFTS = 'drafts';
export const OLDEST = 'oldest';
export const RETIRED = 'retired';
export const UNLABELLED = 'unlabelled';
export const GAP = 'gap';
export const OPTIONAL = 'optional';
export const NO_STOP = 'Every writing in the period landed.';
export const NO_DRAFT = 'No draft is stored.';
export const NO_CARD = 'No card is seeded.';

export const periodLine = (days: number) => `Last ${days} days`;

/** The writings, the landed ones and the rate; no rate over no writing. */
export function writingsLine(writings: number, landed: number): string {
  const head = `${counted(writings, 'writing')} · ${landed} landed`;
  return writings ? `${head} · ${Math.round((100 * landed) / writings)}%` : head;
}

export function spendLine(perLanded: number | null | undefined): string {
  return perLanded == null ? 'No landed problem to divide the spend by' : `$${perLanded.toFixed(2)} a landed problem`;
}

// a sum over a missing cost reads lower than the truth, so the page says how many
export function uncostedLine(n: number): string | null {
  return n ? `${counted(n, 'site outcome')} ${n === 1 ? 'carries' : 'carry'} no cost` : null;
}

/** Where a writing stopped: the site and its gate, a gate alone, or the held state. */
export function stopLabel(stop: Stop): string {
  if (stop.held_at) return `held at ${stop.held_at}`;
  if (stop.gate) return stop.site ? `${stop.site} · ${stop.gate}` : stop.gate;
  return 'stopped before a draft';
}

/** The total `climb gaps` ended on: the core templates no solution displays. */
export function gapsLine(rows: { optional: boolean; gap: boolean }[]): string {
  const core = rows.filter((row) => !row.optional);
  const gaps = core.filter((row) => row.gap).length;
  return `${gaps} of ${counted(core.length, 'core template')} carry no solution`;
}

// a prefix `climb problem --retire` takes, as the commands print an id
export const shortId = (id: string) => id.slice(0, 8);

export const ageLine = (days: number) => (days === 0 ? 'today' : counted(days, 'day'));

export function untemplatedLine(n: number): string | null {
  return n ? `${counted(n, 'problem')} written for a technique, on no template's row` : null;
}

export const INBOX_TITLE = 'Inbox';

export const PREVIOUS_PROBLEM = 'Previous problem';
export const NEXT_PROBLEM = 'Next problem';
// the opened problem's place among the listed rows, as `5 of 133`
export const positionLabel = (at: number, of: number) => `${at} of ${of}`;

// the count beside the inbox's entry in the navigation: the waiting rows, or none
export const waitingCount = (waiting: number | undefined) => (waiting ? String(waiting) : '');
export const WAITING = 'Waiting';
export const WAITING_REQUESTS = 'Retirement requests, waiting';
export const ANSWERED_REQUESTS = 'Retirement requests, answered';
export const RUN_FAULTS = 'Run faults';
export const SPEND = 'Spend';
export const COST = 'cost';
export const CLEAR = 'clear';
export const OPEN = 'open';
export const NO_ANSWERED = 'No retirement request is answered.';
export const NO_FEEDBACK = 'No feedback is stored.';
export const NO_FAULT = 'No run faulted in the period.';
export const NO_CALL = 'No model call in the period.';
export const NO_CORRECTION = 'no correction stands; run difficulty correct first';

// what each pass would ask about now, said in the pass's own terms
const WAITING_WHAT: Record<WaitingPass['command'], [string, string]> = {
  'claim --by-hand': ['of your attempts carries no claim of yours', 'of your attempts carry no claim of yours'],
  'match --by-hand': ['canonical carries no match of yours', 'canonicals carry no match of yours'],
  'difficulty judge': [
    'served problem carries no rating under the standing correction',
    'served problems carry no rating under the standing correction',
  ],
  'judge build': [
    "template's judgement items are not at its current code",
    "templates' judgement items are not at their current code",
  ],
  'fill build': [
    "template's key-line items are not at its current code",
    "templates' key-line items are not at their current code",
  ],
};

export function waitingLine(one: WaitingPass): string {
  if (one.count == null) return NO_CORRECTION;
  if (one.count === 0) return CLEAR;
  const [single, many] = WAITING_WHAT[one.command];
  return `${one.count} ${one.count === 1 ? single : many}`;
}

export const NEEDS_ATTENTION = 'Needs attention';
// the problems page filtered to every flagged row
export const ATTENTION_LINK = '/author/problems?flag=any';

export function attentionLine(n: number): string {
  if (n === 0) return CLEAR;
  return `${n} served ${n === 1 ? 'problem carries' : 'problems carry'} a flag`;
}

export const recentLine = (n: number, days: number) => `${n} in the last ${days} days`;

export const periodTitle = (title: string, days: number) => `${title}, last ${days} days`;

export const costLabel = (cost: number) => `$${cost.toFixed(2)}`;

export function uncostedCallsLine(n: number): string | null {
  return n ? `${counted(n, 'call')} ${n === 1 ? 'carries' : 'carry'} no cost` : null;
}

// an ISO time read as `11-20` or `11-20 14:02`, in UTC as the days are
export const dateLabel = (at: string) => at.slice(5, 10);
export const timeLabel = (at: string) => `${at.slice(5, 10)} ${at.slice(11, 16)}`;
