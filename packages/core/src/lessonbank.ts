import { bankFilter, bankQuery, type BankChip, type BankFilter } from './bank';
import { subTitle, topicTitle, type Catalog } from './courses';
import type { Lesson } from './graph';
import { inGraphOrder, lessonMinutes } from './lessons';
import type { Course, Question } from './types';

// the author's lessons page: `web-app/pages/author/lessons/`

/** The questions page's filter, narrowed to the module, the topic and the subtopic. */
export function lessonFilter(get: (name: string) => string | null, catalog: Catalog): BankFilter | null {
  const f = bankFilter(get, catalog);
  return f && { ...f, level: null, kind: null, format: null };
}

/** A subtopic a lesson teaches, and the levels it teaches there. */
export interface Taught {
  sub: string;
  title: string;
  levels: number[];
}

export interface LessonBankRow {
  x: Lesson;
  minutes: number; // 0 where the snapshot holds no text yet
  taught: Taught[];
  questions: Question[]; // of the groups it teaches, in the bank's order
  needs: Lesson[];
  neededBy: Lesson[];
}

export interface LessonBankGroup {
  key: string;
  heading: string;
  rows: LessonBankRow[];
}

export interface LessonBankView {
  course: Course;
  modules: BankChip[];
  topics: BankChip[];
  subs: BankChip[]; // offered once a topic is picked
  filtered: boolean;
  shown: number; // distinct lessons, though one may sit under several subtopics
  groups: LessonBankGroup[];
}

const lessonsOf = (c: Course) => c.graph?.lessons ?? [];
const topicOf = (c: Course, sub: string) => c.topics.find((t) => t.subs.includes(sub))?.slug ?? '';
const teachesIn = (c: Course, x: Lesson, topic: string | null, sub: string | null) =>
  x.teaches.some(([s]) => (!topic || topicOf(c, s) === topic) && (!sub || s === sub));

/**
 * One module's lessons under `f`, listed under each subtopic a group they teach
 * sits in, in the module's subtopic order and then graph order.
 */
export function lessonBankView(catalog: Catalog, f: BankFilter): LessonBankView {
  const course = catalog.courses.find((c) => c.slug === f.module)!;
  const all = inGraphOrder(course, lessonsOf(course));
  const bank = catalog.questions.filter((q) => q.course === f.module);
  const bySlug = new Map(all.map((x) => [x.slug, x]));

  const row = (x: Lesson): LessonBankRow => {
    const taught: Taught[] = [];
    for (const [sub, level] of x.teaches) {
      const t = taught.find((y) => y.sub === sub);
      if (t) t.levels.push(level);
      else taught.push({ sub, title: subTitle(course, sub), levels: [level] });
    }
    for (const t of taught) t.levels.sort((a, b) => a - b);
    return {
      x,
      minutes: lessonMinutes(course, x),
      taught,
      questions: bank.filter((q) => x.teaches.some(([s, l]) => q.sub === s && q.level === l)),
      needs: x.needs.filter((n) => n.startsWith('lesson:')).flatMap((n) => bySlug.get(n.slice(7)) ?? []),
      neededBy: all.filter((y) => y.needs.includes(`lesson:${x.slug}`)),
    };
  };

  const groups: LessonBankGroup[] = [];
  const shown = new Set<string>();
  for (const t of course.topics) {
    if (f.topic && t.slug !== f.topic) continue;
    for (const sub of t.subs) {
      if (f.sub && sub !== f.sub) continue;
      const here = all.filter((x) => x.teaches.some(([s]) => s === sub));
      if (!here.length) continue;
      for (const x of here) shown.add(x.slug);
      groups.push({
        key: `${t.slug}/${sub}`,
        heading: `${topicTitle(course, t.slug)} · ${subTitle(course, sub)}`,
        rows: here.map(row),
      });
    }
  }

  const topic = course.topics.find((t) => t.slug === f.topic);
  return {
    course,
    modules: catalog.courses.map((c) => ({
      value: c.slug,
      label: c.slug,
      count: lessonsOf(c).length,
      on: c.slug === f.module,
    })),
    topics: course.topics.map((t) => ({
      value: t.slug,
      label: t.title,
      count: all.filter((x) => teachesIn(course, x, t.slug, null)).length,
      on: f.topic === t.slug,
    })),
    subs: topic
      ? topic.subs.map((s) => ({
          value: s,
          label: topic.subTitles[s] ?? s,
          count: all.filter((x) => teachesIn(course, x, null, s)).length,
          on: f.sub === s,
        }))
      : [],
    filtered: f.topic !== null || f.sub !== null,
    shown: shown.size,
    groups,
  };
}

/** A lesson's row on this page: the filter kept when the row is in view, else the module alone. */
export function lessonRowLink(view: LessonBankView, f: BankFilter, slug: string): string {
  const inView = view.groups.some((g) => g.rows.some((r) => r.x.slug === slug));
  const query = inView ? bankQuery(f) : bankQuery(lessonFilterOf(f.module));
  return `?${query}#${encodeURIComponent(slug)}`;
}

/** A question's row on the questions page. */
export const questionRowLink = (module: string, id: string) =>
  `/author/questions?${bankQuery(lessonFilterOf(module))}#${encodeURIComponent(id)}`;

const lessonFilterOf = (module: string): BankFilter => ({
  module,
  topic: null,
  sub: null,
  level: null,
  kind: null,
  format: null,
});

/** What a closed row's second line says it teaches, as `Functions 0, 1 · 24 questions`. */
export const taughtLine = (taught: Taught[], questions: number) =>
  `${LESSON_TEACHES} ${taught.map((t) => `${t.title} ${t.levels.join(', ')}`).join('; ')} · ${questions} ${questions === 1 ? 'question' : 'questions'}`;

export const lessonMinutesLabel = (n: number) => (n ? `${n} min` : '');
export const pretestLabel = (n: number) => `pretest ${n}`;

export const LESSON_TEACHES = 'teaches';
export const LESSON_NEEDS = 'needs';
export const LESSON_NEEDED_BY = 'needed by';
export const LESSON_QUESTIONS = 'Questions';
export const LESSON_BANK_NONE_MATCH = 'No lesson matches these filters.';
export const LESSON_BANK_FILTERS = { module: 'Module', topic: 'Topic', sub: 'Subtopic' };
