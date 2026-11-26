import { levelName, qkey, subTitle } from './courses';
import type { ExamPlan } from './exam';
import { openStep, placedThrough, type Asked } from './placed';
import type { Result } from './result';
import type { Board } from './schedule';
import { shuffle, type Rng } from './select';
import type { Course, Question } from './types';
import { PLACED_NONE } from './words/queue';

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
