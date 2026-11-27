import type { Result } from './result';
import type { Question, TraceStep } from './types';
import { TRACE_CORRECTED_ENDS, TRACE_ENDS, traceCorrected, traceFound, traceMissed } from './words/trace';

// a read-the-trace drill: `content-repo/ai-drills.md`

/** One step as the drill draws it: a message or a call beside its result, and after the answer whether it is the key. */
export interface TraceRow {
  n: number;
  say: string | null;
  call: string | null;
  result: string | null; // the environment's, drawn under its call and never a tap target
  tapped: boolean;
  wrong: boolean; // shown once answered alone
}

const row = (step: TraceStep, n: number, tapped: boolean, wrong: boolean): TraceRow =>
  'call' in step
    ? { n, say: null, call: step.call, result: step.result, tapped, wrong }
    : { n, say: step.say, call: null, result: null, tapped, wrong };

export function traceRows(q: Question, tapped: number | null, answered: boolean): TraceRow[] {
  const t = q.trace;
  if (!t) return [];
  return t.steps.map((step, i) => row(step, i + 1, tapped === i + 1, answered && i + 1 === t.k));
}

/** The corrected run from the key step on, shown under the steps once answered. */
export function traceCorrectedShown(q: Question): { label: string; rows: TraceRow[] } | null {
  const t = q.trace;
  if (!t) return null;
  return { label: traceCorrected(t.k), rows: t.corrected.map((step, i) => row(step, t.k + i, false, false)) };
}

export function traceHead(r: Result): { correct: boolean; text: string } {
  const k = r.q.trace?.k ?? 0;
  return r.correct ? { correct: true, text: traceFound(k) } : { correct: false, text: traceMissed(k) };
}

/** The replay the key rests on: the state each run left the environment in. */
export function traceWitness(q: Question): string[] {
  const t = q.trace;
  if (!t) return [];
  return [`${TRACE_ENDS}: ${t.endState}`, `${TRACE_CORRECTED_ENDS}: ${t.correctedEndState}`];
}
