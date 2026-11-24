import { describe, expect, it } from 'vitest';

import { lessonBankView, lessonFilter, lessonRowLink, loadSnapshot, questionRowLink, taughtLabel } from './index';

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
  it('lists a lesson once, though it teaches in two subtopics, in graph order', () => {
    const view = lessonBankView(catalog, lessonFilter(params('module=py&level=1'), catalog)!);
    expect(view.filtered).toBe(false);
    expect(view.rows.map((r) => r.x.slug)).toEqual(['first', 'later']);
    const later = view.rows[1];
    expect(later.questions.map((x) => x.id)).toEqual(['s1', 'v0']);
    expect(later.needs.map((x) => x.slug)).toEqual(['first']);
    expect(view.rows[0].neededBy.map((x) => x.slug)).toEqual(['later']);
    expect(taughtLabel(later.taught)).toBe('s 1; v 0');
  });

  it('counts on each topic chip the lessons pressing it would leave', () => {
    const view = lessonBankView(catalog, lessonFilter(params('module=py&topic=u'), catalog)!);
    expect(view.topics.map((c) => c.count)).toEqual([2, 1]);
    expect(view.subs.map((c) => [c.value, c.count])).toEqual([['v', 1]]);
    expect(view.rows.map((r) => r.x.slug)).toEqual(['later']);
  });

  it('links a lesson out of view by its module alone, and a question to its row', () => {
    const f = lessonFilter(params('module=py&topic=u'), catalog)!;
    const view = lessonBankView(catalog, f);
    expect(lessonRowLink(view, f, 'first')).toBe('?module=py#first');
    expect(lessonRowLink(view, f, 'later')).toBe('?module=py&topic=u#later');
    expect(questionRowLink('py', 's0')).toBe('/author/questions?module=py#s0');
  });
});
