import { moduleTopicTitle, qkey, topicKey, type Catalog } from './courses';
import type { ExamPlan } from './exam';
import { parseTime } from './schedule';
import { shuffle, type Rng } from './select';
import type { AttemptRecord, Course, SessionRecord } from './types';
import { DELAYED_KICKER, delayedNote } from './words/queue';

// `knowledge.md`, Baseline and delayed tests
export const DELAYED_AFTER_DAYS = 28;
const DAY = 86_400_000;

/** The delayed test a queue offers at its start, four weeks after a topic's baseline test. */
export interface DelayedItem {
  kind: 'delayed';
  course: Course;
  topic: string;
  level: number;
  since: string; // when the baseline test was taken
}

/** The oldest baseline test taken four weeks ago or more whose topic has no delayed test yet. */
export function delayedDue(catalog: Catalog, sessions: readonly SessionRecord[], now: number): DelayedItem | null {
  const delayed = new Set(
    sessions.filter((s) => s.mode === 'delayed' && s.course && s.topic).map((s) => topicKey(s.course!, s.topic!)),
  );
  const due = sessions
    // a skip answered nothing, so its topic gets no delayed test
    .filter((s) => s.mode === 'baseline' && s.n > 0 && s.course && s.topic && s.level !== undefined)
    .filter((s) => !delayed.has(topicKey(s.course!, s.topic!)))
    .filter((s) => now >= parseTime(s.t) + DELAYED_AFTER_DAYS * DAY)
    .sort((a, b) => parseTime(a.t) - parseTime(b.t));
  for (const s of due) {
    const course = catalog.courses.find((c) => c.slug === s.course);
    if (course) return { kind: 'delayed', course, topic: s.topic!, level: s.level!, since: s.t };
  }
  return null;
}

/** The baseline test's questions, read from its answers, asked again in a new order. */
export function delayedPlan(
  catalog: Catalog,
  item: DelayedItem,
  attempts: readonly AttemptRecord[],
  rng: Rng = Math.random,
): ExamPlan {
  const asked = new Set(attempts.filter((a) => a.measure === 'baseline').map(qkey));
  const questions = catalog.questions.filter(
    (q) => q.course === item.course.slug && q.topic === item.topic && asked.has(qkey(q)),
  );
  return {
    mode: 'delayed',
    questions: shuffle(questions, rng),
    test: { measure: 'delayed', course: item.course.slug, topic: item.topic, level: item.level },
  };
}

/** The stop a queue shows for the delayed test: the topic, and when the baseline was taken. */
export function delayedStop(item: DelayedItem, size: number): { kicker: string; title: string; note: string } {
  return {
    kicker: DELAYED_KICKER,
    title: moduleTopicTitle(item.course, item.topic),
    note: delayedNote(size, item.since.slice(0, 10)),
  };
}
