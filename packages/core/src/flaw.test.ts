import { describe, expect, it } from 'vitest';

import { answerResult, canSubmit } from './answer';
import { loadSnapshot } from './courses';
import { flawFixShown, flawLines } from './flaw';
import { makeAttempt } from './records';
import { verdictView } from './result';
import { ratingOf } from './schedule';
import { AGAIN, GOOD, HARD } from './fsrs';
import type { RawQuestion, Snapshot } from './types';

const CLEAN: RawQuestion = {
  id: 'jdg-chunks',
  topic: 'retrieval',
  sub: 'chunking',
  level: 0,
  kind: 'judge',
  prompt: 'Is this chunker correct?',
  format: 'judge',
  lines: ['def chunks(words, size, overlap):', '    step = size - overlap', '    return step'],
  input: 'chunks("a b c".split(), 2, 1)',
  output: '1',
  explain: 'The step leaves the overlap shared.',
};
const FLAWED: RawQuestion = {
  ...CLEAN,
  id: 'jdg-chunks-no-overlap',
  lines: ['def chunks(words, size, overlap):', '    step = size', '    return step'],
  output: '2',
  span: [2, 2],
  fix: ['    step = size - overlap'],
  clean_output: '1',
};

const snap = (raws: RawQuestion[]): Snapshot => ({
  format: 6,
  courses: [
    {
      slug: 'ai-eng',
      definition: {
        title: 'AI Engineering',
        pass_ratio: 0.8,
        kinds: ['judge'],
        topic: [{ slug: 'retrieval', tier: 1, title: 'Retrieval', subs: ['chunking'] }],
      },
      questions: [],
      drills: raws,
    },
  ],
});

const [clean, flawed] = loadSnapshot(snap([CLEAN, FLAWED])).questions;
const reply = (tapped: number | null, calledClean = false) => ({ text: '', picked: [], guessing: false, tapped, calledClean });
const rated = (q: typeof clean, tapped: number | null, calledClean = false) => {
  const r = answerResult(q, [], reply(tapped, calledClean));
  return ratingOf(makeAttempt('2026-11-27T10:00:00Z', 'ai-eng', q.id, r.correct, r.guess, undefined, undefined, undefined, r.drill));
};

describe('a spot-the-flaw drill', () => {
  it('reads its flaw from the snapshot, and none on the clean item', () => {
    expect(clean.judge?.flaw).toBeNull();
    expect(flawed.judge?.flaw?.span).toEqual([2, 2]);
  });

  it('is answered by calling it correct or by tapping a line', () => {
    expect(canSubmit(clean, reply(null))).toBe(false);
    expect(canSubmit(clean, reply(null, true))).toBe(true);
    expect(canSubmit(clean, reply(3))).toBe(true);
  });

  it('rates the right line Good, the wrong line Hard and the wrong verdict Again', () => {
    expect(rated(flawed, 2)).toBe(GOOD);
    expect(rated(flawed, 3)).toBe(HARD);
    expect(rated(flawed, null, true)).toBe(AGAIN);
    expect(rated(clean, null, true)).toBe(GOOD);
    expect(rated(clean, 2)).toBe(AGAIN);
  });

  it('keeps the raw answer on the record', () => {
    const r = answerResult(flawed, [], reply(3));
    expect(r.drill).toEqual({ called_clean: false, tapped: 3, located: false });
  });

  it('shows the flaw and the witness once answered', () => {
    const r = answerResult(flawed, [], reply(3));
    expect(verdictView(r).head?.text).toBe('Right that a line is wrong, but the flaw is on line 2.');
    expect(verdictView(r).explain).toContain('The correct lines give: `1`');
    expect(flawLines(flawed, 3, true).map((l) => [l.tapped, l.flawed])).toEqual([
      [false, false],
      [false, true],
      [true, false],
    ]);
    expect(flawLines(flawed, 3, false).some((l) => l.flawed)).toBe(false);
    expect(flawFixShown(flawed)).toEqual({ label: 'Line 2 should read', code: '    step = size - overlap' });
  });

  it('calls a tapped clean item a false alarm', () => {
    expect(verdictView(answerResult(clean, [], reply(2))).head).toEqual({
      correct: false,
      text: '✗ The lines were correct: no line is wrong.',
    });
  });
});
