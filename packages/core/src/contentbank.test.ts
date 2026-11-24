import { describe, expect, it } from 'vitest';

import {
  cardBankView,
  cardFilter,
  cardShapeLine,
  difficultyLabel,
  flagsLabel,
  problemBankView,
  problemFilter,
  problemPicked,
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
  deviation: null,
  retired_reason: null,
  requests: 0,
  landed_at: null,
  flags: [],
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

  const counts = (view: ReturnType<typeof problemBankView>, field: string) =>
    view.menus.find((one) => one.field === field)?.options.map((one) => [one.value, one.count]);

  it('reads the served problems until retired is picked', () => {
    const view = problemBankView(
      rows,
      problemFilter(() => null),
    );

    expect(view.rows.map((one) => one.problem_id)).toEqual(['p1', 'p3']);
    expect(counts(view, 'status')).toEqual([
      ['served', 2],
      ['retired', 1],
    ]);
    expect(view.menus.map((one) => one.field)).not.toContain('reason');
  });

  it('offers the reason only under retired, and drops it on served', () => {
    const retired = problemPicked(problemFilter(() => null), 'status', 'retired');
    const defective = problemPicked(retired, 'reason', 'defective');

    expect(counts(problemBankView(rows, retired), 'reason')).toEqual([
      [null, 1],
      ['defective', 1],
      ['copied', 0],
    ]);
    expect(problemQuery(defective)).toBe('status=retired&reason=defective');
    expect(problemQuery(problemPicked(defective, 'status', 'served'))).toBe('');
    expect(problemFilter((name) => ({ reason: 'defective' })[name] ?? null).reason).toBeNull();
  });

  it('reads an old status=all as served', () => {
    expect(problemFilter((name) => (name === 'status' ? 'all' : null)).status).toBe('served');
  });

  it('keeps a zero option in the menu, as hard on a corpus with no hard problem', () => {
    const view = problemBankView(rows, problemFilter(() => null));

    expect(counts(view, 'difficulty')).toEqual([
      [null, 2],
      ['easy', 2],
      ['medium', 0],
      ['hard', 0],
    ]);
  });

  it('offers every target template, and the one a link names though no row targets it', () => {
    const view = problemBankView(rows, problemFilter((name) => (name === 'template' ? 'gone' : null)));
    const target = view.menus.find((one) => one.field === 'template');

    expect(target?.label).toBe('target: gone');
    expect(target?.search).toBe(true);
    expect(counts(view, 'template')).toEqual([
      [null, 2],
      ['core', 1],
      ['gone', 0],
    ]);
  });

  it('narrows to the problems written for one template', () => {
    const view = problemBankView(
      rows,
      problemFilter((name) => (name === 'template' ? 'core' : null)),
    );

    expect(view.rows.map((one) => one.problem_id)).toEqual(['p3']);
  });

  it('lists the problems landed within the window, by the first solution', () => {
    const now = Date.parse('2026-11-24T12:00:00Z');
    const dated = [
      row('new', { landed_at: '2026-11-24T02:00:00Z' }),
      row('week', { landed_at: '2026-11-20T12:00:00Z' }),
      row('old', { landed_at: '2026-09-01T12:00:00Z' }),
      row('undated', {}),
    ];
    const view = problemBankView(dated, problemFilter((name) => (name === 'landed' ? '1d' : null)), now);

    expect(view.rows.map((one) => one.problem_id)).toEqual(['new']);
    expect(counts(view, 'landed')).toEqual([
      [null, 4],
      ['1d', 1],
      ['7d', 2],
      ['30d', 2],
    ]);
    expect(view.filtered).toBe(true);
  });

  it('orders by score or cases, highest first, unrated last and ties newest first', () => {
    const scored = [
      row('a', { score: 1200, cases: 3 }),
      row('b', { score: null, cases: 9 }),
      row('c', { score: 1500, cases: 3 }),
    ];
    const by = (sort: string) =>
      problemBankView(scored, problemFilter((name) => (name === 'sort' ? sort : null))).rows.map(
        (one) => one.problem_id,
      );

    expect(by('score')).toEqual(['c', 'a', 'b']);
    expect(by('cases')).toEqual(['b', 'a', 'c']);
    expect(by('nonsense')).toEqual(['a', 'b', 'c']);
  });

  it('narrows to any flag, or to one, counting each option', () => {
    const flagged = [row('a', { flags: ['untagged', 'titled'] }), row('b', { flags: ['titled'] }), row('c', {})];
    const by = (flag: string) => problemBankView(flagged, problemFilter((name) => (name === 'flag' ? flag : null)));
    const menu = by('any').menus.find((one) => one.field === 'flag');

    expect(by('any').rows.map((one) => one.problem_id)).toEqual(['a', 'b']);
    expect(by('untagged').rows.map((one) => one.problem_id)).toEqual(['a']);
    expect(menu?.options.slice(0, 4).map((one) => [one.label, one.count])).toEqual([
      ['any', 3],
      ['Needs attention', 2],
      ['untagged', 1],
      ['titled', 2],
    ]);
    expect(problemQuery(problemFilter((name) => (name === 'flag' ? 'titled' : null)))).toBe('flag=titled');
  });

  it('names the flags on a served row, and the reason alone on a retired one', () => {
    expect(flagsLabel(row('a', { flags: ['untagged', 'titled'] }))).toBe('⚑ untagged titled');
    expect(flagsLabel(row('b', { flags: ['requested'], retired_reason: 'copied' }))).toBe('retired: copied');
  });

  it('reads the score with its deviation and label, and the label alone unrated', () => {
    expect(difficultyLabel(1312.4, 'medium', 265.2)).toBe('1312 ± 265 medium');
    expect(difficultyLabel(1200, 'medium', null)).toBe('1200 medium');
    expect(difficultyLabel(null, 'easy', null)).toBe('easy');
  });

  it('keeps the sort out of the URL until it leaves newest', () => {
    const score = problemPicked(problemFilter(() => null), 'sort', 'score');

    expect(problemQuery(score)).toBe('sort=score');
    expect(problemQuery(problemPicked(score, 'sort', 'newest'))).toBe('');
  });
});
