import { moduleTopicTitle, qkey, topicKey } from './courses';
import type { ExamPlan } from './exam';
import type { Board } from './schedule';
import { shuffle, type Rng } from './select';
import type { Course, Question, SessionRecord } from './types';
import { BASELINE_KICKER, baselineNote } from './words/queue';

// `core-package/knowledge/baseline-tests.md`
export const BASELINE_PER_SUB = 2;
export const BASELINE_MOST = 20;

/** The baseline test a queue offers in place of a topic's first new question. */
export interface BaselineItem {
  kind: 'baseline';
  course: Course;
  topic: string;
  level: number;
}

/** The topics a baseline test was taken or skipped on, each stored as a stint. */
export function baselineTopics(sessions: readonly SessionRecord[]): Set<string> {
  const out = new Set<string>();
  for (const s of sessions) if (s.mode === 'baseline' && s.course && s.topic) out.add(topicKey(s.course, s.topic));
  return out;
}

/** No question of the topic was answered in practice: the board skips a test's answers. */
export function untouched(b: Board, course: string, topic: string): boolean {
  return !b.questions().some((q) => q.course === course && q.topic === topic && b.attempts(q).length);
}

/** The test before `q`, where `q` opens a topic the user has neither studied nor tested. */
export function baselineBefore(b: Board, q: Question, tested: ReadonlySet<string>): BaselineItem | null {
  const course = b.course(q.course);
  if (!course || tested.has(topicKey(q.course, q.topic)) || !untouched(b, q.course, q.topic)) return null;
  return { kind: 'baseline', course, topic: q.topic, level: q.level };
}

/** Two `choice` or `short` questions per subtopic at the item's level, at most twenty. */
export function baselinePlan(b: Board, item: BaselineItem, rng: Rng = Math.random): ExamPlan {
  const pool = b
    .questions()
    .filter((q) => q.course === item.course.slug && q.topic === item.topic && q.level === item.level)
    .filter((q) => q.format !== 'card' && !b.placementAnswers.has(qkey(q)));
  const subs = item.course.topics.find((t) => t.slug === item.topic)?.subs ?? [];
  const picked = subs.flatMap((s) =>
    shuffle(
      pool.filter((q) => q.sub === s),
      rng,
    ).slice(0, BASELINE_PER_SUB),
  );
  return {
    mode: 'baseline',
    questions: shuffle(picked, rng).slice(0, BASELINE_MOST),
    test: { measure: 'baseline', course: item.course.slug, topic: item.topic, level: item.level },
  };
}

/** A skip: a baseline stint that answered nothing, so the test is not offered again. */
export function skipBaseline(item: BaselineItem, t: string): SessionRecord {
  return { t, mode: 'baseline', score: 0, n: 0, course: item.course.slug, topic: item.topic, level: item.level };
}

/** The stop a queue shows for the test: the topic, and what the test asks and stores. */
export function baselineStop(item: BaselineItem, size: number): { kicker: string; title: string; note: string } {
  return { kicker: BASELINE_KICKER, title: moduleTopicTitle(item.course, item.topic), note: baselineNote(size) };
}
