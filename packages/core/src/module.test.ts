import { describe, expect, it } from 'vitest';

import {
  Board,
  dueCount,
  focusLabel,
  focusLine,
  groupCell,
  levelCounts,
  levelCountsLine,
  loadSnapshot,
  moduleGrid,
  nodeView,
  startPreview,
  subtopicView,
} from './index';

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
      slug: 'c',
      definition: {
        title: 'C',
        pass_ratio: 1,
        kinds: ['concept'],
        topic: [{ slug: 't', tier: 1, title: 'Types', subs: ['s1', 's2'], sub_titles: { s1: 'Ints' } }],
      },
      questions: [mk('a', 's1', 0), mk('b', 's1', 0), mk('c', 's1', 1), mk('d', 's2', 0)],
    },
  ],
} as never);
const T = '2026-11-10T08:00:00.000Z';
const NOW = Date.parse('2026-11-10T12:00:00.000Z');
const g = (sub: string, level: number) => ({ course: 'c', topic: 't', sub, level });

describe('a group cell', () => {
  const b = Board.build(catalog, [{ t: T, course: 'c', id: 'd', ok: true }]);

  it('reads a group with every question passed as covered', () => {
    expect(groupCell(b, g('s2', 0))).toMatchObject({ state: 'covered', count: '1/1', line: '1/1 · covered' });
  });

  it('reads an open group by its passed share', () => {
    expect(groupCell(b, g('s1', 0))).toMatchObject({ state: 'open', count: '0/2', line: '0/2 · open' });
  });

  it('names what a locked group waits for', () => {
    const cell = groupCell(b, g('s1', 1));
    expect(cell.state).toBe('locked');
    expect(cell.line).toBe(`0/1 · ${cell.needs || 'locked'}`);
  });

  it('names the needed subtopic by its title', () => {
    /** a slug is the authoring name, which the learner never meets elsewhere */
    const gated = loadSnapshot({
      format: 6,
      courses: [
        {
          slug: 'c',
          definition: {
            title: 'C',
            pass_ratio: 1,
            kinds: ['concept'],
            topic: [{ slug: 't', tier: 1, title: 'Types', subs: ['s1', 's2'], sub_titles: { s1: 'Ints' } }],
          },
          questions: [mk('a', 's1', 0), mk('d', 's2', 0)],
          graph: { format: 2, needs: { s2: ['s1'] } },
        },
      ],
    } as never);
    expect(groupCell(Board.build(gated, []), g('s2', 0)).needs).toBe('needs Ints · Foundation 0/1');
  });

  it('marks a group holding no questions', () => {
    expect(groupCell(b, g('s2', 1))).toMatchObject({ state: 'empty', count: '·', line: 'no questions' });
  });
});

describe('the counts per level', () => {
  it('sum the passed questions over every subtopic of the module', () => {
    const b = Board.build(catalog, [{ t: T, course: 'c', id: 'd', ok: true }]);
    expect(levelCounts(b, b.courses[0]).slice(0, 2)).toEqual([
      { level: 0, name: 'Foundation', passed: 1, total: 3 },
      { level: 1, name: 'Associate', passed: 0, total: 1 },
    ]);
  });
});

describe('the counts in one line', () => {
  it('leaves out a level that holds no questions', () => {
    const b = Board.build(catalog, [{ t: T, course: 'c', id: 'd', ok: true }]);
    expect(levelCountsLine(b, b.courses[0])).toBe('Foundation 1/3 · Associate 0/1');
  });
});

describe("a module's grid", () => {
  it('reads a row per subtopic by its title, and a cell per level named for its press', () => {
    const b = Board.build(catalog, []);
    const grid = moduleGrid(b, b.courses[0]);
    expect(grid.levels[0]).toEqual({ level: 0, name: expect.any(String) });
    const [t] = grid.topics;
    expect([t.title, t.count, t.rows.map((r) => r.title)]).toEqual(['Types', 2, ['Ints', 's2']]);
    expect(t.rows[0]).toMatchObject({ start: 'Start Ints', focus: 'Focus on Ints' });
    expect(t.rows[0].cells[0].label).toBe('Start Ints, Foundation: 0/2 · open');
  });
});

describe('a mapped subtopic', () => {
  const mapped = loadSnapshot({
    format: 6,
    courses: [
      {
        slug: 'c',
        definition: {
          title: 'C',
          pass_ratio: 1,
          kinds: ['concept'],
          topic: [{ slug: 't', tier: 1, title: 'Types', subs: ['s1', 's3'], sub_titles: { s3: 'Floats' } }],
        },
        questions: [mk('a', 's1', 0), mk('c', 's1', 1)],
        graph: { format: 2, needs: { s1: ['s3'] } },
      },
    ],
  } as never);
  const b = Board.build(mapped, []);

  it('reads every group of a subtopic holding no question as not yet open', () => {
    /** a written subtopic's level holding none stays empty: the subtopic itself is open */
    expect(groupCell(b, g('s3', 0))).toMatchObject({ state: 'mapped', count: '·', line: 'not yet open' });
    expect(groupCell(b, g('s1', 2)).state).toBe('empty');
  });

  it('offers a row that names the state and presses nothing', () => {
    /** a mapped row's name and Focus would open a drill holding no question */
    const [t] = moduleGrid(b, b.courses[0]).topics;
    expect(t.mapped).toBe(false);
    expect(t.rows.map((r) => [r.title, r.mapped, r.note])).toEqual([
      ['Floats', true, 'Not yet open'],
      ['s1', false, ''],
    ]);
  });

  it('locks nothing that needs it', () => {
    /** a learner is never held back by a subtopic nobody has written */
    expect(groupCell(b, g('s1', 0)).state).toBe('open');
    expect(b.nextNew(b.courses[0])).toMatchObject({ sub: 's1', level: 0 });
  });

  it('adds nothing to the counts per level', () => {
    expect(levelCountsLine(b, b.courses[0])).toBe('Foundation 0/1 · Associate 0/1');
  });

  it('reads as one line on its map node and its page', () => {
    /** four lines of "not yet open" would say one fact four times */
    const v = nodeView(b, b.courses[0], { topic: 't', sub: 's3' }, null);
    expect([v.mapped, v.levels]).toEqual([true, [{ line: 'Not yet open', empty: true }]]);
    expect(subtopicView(b, b.courses[0], 's3')?.levels).toEqual(['Not yet open']);
  });
});

describe('the due count', () => {
  it('counts a question answered wrong once its step has passed, and none unseen', () => {
    const b = Board.build(catalog, [{ t: T, course: 'c', id: 'd', ok: false }]);
    expect(dueCount(b, NOW)).toBe(1);
    expect(dueCount(Board.build(catalog, []), NOW)).toBe(0);
  });
});

describe('the start sheet', () => {
  it('counts what its choices leave, and names the press', () => {
    const b = Board.build(catalog, []);
    expect(startPreview(b, { course: 'c', topic: 't', sub: 's1', level: 0 }, 10, NOW)).toMatchObject({
      reviews: 0,
      newLeft: 10,
      empty: false,
      label: 'Start · 0 reviews · 10 new',
    });
  });

  it('says so where nothing is ready', () => {
    const b = Board.build(catalog, []);
    expect(startPreview(b, { course: 'c', due: true }, 10, NOW).label).toBe('Nothing ready here');
  });
});

describe('the focus label', () => {
  it('names the topic and the subtopic by their titles', () => {
    expect(focusLabel({ course: 'c', topic: 't', sub: 's1' }, catalog)).toBe('C › Types › Ints');
  });
});

describe('the focus record', () => {
  it('clears the focus where none is given', () => {
    expect(focusLine(null)).toEqual({ course: null, topic: null, sub: null, strict: false });
  });

  it('names a certification only on a certification focus', () => {
    expect(focusLine({ course: 'c', topic: 't', sub: null, strict: true, cert: 'c-t-associate' })).toEqual({
      course: 'c',
      topic: 't',
      sub: null,
      strict: true,
      cert: 'c-t-associate',
    });
  });
});
