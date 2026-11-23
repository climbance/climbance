import type { components } from './api/schema';
import { described, type EngineClient } from './engine';
import { NO_DIFFICULTY, techniquesLine } from './words/pages';
import { OUTCOME_LABELS } from './recall';
import { duration } from './sitting';
import type { Moved, Outcome } from './sittingrun';

// a cold sitting, for every platform: `web-app/pages/practice/cold/`, and
// `api/rating.md` for each rule

type ColdSeated = components['schemas']['ColdSeated'];
type ColdSubmitted = components['schemas']['ColdSubmitted'];
type Revealed = components['schemas']['Revealed'];
type Sitting = components['schemas']['Sitting'];
type Measured = components['schemas']['Measured'];

/** The engine's reading of a cold sitting, with when the platform received it. */
export interface ColdRead {
  seated: ColdSeated;
  at: number;
}

/** The seconds left before the limit, counted on from the reading as the drill loop's clock is. */
export function secondsLeft(sitting: Sitting, elapsedSec: number | null, receivedAt: number, now: number): number {
  const limit = sitting.time_limit_sec ?? 0;
  const spent = (elapsedSec ?? 0) + (sitting.ended_at == null ? Math.max(0, now - receivedAt) / 1000 : 0);
  return Math.max(0, limit - spent);
}

export const timeLeft = (seconds: number) => `${duration(Math.ceil(seconds))} left`;

/** The verdict a cold submission reads: the first failed case by its number alone. */
export function coldVerdict(submitted: ColdSubmitted): string {
  if (submitted.attempt.solved) return COLD_SOLVED_VERDICT;
  const failed = submitted.failure;
  return failed ? `Not solved: case ${failed.number}, ${OUTCOME_LABELS[failed.outcome]}` : 'Not solved';
}

/** The ended bar's outcome: solved with the time from serving, or not solved. */
export function coldOutcome(last: ColdSubmitted | null): string {
  const solve = last?.attempt.solved ? last.attempt.time_to_solve_sec : null;
  return solve != null ? `Solved in ${duration(solve)}` : 'Not solved';
}

/** The record line an ended cold sitting reveals: the difficulty with its score, then the techniques. */
export function revealedFacts(revealed: Revealed): { difficulty: string; techniques: string } {
  const label = revealed.difficulty ?? NO_DIFFICULTY;
  return {
    difficulty: revealed.score == null ? label : `${label} ${Math.round(revealed.score)}`,
    techniques: techniquesLine(revealed.techniques),
  };
}

async function attempt<T>(run: () => Promise<Outcome<T>>): Promise<Outcome<T>> {
  try {
    return await run();
  } catch (reason) {
    return { ok: false, refused: String(reason) };
  }
}

/** Serves a cold sitting, or the one running: the engine answers a second serve with it. */
export function serveCold(client: EngineClient, device: string, now: () => number): Promise<Outcome<ColdRead>> {
  return attempt(async () => {
    const { data, error } = await client.POST('/api/cold-sittings', { body: { device } });
    return data ? { ok: true, value: { seated: data, at: now() } } : { ok: false, refused: described(error) };
  });
}

/** Reads a cold sitting back, which touches it and lets the engine end it at its limit. */
export function readCold(client: EngineClient, sittingId: string, now: () => number): Promise<Outcome<ColdRead>> {
  return attempt(async () => {
    const { data, error } = await client.GET('/api/cold-sittings/{sitting_id}', {
      params: { path: { sitting_id: sittingId } },
    });
    return data ? { ok: true, value: { seated: data, at: now() } } : { ok: false, refused: described(error) };
  });
}

export function submitCold(
  client: EngineClient,
  sittingId: string,
  code: string,
  now: () => number,
): Promise<Outcome<{ submitted: ColdSubmitted; at: number }>> {
  return attempt(async () => {
    const { data, error } = await client.POST('/api/cold-sittings/{sitting_id}/submissions', {
      params: { path: { sitting_id: sittingId } },
      body: { code, restored: false },
    });
    return data ? { ok: true, value: { submitted: data, at: now() } } : { ok: false, refused: described(error) };
  });
}

/** Ends a cold sitting through the sitting's own route, as End does in the drill loop. */
export function endCold(client: EngineClient, sittingId: string, now: () => number): Promise<Outcome<Moved>> {
  return attempt(async () => {
    const { data, error } = await client.POST('/api/sittings/{sitting_id}/end', {
      params: { path: { sitting_id: sittingId } },
    });
    return data
      ? { ok: true, value: { sitting: data.sitting, elapsedSec: data.elapsed_sec, at: now() } }
      : { ok: false, refused: described(error) };
  });
}

// no game leaves Glicko-1's default, which says nothing about the user
export function ratingLine(measured: Measured | null): string | null {
  if (!measured || measured.games === 0) return null;
  const sittings = measured.games === 1 ? '1 sitting' : `${measured.games} sittings`;
  return `Rating ${Math.round(measured.rating)} ± ${Math.round(measured.deviation)}, from ${sittings}`;
}

export const COLD_TITLE = 'Cold problem';
export const COLD_PANEL_NOTE = 'An unseen problem with nothing named, 60 minutes, no pause. It measures your rating.';
export const COLD_START = 'Start cold';
export const COLD_SOLVED_VERDICT = 'Solved: every case passed';
export const COLD_SOLVED_LINE = 'Solved. End shows the problem: its title, techniques and difficulty.';
export const COLD_END_TITLE = 'End the cold sitting?';
// an unsolved sitting ended is a game lost, and the rating keeps it
export const coldEndNote = (solved: boolean) =>
  solved
    ? 'The sitting counts as solved, and the page then shows the problem.'
    : 'Nothing has passed yet, so the sitting counts as not solved. The rating keeps that game.';
export const COLD_KEEP = 'Keep solving';
