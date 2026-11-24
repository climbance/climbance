import { describe, expect, it } from 'vitest';

import { answeredRight, bankAnswer, bankFilter, bankPressed, bankView, loadSnapshot } from './index';

const mk = (id: string, more: object = {}) => ({
  id,
  topic: 't',
  sub: 's',
  level: 0,
  kind: 'output',
  prompt: `${id}\nsecond line`,
  format: 'choice' as const,
  choices: ['a', 'b'],
  answer: ['A'],
  ...more,
});
const catalog = loadSnapshot({
  format: 6,
  courses: [
    {
      slug: 'algo',
      definition: {
        title: 'Algo',
        pass_ratio: 1,
        kinds: ['output', 'principle'],
        topic: [
          { slug: 't', tier: 1, title: 'T', subs: ['s', 'r'] },
          { slug: 'u', tier: 2, title: 'U', subs: ['v'] },
        ],
      },
      questions: [
        mk('late', { level: 2, code: 'x = 1\nprint(x)\n' }),
        mk('early'),
        mk('said', { kind: 'principle', sub: 'r' }),
        mk('other', { topic: 'u', sub: 'v', format: 'short', accept: ['3', 'three'] }),
      ],
    },
    {
      slug: 'py',
      definition: { title: 'Py', pass_ratio: 1, kinds: ['output'], topic: [{ slug: 'p', tier: 1, title: 'P', subs: ['q'] }] },
      questions: [mk('py-one', { topic: 'p', sub: 'q' })],
    },
  ],
} as never);
const params = (query: string) => {
  const q = new URLSearchParams(query);
  return (name: string) => q.get(name);
};

describe('bankFilter', () => {
  it('opens the first module, and degrades an unknown subtopic to its topic', () => {
    expect(bankFilter(params(''), catalog)?.module).toBe('algo');
    const f = bankFilter(params('module=algo&topic=t&sub=v&kind=nope&level=9&format=open'), catalog);
    expect(f).toEqual({ module: 'algo', topic: 't', sub: null, level: null, kind: null, format: 'open' });
  });
});

describe('bankView', () => {
  it('lists every output question, each chip counting what pressing it would leave', () => {
    const f = bankFilter(params('module=algo&kind=output'), catalog)!;
    const view = bankView(catalog, f);
    expect(view.rows.map((row) => row.q.id)).toEqual(['early', 'late', 'other']);
    expect(view.kinds.map((chip) => [chip.value, chip.count, chip.on])).toEqual([
      ['output', 3, true],
      ['principle', 1, false],
    ]);
    expect(view.formats.map((chip) => chip.count)).toEqual([2, 1, 0]);
  });

  it('reads a row: the first line of the prompt and the code in lines', () => {
    const f = bankFilter(params('module=algo&level=2'), catalog)!;
    const [row] = bankView(catalog, f).rows;
    expect([row.first, row.lines]).toEqual(['late', 2]);
  });

  it('offers the subtopics once a topic is picked, and drops the subtopic with a new topic', () => {
    const f = bankFilter(params('module=algo&topic=t&sub=r'), catalog)!;
    expect(bankView(catalog, f).subs.map((chip) => chip.count)).toEqual([2, 1]);
    expect(bankPressed(f, 'topic', 'u')).toMatchObject({ topic: 'u', sub: null });
    expect(bankPressed(f, 'sub', 'r').sub).toBeNull();
  });
});

describe('bankAnswer', () => {
  it("names each choice's reason and a wrong choice's misconception by id", () => {
    const q = loadSnapshot({
      format: 6,
      courses: [
        {
          slug: 'algo',
          definition: { title: 'Algo', pass_ratio: 1, kinds: ['output'], topic: [{ slug: 't', tier: 1, title: 'T', subs: ['s'] }] },
          questions: [
            mk('q', {
              concept: 'lower-bound',
              why: ['Right.', 'Wrong.'],
              misconception: { B: 'any-copy' },
              misconception_text: { B: 'any copy will do' },
            }),
          ],
        },
      ],
    } as never).questions[0];
    expect(q.concept).toBe('lower-bound');
    expect(bankAnswer(q).map((row) => [row.mark, row.label, row.note])).toEqual([
      ['✓', 'A) a', 'Right.'],
      ['✗', 'B) b', 'Wrong.\nany-copy: any copy will do'],
    ]);
  });

  it('answers each format right through the queue grading', () => {
    const [choice, , , short] = catalog.questions;
    expect(answeredRight(choice).correct).toBe(true);
    expect(answeredRight(short).correct).toBe(true);
    expect(bankAnswer(short).map((row) => row.label)).toEqual(['3', 'three', 'Case is ignored']);
  });
});
