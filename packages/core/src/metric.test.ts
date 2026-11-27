import { describe, expect, it } from 'vitest';

import { answerResult, offersChoices } from './answer';
import { agreeing, loadSnapshot } from './courses';
import { metricShown } from './metric';
import { verdictView } from './result';
import type { RawQuestion, Snapshot } from './types';

const DRILL: RawQuestion = {
  id: 'met-fraud',
  topic: 'extraction',
  sub: 'extraction-evals',
  level: 0,
  kind: 'metric',
  prompt: 'A missed fraud costs most. Which metric decides?',
  format: 'metric',
  expected: ['ok', 'fraud'],
  a: ['ok', 'ok'],
  b: ['fraud', 'fraud'],
  candidates: [
    { metric: 'accuracy', label: 'Accuracy' },
    { metric: 'recall', label: 'Recall on fraud' },
  ],
  scores: [
    [0.5, 0.5],
    [0, 1],
  ],
  goal: [-100, -1],
  explain: 'Only the fraud caught tells them apart.',
};

const snap = (raw: RawQuestion): Snapshot => ({
  format: 6,
  courses: [
    {
      slug: 'ai-eng',
      definition: {
        title: 'AI Engineering',
        pass_ratio: 0.8,
        kinds: ['metric'],
        topic: [{ slug: 'extraction', tier: 1, title: 'Extraction', subs: ['extraction-evals'] }],
      },
      questions: [],
      drills: [raw],
    },
  ],
});

const drill = () => loadSnapshot(snap(DRILL)).questions[0];
const pick = (pos: number) => ({ text: '', picked: [pos], guessing: false });

describe('a pick-the-metric drill', () => {
  it('offers its candidates as the choices', () => {
    expect(offersChoices(drill())).toBe(true);
    expect(drill().choices).toEqual(['Accuracy', 'Recall on fraud']);
  });

  it('takes as its key the candidate ranking the systems as the goal does', () => {
    // the key is derived from the computed scores, never authored
    expect(drill().answer).toEqual([1]);
    expect(answerResult(drill(), [0, 1], pick(1)).correct).toBe(true);
    expect(answerResult(drill(), [0, 1], pick(0)).correct).toBe(false);
  });

  it('counts a tie as agreeing with no goal', () => {
    expect(
      agreeing(
        [
          [1, 1],
          [0.2, 0.1],
        ],
        [1, 0],
      ),
    ).toEqual([1]);
  });

  it('shows each candidate with the ranking it gave, in displayed order, and the goal', () => {
    const v = verdictView(answerResult(drill(), [1, 0], pick(1)));
    expect(v.head?.text).toBe('✗ Answer: A.');
    expect(v.explain.split('\n\n')[0].split('\n')).toEqual([
      'A) Recall on fraud: System A 0, System B 1, System B first.',
      'B) Accuracy: System A 0.5, System B 0.5, a tie.',
      'The goal: System A -100, System B -1, System B first.',
    ]);
  });

  it('states its cases as a table, a column for the inputs only where given', () => {
    expect(metricShown(drill())).toEqual({
      header: ['Expected', 'System A', 'System B'],
      rows: [
        ['ok', 'ok', 'fraud'],
        ['fraud', 'ok', 'fraud'],
      ],
    });
    const tries = loadSnapshot(snap({ ...DRILL, inputs: ['t1', 't2'], a: [[true, false], 'x'] })).questions[0];
    expect(metricShown(tries)?.rows[0]).toEqual(['t1', 'ok', '✓ ✗', 'fraud']);
  });
});
