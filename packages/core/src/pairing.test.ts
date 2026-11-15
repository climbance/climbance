import { describe, expect, it } from 'vitest';

import { cardSubtopics, lessonCards, loadSnapshot, subtopicLabel, type Lesson } from './index';

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
    expect(lessonCards(courses.find((c) => c.slug === 'algo')!, lesson, cards)).toEqual([{ technique: 'binary-search' }]);
  });
});
