import { cardFields } from './records';
import { gradeChoice, hasAnswer, matchShort, parseEstimate, splitGuess, withinFactor } from './reply';
import type { Result } from './result';
import type { DrillFields, Question } from './types';

/** What the user typed, picked and ticked on one question, before it is answered. */
export interface Reply {
  text: string;
  picked: number[]; // displayed positions
  guessing: boolean;
  tapped?: number | null; // a spot-the-flaw drill's line, 1-based
  calledClean?: boolean;
}

/** A short or a choice question's answer. A reply ending in `?` is a guess too. */
export function answerResult(q: Question, order: number[], reply: Reply): Result {
  if (q.judge) return flawResult(q, order, reply);
  if (q.estimate) {
    const [text, suffix] = splitGuess(reply.text);
    const n = parseEstimate(text);
    const correct = n !== null && withinFactor(n, q.estimate);
    return { q, correct, guess: reply.guessing || suffix, order, picked: [], reply: text, drill: n === null ? {} : { estimate: n } };
  }
  if (q.format === 'short') {
    const [text, suffix] = splitGuess(reply.text);
    return { q, correct: matchShort(text, q), guess: reply.guessing || suffix, order, picked: [], reply: text };
  }
  const { picked } = reply;
  return { q, correct: gradeChoice(q, order, picked), guess: reply.guessing, order, picked, reply: '' };
}

/** A spot-the-flaw answer: the verdict is right on a clean item called clean, or a flawed item tapped anywhere. */
function flawResult(q: Question, order: number[], reply: Reply): Result {
  const span = q.judge?.flaw?.span;
  const tapped = reply.calledClean ? null : (reply.tapped ?? null);
  const correct = span ? tapped !== null : tapped === null;
  const drill: DrillFields = { called_clean: tapped === null };
  if (tapped !== null) drill.tapped = tapped;
  if (span && tapped !== null) drill.located = tapped >= span[0] && tapped <= span[1];
  return { q, correct, guess: reply.guessing, order, picked: [], reply: '', drill };
}

/** An open question's answer, graded from the points recalled, the traps fallen into and anything else wrong. */
export function gradeResult(
  q: Question,
  order: number[],
  recalled: Set<number>,
  fell: Set<number>,
  wrong: boolean,
): Result {
  const card = cardFields(q.key.length, recalled, fell, wrong);
  return { q, correct: card.grade === 'k', guess: false, order, picked: [], reply: '', grade: card.grade, card };
}

export function togglePick(picked: number[], pos: number, multi: boolean): number[] {
  if (!multi) return [pos];
  return picked.includes(pos) ? picked.filter((p) => p !== pos) : [...picked, pos];
}

export function canSubmit(q: Question, reply: Reply): boolean {
  if (q.judge) return !!reply.calledClean || reply.tapped != null;
  if (q.estimate) return parseEstimate(splitGuess(reply.text)[0]) !== null;
  return typed(q) ? hasAnswer(reply.text) : reply.picked.length > 0;
}

/** A question answered by picking among options: a choice, or a pick-the-metric drill's candidates. */
export function offersChoices(q: Question): boolean {
  return q.format === 'choice' || q.format === 'metric';
}

/** A question answered by typing: a short reply, or an estimate's number. */
export function typed(q: Question): boolean {
  return q.format === 'short' || q.format === 'estimate';
}

export function flipped(s: Set<number>, i: number): Set<number> {
  const next = new Set(s);
  if (next.has(i)) next.delete(i);
  else next.add(i);
  return next;
}
