import type { components } from './api/schema';
import { counted } from './screens';

type Stop = components['schemas']['Stop'];

// the author area's pages, by the last segment of each path:
// `web-app/pages/author/README.md`
export const AUTHOR_PAGES: Record<string, string> = {
  product: 'Product',
  generation: 'Generation',
  workflow: 'Workflow',
};

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

export const ageLine = (days: number) => (days === 0 ? 'today' : counted(days, 'day'));

export function untemplatedLine(n: number): string | null {
  return n ? `${counted(n, 'problem')} written for a technique, on no template's row` : null;
}
