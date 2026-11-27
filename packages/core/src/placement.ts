import { levelName, moduleTopicTitle, qkey, subTitle } from './courses';
import type { ExamPlan } from './exam';
import { openStep, placedThrough, type Asked } from './placed';
import type { Result } from './result';
import type { Board } from './schedule';
import { shuffle, type Rng } from './select';
import type { Course, Question, SessionRecord } from './types';
import { PLACED_NONE, PLACEMENT_KICKER, placementNote } from './words/queue';

/** The log's placement answers, and this run's over them. */
function withRun(b: Board, results: readonly Result[]): Map<string, Asked> {
  const asked = new Map(b.placementAnswers);
  for (const r of results) asked.set(qkey(r.q), { key: qkey(r.q), ok: r.correct, guess: r.guess });
  return asked;
}

/** The next question a topic's placement asks, after the log's answers and this run's. */
export function placementNext(
  b: Board,
  course: string,
  topic: string,
  results: readonly Result[],
  rng: Rng = Math.random,
): Question | null {
  const asked = withRun(b, results);
  const c = b.course(course);
  for (const sub of c?.topics.find((t) => t.slug === topic)?.subs ?? []) {
    const left = openStep(b, course, topic, sub, asked);
    if (left?.length) return shuffle(left, rng)[0];
  }
  return null;
}

/** Whether a topic's placement has a question left to ask. */
export function placementOpen(b: Board, course: string, topic: string): boolean {
  return placementNext(b, course, topic, []) !== null;
}

/** A topic's placement as an exam both clients run: each question picked after the last answer. */
export function placementPlan(b: Board, c: Course, topic: string, rng: Rng = Math.random): ExamPlan | null {
  const first = placementNext(b, c.slug, topic, [], rng);
  if (!first) return null;
  return {
    mode: 'placement',
    questions: [first],
    test: { measure: 'placement', course: c.slug, topic },
    follow: (results) => placementNext(b, c.slug, topic, results, rng),
    rows: (results) => placementRows(b, c, topic, results),
  };
}

/** The summary's rows: per subtopic of the topic, the level placed through. */
export function placementRows(b: Board, c: Course, topic: string, results: readonly Result[]) {
  const asked = withRun(b, results);
  const subs = c.topics.find((t) => t.slug === topic)?.subs ?? [];
  return subs
    .filter((sub) => results.some((r) => r.q.sub === sub))
    .map((sub) => {
      const level = placedThrough(b, c.slug, topic, sub, asked);
      return {
        topic: `${c.slug}/${topic}/${sub}`,
        title: subTitle(c, sub),
        value: level === null ? PLACED_NONE : levelName(b.rules, level),
      };
    });
}

/** The placement a queue offers before a module's first lesson, on the topic of its first new question. */
export interface PlacementItem {
  kind: 'placement';
  course: Course;
  topic: string;
}

/** A module nobody answered in, by practice or a test, and no stint names: `core-package/knowledge/placement.md`. */
export function freshModule(b: Board, course: string, sessions: readonly SessionRecord[]): boolean {
  if (sessions.some((s) => s.course === course)) return false;
  return !b
    .questions()
    .some(
      (q) =>
        q.course === course && (b.attempts(q).length || b.baselineAsked.has(qkey(q)) || b.placementAnswers.has(qkey(q))),
    );
}

/** The placement before `q`, where `q` opens a fresh module and its topic has a question to ask. */
export function placementBefore(b: Board, q: Question, sessions: readonly SessionRecord[]): PlacementItem | null {
  const course = b.course(q.course);
  if (!course || !freshModule(b, q.course, sessions) || !placementOpen(b, q.course, q.topic)) return null;
  return { kind: 'placement', course, topic: q.topic };
}

/** A skip: a placement stint that answered nothing, so the module is offered none again. */
export function skipPlacement(item: PlacementItem, t: string): SessionRecord {
  return { t, mode: 'placement', score: 0, n: 0, course: item.course.slug, topic: item.topic };
}

/** The stop a queue shows for the placement: the topic, and what the placement asks. */
export function placementStop(item: PlacementItem): { kicker: string; title: string; note: string } {
  return { kicker: PLACEMENT_KICKER, title: moduleTopicTitle(item.course, item.topic), note: placementNote };
}
