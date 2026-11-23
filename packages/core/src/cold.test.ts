import { describe, expect, it } from 'vitest';

import { coldOutcome, coldVerdict, revealedFacts, secondsLeft, timeLeft, type components } from './index';

type Sitting = components['schemas']['Sitting'];
type ColdSubmitted = components['schemas']['ColdSubmitted'];

const sitting = (over: Partial<Sitting> = {}): Sitting =>
  ({ id: 's1', cold: true, time_limit_sec: 3600, ended_at: null, pauses: [], ...over }) as Sitting;
const submitted = (solved: boolean, failure: ColdSubmitted['failure'] = null, solveSec: number | null = null) =>
  ({ attempt: { solved, time_to_solve_sec: solveSec }, sitting: sitting(), failure }) as ColdSubmitted;

describe('the countdown', () => {
  it('counts down from the limit, on from the reading', () => {
    /** The time left is the limit less the engine's elapsed time and what passed since the reading arrived. */
    expect(secondsLeft(sitting(), 600, 1_000, 61_000)).toBe(2940);
    expect(timeLeft(2940)).toBe('49:00 left');
  });

  it('stops at zero, and on an ended sitting', () => {
    /** The count never goes negative, and an ended sitting no longer counts on. */
    expect(secondsLeft(sitting(), 3590, 0, 60_000)).toBe(0);
    expect(secondsLeft(sitting({ ended_at: '2026-11-23T10:00:00Z' }), 600, 0, 60_000)).toBe(3000);
  });
});

describe('the verdict', () => {
  it('names the failed case by its number alone', () => {
    /** A contest names the failing test and hides it: `api/rating.md`. */
    expect(coldVerdict(submitted(false, { number: 8, outcome: 'wrong' }))).toBe('Not solved: case 8, wrong answer');
    expect(coldVerdict(submitted(true))).toBe('Solved: every case passed');
  });

  it('reads the outcome with the time from serving', () => {
    /** Solved reads its time; no passing submission reads not solved. */
    expect(coldOutcome(submitted(true, null, 2472))).toBe('Solved in 41:12');
    expect(coldOutcome(submitted(false))).toBe('Not solved');
    expect(coldOutcome(null)).toBe('Not solved');
  });
});

describe('the reveal', () => {
  it('reads the difficulty with its score', () => {
    /** The ended sitting shows the score the rating read the game against. */
    expect(
      revealedFacts({ title: 't', techniques: ['binary-search'], difficulty: 'medium', score: 1609.6 }).difficulty,
    ).toBe('medium 1610');
    expect(revealedFacts({ title: 't', techniques: [], difficulty: 'hard', score: null }).difficulty).toBe('hard');
  });
});
