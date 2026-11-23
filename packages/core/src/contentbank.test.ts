import { describe, expect, it } from 'vitest';

import {
  cardBankView,
  cardFilter,
  cardShapeLine,
  problemBankView,
  problemFilter,
  problemPressed,
  problemQuery,
  type AuthorCard,
  type AuthorProblemRow,
} from './index';

const template = (slug: string, optional = false) => ({
  id: `t-${slug}`,
  slug,
  title: slug,
  trigger: 't',
  code: 'pass',
  optional,
});
const card = (slug: string, module: string, depth: number, gaps: string[] = []): AuthorCard =>
  ({
    card: {
      id: slug,
      slug,
      technique: slug,
      module,
      title: slug,
      trigger: 't',
      brief: 'b',
      templates: [template('a'), template('b', true)],
      selector: { technique: slug, size: 3 },
    },
    depth,
    counts: [],
    required_by: [],
    rungs: [],
    gaps,
  }) as unknown as AuthorCard;

const row = (id: string, fields: Partial<AuthorProblemRow>): AuthorProblemRow => ({
  problem_id: id,
  title: id,
  target_template: null,
  target_technique: 'greedy',
  difficulty: 'easy',
  score: null,
  techniques: ['greedy'],
  cases: 1,
  roles: ['canonical'],
  retired_reason: null,
  requests: 0,
  landed_at: null,
  ...fields,
});

describe('the cards page', () => {
  const cards = [card('x', 'algo', 0), card('y', 'algo', 1, ['a']), card('z', 'py', 0)];

  it('counts on each chip what pressing it would leave', () => {
    const view = cardBankView(
      cards,
      cardFilter((name) => ({ depth: '0' })[name] ?? null),
    );

    expect(view.rows.map((one) => one.card.slug)).toEqual(['x', 'z']);
    expect(view.modules.map((one) => [one.value, one.count])).toEqual([
      ['algo', 1],
      ['py', 1],
    ]);
    expect(view.depths.map((one) => [one.value, one.count, one.on])).toEqual([
      [0, 2, true],
      [1, 1, false],
    ]);
  });

  it('names a gap on the closed row', () => {
    expect(cardShapeLine(cards[1])).toBe('1 core + 1 optional · 0 of 3 rungs · 1 gap: a');
  });
});

describe('the problems page', () => {
  const rows = [
    row('p1', { techniques: ['greedy', 'sorting'] }),
    row('p2', { difficulty: 'hard', retired_reason: 'defective' }),
    row('p3', { target_template: 'core', target_technique: null }),
  ];

  it('reads the served problems until another status is picked', () => {
    const view = problemBankView(
      rows,
      problemFilter(() => null),
    );

    expect(view.rows.map((one) => one.problem_id)).toEqual(['p1', 'p3']);
    expect(view.statuses.map((one) => [one.value, one.count])).toEqual([
      ['served', 2],
      ['retired', 1],
      ['defective', 1],
      ['copied', 0],
    ]);
  });

  it('keeps the status pressed off in the URL', () => {
    const all = problemPressed(
      problemFilter(() => null),
      'status',
      'served',
    );

    expect(problemQuery(all)).toBe('status=all');
    expect(problemBankView(rows, all).rows).toHaveLength(3);
  });

  it('narrows to the problems written for one template', () => {
    const view = problemBankView(
      rows,
      problemFilter((name) => (name === 'template' ? 'core' : null)),
    );

    expect(view.rows.map((one) => one.problem_id)).toEqual(['p3']);
  });
});
