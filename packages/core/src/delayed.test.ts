import { describe, expect, it } from 'vitest';

import {
  Board,
  delayedDue,
  delayedStop,
  loadSnapshot,
  nextQueue,
  QueueRun,
  type AttemptRecord,
  type SessionRecord,
} from './index';

const mk = (id: string) => ({
  id,
  topic: 't',
  sub: 's',
  level: 0,
  kind: 'k',
  prompt: id,
  format: 'choice' as const,
  choices: ['a', 'b', 'c'],
  answer: ['A'],
});
const catalog = loadSnapshot({
  format: 6,
  courses: [
    {
      slug: 'c',
      definition: { title: 'C', pass_ratio: 1, kinds: ['k'], topic: [{ slug: 't', tier: 1, title: 'T', subs: ['s'] }] },
      questions: [mk('a'), mk('b'), mk('x')],
    },
  ],
} as never);
const T = '2026-10-01T09:00:00Z';
const DAY = 86_400_000;
const baseline: SessionRecord = { t: T, mode: 'baseline', score: 1, n: 2, course: 'c', topic: 't', level: 0 };
const answers: AttemptRecord[] = [
  { t: T, course: 'c', id: 'a', ok: true, measure: 'baseline' },
  { t: T, course: 'c', id: 'b', ok: false, measure: 'baseline' },
];
const at = (days: number) => Date.parse(T) + days * DAY;

describe('the delayed test', () => {
  it('falls due four weeks after a taken baseline test, and not before', () => {
    expect(delayedDue(catalog, [baseline], at(27))).toBeNull();
    expect(delayedDue(catalog, [baseline], at(28))).toMatchObject({ topic: 't', since: T });
  });

  it('is not offered on a skipped baseline test, nor once taken', () => {
    const skip = { ...baseline, score: 0, n: 0 };
    expect(delayedDue(catalog, [skip], at(40))).toBeNull();
    const taken = { ...baseline, t: '2026-11-01T09:00:00Z', mode: 'delayed' };
    expect(delayedDue(catalog, [baseline, taken], at(40))).toBeNull();
  });

  it("opens a queue run with the baseline's questions, and a later run offers it again", () => {
    const src = { catalog, attempts: answers, sessions: [baseline] };
    const run = () => new QueueRun(nextQueue(Board.build(catalog, answers), 10), 'next', null, null, src);
    const r = run();
    expect(r.current && 'delayed' in r.current).toBe(true);
    expect(r.delayedPlan?.questions.map((q) => q.id).sort()).toEqual(['a', 'b']);
    expect(r.delayedPlan?.test).toMatchObject({ measure: 'delayed', course: 'c', topic: 't', level: 0 });
    r.next(src);
    expect(r.current && 'delayed' in r.current).toBe(false);
    expect(run().current && 'delayed' in run().current!).toBe(true);
  });

  it('names the module, the topic and the day of the baseline test', () => {
    const item = delayedDue(catalog, [baseline], at(30))!;
    expect(delayedStop(item, 2)).toMatchObject({ title: 'C · T' });
    expect(delayedStop(item, 2).note).toMatch(/^The 2 questions of your baseline test on 2026-10-01/);
  });
});
