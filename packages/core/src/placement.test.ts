import { describe, expect, it } from 'vitest';

import {
  baselinePlan,
  Board,
  ExamRun,
  groupCell,
  loadSnapshot,
  placementNext,
  placementPlan,
  type AttemptRecord,
  type Question,
  type Result,
} from './index';

const mk = (id: string, sub: string, level: number, format: 'choice' | 'card' = 'choice') => ({
  id,
  topic: 't',
  sub,
  level,
  kind: 'k',
  prompt: id,
  format,
  ...(format === 'choice' ? { choices: ['a', 'b', 'c', 'd'], answer: ['A'] } : { key: ['one'] }),
});
const four = (sub: string, level: number) => [1, 2, 3, 4].map((i) => mk(`${sub}${level}-${i}`, sub, level));
const catalog = loadSnapshot({
  format: 6,
  courses: [
    {
      slug: 'c',
      definition: {
        title: 'C',
        pass_ratio: 0.8,
        kinds: ['k'],
        topic: [{ slug: 't', tier: 1, title: 'T', subs: ['s', 'u'] }],
      },
      questions: [
        ...four('s', 0),
        ...four('s', 1),
        ...four('s', 2),
        mk('s3-open', 's', 3, 'card'),
        ...four('u', 0),
        ...four('u', 1),
      ],
    },
  ],
} as never);
const course = catalog.courses[0];
const T = '2026-11-01T09:00:00Z';
const first = () => 0;
const res = (q: Question, correct: boolean, guess = false): Result => ({
  q,
  correct,
  guess,
  order: [0, 1, 2, 3],
  picked: [0],
  reply: '',
});
const placed = (ids: string[], ok = true): AttemptRecord[] =>
  ids.map((id) => ({ t: T, course: 'c', id, ok, measure: 'placement' }));
const group = (sub: string, level: number) => ({ course: 'c', topic: 't', sub, level });

describe('a placement', () => {
  it('asks a subtopic first at its highest level holding a choice or a short question', () => {
    const q = placementNext(Board.build(catalog, []), 'c', 't', [], first);
    expect(q).toMatchObject({ sub: 's', level: 2 });
  });

  it('moves one level down on a wrong answer, and on a guessed one', () => {
    const b = Board.build(catalog, []);
    const q = placementNext(b, 'c', 't', [], first) as Question;
    expect(placementNext(b, 'c', 't', [res(q, false)], first)).toMatchObject({ sub: 's', level: 1 });
    expect(placementNext(b, 'c', 't', [res(q, true, true)], first)).toMatchObject({ sub: 's', level: 1 });
  });

  it('ends a subtopic on three correct answers, and goes on to the next subtopic', () => {
    const b = Board.build(catalog, placed(['s2-1', 's2-2', 's2-3']));
    expect(placementNext(b, 'c', 't', [], first)).toMatchObject({ sub: 'u', level: 1 });
  });

  it('asks nothing once every subtopic ended', () => {
    const misses = placed(['u1-1', 'u0-1'], false);
    const b = Board.build(catalog, [...placed(['s2-1', 's2-2', 's2-3']), ...misses]);
    expect(placementNext(b, 'c', 't', [], first)).toBeNull();
    expect(placementPlan(b, course, 't')).toBeNull();
  });
});

describe('a placed group', () => {
  it('counts as done for gating, at the passed level and every level below', () => {
    const records = [...placed(['s2-1'], false), ...placed(['s1-1', 's1-2', 's1-3'])];
    const b = Board.build(catalog, records);
    expect(b.done(group('s', 0))).toBe(true);
    expect(b.done(group('s', 1))).toBe(true);
    expect(b.done(group('s', 2))).toBe(false);
    expect(b.unlocked(group('s', 2))).toBe(true);
    expect(b.frontier(course).map((g) => `${g.sub}@${g.level}`).sort()).toEqual(['s@2', 'u@0']);
  });

  it('reads placed rather than covered, since a placement passes no question', () => {
    const b = Board.build(catalog, placed(['s2-1', 's2-2', 's2-3']));
    expect(groupCell(b, group('s', 1)).state).toBe('placed');
    expect(b.nPassed(group('s', 2))).toBe(0);
    expect(b.status(b.groupQuestions(group('s', 2))[0], Date.parse(T))).toBe('unseen');
  });

  it('is placed by no partial step', () => {
    const b = Board.build(catalog, placed(['s2-1', 's2-2']));
    expect(b.done(group('s', 2))).toBe(false);
    expect(b.done(group('s', 0))).toBe(false);
  });
});

describe('a placement run', () => {
  it('picks each question after the last answer, and stores its answers and a stint naming the topic', () => {
    const plan = placementPlan(Board.build(catalog, []), course, 't', first);
    if (!plan) throw new Error('no placement');
    const run = new ExamRun(plan, catalog.courses);
    const asked: string[] = [];
    // s: misses level 2, passes level 1; u: misses both levels
    const answers = [false, true, true, true, false, false];
    for (const ok of answers) {
      const q = run.question as Question;
      asked.push(`${q.sub}${q.level}`);
      run.answer(res(q, ok));
      if (run.last) break;
      run.next();
    }
    expect(asked).toEqual(['s2', 's1', 's1', 's1', 'u1', 'u0']);
    expect(run.last).toBe(true);
    const records = run.next();
    expect(records?.attempts.every((a) => a.measure === 'placement')).toBe(true);
    expect(records?.session).toMatchObject({ mode: 'placement', course: 'c', topic: 't', score: 3, n: 6 });
    expect(records?.session).not.toHaveProperty('level');
    expect(run.outcome.byTopic.map((r) => r.value)).toEqual(['Associate', 'Not placed']);
  });
});

describe('the baseline test', () => {
  it('samples none of the questions a placement asked', () => {
    const b = Board.build(catalog, placed(['s0-1', 's0-2', 'u0-1', 'u0-2']));
    const plan = baselinePlan(b, { kind: 'baseline', course, topic: 't', level: 0 });
    expect(plan.questions.map((q) => q.id).sort()).toEqual(['s0-3', 's0-4', 'u0-3', 'u0-4']);
  });
});
