import { describe, expect, it } from 'vitest';

import {
  coldOutcome,
  coldVerdict,
  projectedLine,
  ratingLine,
  revealedFacts,
  secondsLeft,
  timeLeft,
  type components,
} from './index';

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

describe('the rating line', () => {
  it('reads nothing before an ended cold sitting', () => {
    /** A rating from no games is Glicko-1's default and says nothing about the user. */
    expect(ratingLine({ rating: 1500, deviation: 350, games: 0 })).toBeNull();
    expect(ratingLine(null)).toBeNull();
  });

  it('reads the rating, its deviation and the sittings, rounded', () => {
    /** The board's cold panel reads the replayed rating once a game exists. */
    expect(ratingLine({ rating: 1579.6, deviation: 210.4, games: 3 })).toBe('Rating 1580 ± 210, from 3 sittings');
    expect(ratingLine({ rating: 1400, deviation: 290, games: 1 })).toBe('Rating 1400 ± 290, from 1 sitting');
  });
});

describe('the projected line', () => {
  it('reads nothing before a sitting reaches a technique', () => {
    /** With no technique reached, the projection is the start and says nothing about the user. */
    expect(projectedLine({ rating: 1500, deviation: 350, techniques: 0 })).toBeNull();
    expect(projectedLine(null)).toBeNull();
  });

  it('reads the projection, its deviation and the techniques, rounded', () => {
    /** The board reads the projected rating beside the measured one. */
    expect(projectedLine({ rating: 1641.5, deviation: 180.2, techniques: 4 })).toBe(
      'Projected 1642 ± 180, from 4 techniques practised',
    );
    expect(projectedLine({ rating: 1500, deviation: 330, techniques: 1 })).toBe(
      'Projected 1500 ± 330, from 1 technique practised',
    );
  });
});
