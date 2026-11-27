import { LETTERS } from './courses';
import type { Question } from './types';
import {
  METRIC_EXPECTED,
  METRIC_GOAL,
  METRIC_INPUT,
  METRIC_TIE,
  metricFirst,
  SYSTEM_A,
  SYSTEM_B,
} from './words/metric';

// a pick-the-metric drill: `content-repo/ai-drills.md`

/** One output as a cell reads: a try as ✓ or ✗, a list space-separated. */
export function cell(value: unknown): string {
  if (typeof value === 'boolean') return value ? '✓' : '✗';
  if (Array.isArray(value)) return value.map(cell).join(' ');
  return String(value);
}

/** The cases a pick-the-metric drill states, as a table: the input where given, the expected, and each system's output. */
export function metricShown(q: Question): { header: string[]; rows: string[][] } | null {
  const m = q.metric;
  if (!m) return null;
  const inputs = m.inputs.length > 0;
  const header = [...(inputs ? [METRIC_INPUT] : []), METRIC_EXPECTED, SYSTEM_A, SYSTEM_B];
  const rows = m.expected.map((e, i) => [...(inputs ? [m.inputs[i]] : []), cell(e), cell(m.a[i]), cell(m.b[i])]);
  return { header, rows };
}

const shown = (n: number) => String(Number(n.toPrecision(3)));

function ranking(label: string, [a, b]: [number, number]): string {
  const first = a === b ? METRIC_TIE : metricFirst(a > b ? SYSTEM_A : SYSTEM_B);
  return `${label}: ${SYSTEM_A} ${shown(a)}, ${SYSTEM_B} ${shown(b)}, ${first}.`;
}

/** What each candidate scored and which system it put first, in displayed order, then the goal's own ranking. */
export function metricRankings(q: Question, order: number[]): string[] {
  const m = q.metric;
  if (!m) return [];
  const candidates = order.map((i, pos) => ranking(`${LETTERS[pos]}) ${q.choices[i]}`, m.scores[i]));
  return [...candidates, ranking(METRIC_GOAL, m.goal)];
}
