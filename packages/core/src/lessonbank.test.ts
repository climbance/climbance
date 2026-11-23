import { describe, expect, it } from 'vitest';

import { lessonBankView, lessonFilter, lessonRowLink, loadSnapshot, questionRowLink, taughtLine } from './index';

const q = (id: string, sub: string, level: number) => ({
  id,
  topic: sub === 'v' ? 'u' : 't',
  sub,
  level,
  kind: 'output',
  prompt: id,
  format: 'choice' as const,
  choices: ['a', 'b'],
  answer: ['A'],
});
const catalog = loadSnapshot({
  format: 6,
  courses: [
    {
      slug: 'py',
      definition: {
        title: 'Py',
        pass_ratio: 1,
        kinds: ['output'],
        topic: [
          { slug: 't', tier: 1, title: 'T', subs: ['s', 'r'] },
          { slug: 'u', tier: 2, title: 'U', subs: ['v'] },
        ],
      },
      questions: [q('s0', 's', 0), q('s1', 's', 1), q('r0', 'r', 0), q('v0', 'v', 0)],
      graph: {
        lesson: {
          later: { title: 'Later', file: 'later.md', teaches: ['s@1', 'v@0'], needs: ['lesson:first'] },
          first: { title: 'First', file: 'first.md', teaches: ['s@0'], pretest: 1 },
        },
      },
      lesson_bodies: { first: 'one two three' },
    },
  ],
} as never);
const params = (query: string) => {
  const p = new URLSearchParams(query);
  return (name: string) => p.get(name);
};

describe('lessonBankView', () => {
  it('lists a lesson under each subtopic it teaches, in graph order', () => {
    const view = lessonBankView(catalog, lessonFilter(params('module=py&level=1'), catalog)!);
    expect(view.filtered).toBe(false);
    expect(view.shown).toBe(2);
    expect(view.groups.map((g) => [g.key, g.rows.map((r) => r.x.slug)])).toEqual([
      ['t/s', ['first', 'later']],
      ['u/v', ['later']],
    ]);
    const later = view.groups[0].rows[1];
    expect(later.questions.map((x) => x.id)).toEqual(['s1', 'v0']);
    expect(later.needs.map((x) => x.slug)).toEqual(['first']);
    expect(view.groups[0].rows[0].neededBy.map((x) => x.slug)).toEqual(['later']);
    expect(taughtLine(later.taught, 2)).toBe('teaches s 1; v 0 · 2 questions');
  });

  it('counts on each topic chip the lessons pressing it would leave', () => {
    const view = lessonBankView(catalog, lessonFilter(params('module=py&topic=u'), catalog)!);
    expect(view.topics.map((c) => c.count)).toEqual([2, 1]);
    expect(view.subs.map((c) => [c.value, c.count])).toEqual([['v', 1]]);
    expect(view.groups.map((g) => g.key)).toEqual(['u/v']);
  });

  it('links a lesson out of view by its module alone, and a question to its row', () => {
    const f = lessonFilter(params('module=py&topic=u'), catalog)!;
    const view = lessonBankView(catalog, f);
    expect(lessonRowLink(view, f, 'first')).toBe('?module=py#first');
    expect(lessonRowLink(view, f, 'later')).toBe('?module=py&topic=u#later');
    expect(questionRowLink('py', 's0')).toBe('/author/questions?module=py#s0');
  });
});
