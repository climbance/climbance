import { groupKey, levels, qkey } from './courses';
import type { AttemptRecord, Course, Group, Question, Rules } from './types';

// `core-package/knowledge/placement.md`
export const PLACEMENT_STEP = 3;

/** What the placement rules read of a board; `schedule.ts` imports this file. */
export interface PlacementView {
  readonly rules: Rules;
  readonly courses: Course[];
  readonly baselineAsked: ReadonlySet<string>;
  readonly placementAnswers: ReadonlyMap<string, Asked>;
  groupQuestions(g: Group): Question[];
}

/** One placement answer, from the log or from the run asking it. */
export interface Asked {
  key: string; // qkey
  ok: boolean;
  guess: boolean;
}

type Step = 'passed' | 'missed' | 'open';

/** A placement step: missed on the first wrong or guessed answer, passed once it asked enough. */
function stepOf(pool: readonly Question[], asked: ReadonlyMap<string, Asked>): Step {
  const mine = pool.filter((q) => asked.has(qkey(q))).map((q) => asked.get(qkey(q)) as Asked);
  if (mine.some((a) => !a.ok || a.guess)) return 'missed';
  return mine.length >= Math.min(PLACEMENT_STEP, pool.length) ? 'passed' : 'open';
}

/** A group's placement pool: its `choice` and `short` questions no baseline test asked. */
function poolOf(b: PlacementView, course: string, topic: string, sub: string, level: number): Question[] {
  return b
    .groupQuestions({ course, topic, sub, level })
    .filter((q) => q.format !== 'card' && !b.baselineAsked.has(qkey(q)));
}

/** The subtopic's written levels, highest first: those whose pool holds a question. */
function written(b: PlacementView, course: string, topic: string, sub: string): number[] {
  return levels(b.rules)
    .filter((level) => poolOf(b, course, topic, sub, level).length)
    .reverse();
}

/** The level a subtopic is placed through, or null where no placement step passed. */
export function placedThrough(b: PlacementView, course: string, topic: string, sub: string, asked: ReadonlyMap<string, Asked>) {
  for (const level of written(b, course, topic, sub)) {
    const step = stepOf(poolOf(b, course, topic, sub, level), asked);
    if (step === 'passed') return level;
    if (step === 'open') return null;
  }
  return null;
}

/** The group to ask next on a subtopic, or null once a pass or the last miss ended it. */
export function openStep(b: PlacementView, course: string, topic: string, sub: string, asked: ReadonlyMap<string, Asked>) {
  for (const level of written(b, course, topic, sub)) {
    const pool = poolOf(b, course, topic, sub, level);
    const step = stepOf(pool, asked);
    if (step === 'passed') return null;
    if (step === 'open') return pool.filter((q) => !asked.has(qkey(q)));
  }
  return null;
}

/** The placement answers in a log, by question. */
export function placementAnswers(records: readonly AttemptRecord[]): Map<string, Asked> {
  const out = new Map<string, Asked>();
  for (const r of records)
    if (r.measure === 'placement') out.set(qkey(r), { key: qkey(r), ok: r.ok, guess: !!r.guess });
  return out;
}

/** The `groupKey` of every placed group: each passed step's, and each lower group of its subtopic. */
export function placedGroups(b: PlacementView): Set<string> {
  const out = new Set<string>();
  if (!b.placementAnswers.size) return out;
  for (const c of b.courses)
    for (const t of c.topics)
      for (const sub of t.subs) {
        const top = placedThrough(b, c.slug, t.slug, sub, b.placementAnswers);
        if (top === null) continue;
        for (let level = 0; level <= top; level++) out.add(groupKey({ course: c.slug, topic: t.slug, sub, level }));
      }
  return out;
}
