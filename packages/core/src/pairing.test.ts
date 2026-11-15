import { describe, expect, it } from 'vitest';

import {
  Board,
  cardSubtopics,
  citedSubtopics,
  lessonCards,
  loadSnapshot,
  subtopicCards,
  subtopicLabel,
  subtopicView,
  type Lesson,
} from './index';

const module = (slug: string, title: string, subs: string[], techniques: Record<string, string[]>) => ({
  slug,
  definition: {
    title,
    pass_ratio: 1,
    kinds: ['concept'],
    topic: [{ slug: 't', tier: 1, title: 'T', subs, sub_titles: { [subs[0]]: 'First' }, sub_techniques: techniques }],
  },
  questions: [],
});
const courses = loadSnapshot({
  format: 6,
  courses: [
    module('py', 'Python', ['heapq', 'other'], { heapq: ['heap'] }),
    module('algo', 'Algorithms', ['heaps', 'search'], { heaps: ['heap'], search: ['binary-search'] }),
  ],
} as never).courses;

describe('a card and its subtopics', () => {
  it("lists every subtopic naming the card's technique, the primary module's first", () => {
    /** another module's subtopic adds to the card, after the one supporting it */
    const found = cardSubtopics(courses, { technique: 'heap', module: 'algo' });
    expect(found.map((one) => `${one.module}/${one.sub}`)).toEqual(['algo/heaps', 'py/heapq']);
    expect(subtopicLabel(found[1])).toBe('First, Python');
  });

  it('lists nothing for a technique no subtopic names', () => {
    expect(cardSubtopics(courses, { technique: 'greedy', module: 'algo' })).toEqual([]);
  });
});

describe('a lesson and its cards', () => {
  it('lists the cards paired with a subtopic the lesson teaches', () => {
    const lesson = { slug: 'l', teaches: [['search', 0]] } as unknown as Lesson;
    const cards = [{ technique: 'heap' }, { technique: 'binary-search' }];
    expect(
      lessonCards(
        courses.find((c) => c.slug === 'algo')!,
        lesson,
        cards,
      ),
    ).toEqual([{ technique: 'binary-search' }]);
  });
});

describe("a subtopic's page", () => {
  const mk = (id: string, sub: string, level: number) => ({
    id,
    topic: 't',
    sub,
    level,
    kind: 'concept',
    prompt: id,
    format: 'choice' as const,
    choices: ['a', 'b', 'c'],
    answer: ['A'],
  });
  const catalog = loadSnapshot({
    format: 6,
    courses: [
      {
        slug: 'algo',
        definition: {
          title: 'Algorithms',
          pass_ratio: 1,
          kinds: ['concept'],
          topic: [
            {
              slug: 't',
              tier: 1,
              title: 'T',
              subs: ['search', 'heaps'],
              sub_titles: { search: 'Binary search' },
              sub_techniques: { search: ['binary-search'] },
            },
          ],
        },
        questions: [mk('q1', 'search', 0), mk('q2', 'search', 0), mk('q3', 'heaps', 0)],
        graph: {
          format: 2,
          needs: {},
          lesson: {
            sorted: { title: 'Sorted', file: 'a.md', teaches: ['search@0'], needs: [], pretest: 0 },
            heap: { title: 'Heap', file: 'b.md', teaches: ['heaps@0'], needs: [], pretest: 0 },
          },
        },
      },
    ],
  } as never);
  const [c] = catalog.courses;

  it('reads a line per level holding questions, and the lessons teaching the subtopic', () => {
    const view = subtopicView(
      Board.build(catalog, [{ t: '2026-11-10T08:00:00.000Z', course: 'algo', id: 'q1', ok: true }]),
      c,
      'search',
    );
    expect(view?.title).toBe('Binary search');
    expect(view?.levels).toEqual(['Foundation · 1/2 · open']);
    expect(view?.lessons.map((x) => x.slug)).toEqual(['sorted']);
  });

  it('lists the cards paired with the subtopic', () => {
    expect(subtopicCards(c, 'search', [{ technique: 'heap' }, { technique: 'binary-search' }])).toEqual([
      { technique: 'binary-search' },
    ]);
  });

  it('reads nothing for a subtopic the module does not hold', () => {
    expect(subtopicView(Board.build(catalog, []), c, 'graphs')).toBeNull();
  });
});

describe("a template's citations", () => {
  it('reads each cited subtopic the catalog holds, in the order cited', () => {
    /** a citation the catalog no longer holds has nothing to open */
    const cited = citedSubtopics(courses, ['py/t/heapq', 'py/t/gone', 'algo/t/heaps']);
    expect(cited.map(subtopicLabel)).toEqual(['First, Python', 'First, Algorithms']);
  });
});
