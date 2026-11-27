import { describe, expect, it } from 'vitest';

import { answerResult, canSubmit } from './answer';
import { answeredRight } from './bank';
import { loadSnapshot } from './courses';
import { makeAttempt } from './records';
import { verdictView, youLine } from './result';
import { ratingOf } from './schedule';
import { AGAIN, GOOD, HARD } from './fsrs';
import { traceCorrectedShown, traceRows } from './trace';
import type { RawQuestion, Snapshot } from './types';

const TRACE: RawQuestion = {
  id: 'trc-other-order',
  topic: 'agents',
  sub: 'agent-failures',
  level: 0,
  kind: 'trace',
  prompt: 'Ana asked for a refund of order 42. Tap the first wrong step.',
  format: 'trace',
  steps: [
    { call: "find(customer='ana')", result: '[41, 42]' },
    { call: 'refund(number=41)', result: 'refunded 41' },
    { say: 'Refunded order 41.' },
  ],
  k: 2,
  corrected: [{ call: 'refund(number=42)', result: 'refunded 42' }, { say: 'Refunded order 42.' }],
  end_state: 'refunded: [41]',
  corrected_end_state: 'refunded: [42]',
  explain: 'Order 41 is not the order Ana named.',
};

const snap: Snapshot = {
  format: 6,
  courses: [
    {
      slug: 'ai-eng',
      definition: {
        title: 'AI Engineering',
        pass_ratio: 0.8,
        kinds: ['trace'],
        topic: [{ slug: 'agents', tier: 1, title: 'Agents', subs: ['agent-failures'] }],
      },
      questions: [],
      drills: [TRACE],
    },
  ],
};

const [q] = loadSnapshot(snap).questions;
const reply = (tapped: number | null, guessing = false) => ({ text: '', picked: [], guessing, tapped });
const rated = (tapped: number, guessing = false) => {
  const r = answerResult(q, [], reply(tapped, guessing));
  return ratingOf(makeAttempt('2026-11-27T10:00:00Z', 'ai-eng', q.id, r.correct, r.guess, undefined, undefined, undefined, r.drill));
};

describe('a read-the-trace drill', () => {
  it('reads its steps and its key from the snapshot', () => {
    expect(q.trace?.k).toBe(2);
    expect(traceRows(q, null, false).map((row) => [row.call ?? row.say, row.result])).toEqual([
      ["find(customer='ana')", '[41, 42]'],
      ['refund(number=41)', 'refunded 41'],
      ['Refunded order 41.', null],
    ]);
  });

  it('is answered by tapping a step', () => {
    expect(canSubmit(q, reply(null))).toBe(false);
    expect(canSubmit(q, reply(1))).toBe(true);
  });

  it('rates the key step Good, a guess on it Hard and any other step Again', () => {
    expect(rated(2)).toBe(GOOD);
    expect(rated(2, true)).toBe(HARD);
    expect(rated(1)).toBe(AGAIN);
    expect(rated(3)).toBe(AGAIN);
  });

  it('keeps the tapped step on the record', () => {
    expect(answerResult(q, [], reply(3)).drill).toEqual({ tapped: 3 });
    expect(youLine(answerResult(q, [], reply(3)))).toBe('You: step 3');
  });

  it('marks the key step and shows the corrected run and both end states once answered', () => {
    const r = answerResult(q, [], reply(1));
    expect(verdictView(r).head).toEqual({ correct: false, text: '✗ The first wrong step is step 2.' });
    expect(verdictView(r).explain).toContain('The corrected run ends with: refunded: [42]');
    expect(traceRows(q, 1, true).map((row) => [row.tapped, row.wrong])).toEqual([
      [true, false],
      [false, true],
      [false, false],
    ]);
    expect(traceRows(q, 1, false).some((row) => row.wrong)).toBe(false);
    expect(traceCorrectedShown(q)?.rows.map((row) => row.n)).toEqual([2, 3]);
  });

  it('is answered right by the bank on its key step', () => {
    expect(answeredRight(q).correct).toBe(true);
  });
});
