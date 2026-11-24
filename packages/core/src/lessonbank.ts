import { bankFilter, bankQuery, type BankChip, type BankFilter } from './bank';
import { subTitle, type Catalog } from './courses';
import type { Lesson } from './graph';
import type { GridColumn } from './grid';
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

export interface LessonBankView {
  course: Course;
  modules: BankChip[];
  topics: BankChip[];
  subs: BankChip[]; // offered once a topic is picked
  filtered: boolean;
  rows: LessonBankRow[]; // a lesson once, however many subtopics it teaches in
}

const lessonsOf = (c: Course) => c.graph?.lessons ?? [];
const topicOf = (c: Course, sub: string) => c.topics.find((t) => t.subs.includes(sub))?.slug ?? '';
const teachesIn = (c: Course, x: Lesson, topic: string | null, sub: string | null) =>
  x.teaches.some(([s]) => (!topic || topicOf(c, s) === topic) && (!sub || s === sub));

/**
 * One module's lessons under `f`, each once, by the first subtopic in the
 * module's order that a group it teaches sits in, then in graph order.
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

  const shown = new Map<string, Lesson>();
  for (const t of course.topics) {
    if (f.topic && t.slug !== f.topic) continue;
    for (const sub of t.subs) {
      if (f.sub && sub !== f.sub) continue;
      for (const x of all.filter((y) => y.teaches.some(([s]) => s === sub))) shown.set(x.slug, x);
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
    rows: [...shown.values()].map(row),
  };
}

/** A lesson's row on this page: the filter kept when the row is in view, else the module alone. */
export function lessonRowLink(view: LessonBankView, f: BankFilter, slug: string): string {
  const inView = view.rows.some((r) => r.x.slug === slug);
  const query = inView ? bankQuery(f) : bankQuery(lessonFilterOf(f.module));
  return `?${query}#${encodeURIComponent(slug)}`;
}

/** A lesson's dialog on the lessons page, the module alone kept. */
export const lessonRowOf = (module: string, slug: string) =>
  `/author/lessons?${bankQuery(lessonFilterOf(module))}#${encodeURIComponent(slug)}`;

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

/** The groups a lesson teaches, as `Functions 0, 1; Closures 1`. */
export const taughtLabel = (taught: Taught[]) => taught.map((t) => `${t.title} ${t.levels.join(', ')}`).join('; ');

/** The dialog's line on what a lesson teaches, as `teaches Functions 0, 1 · 6 min`. */
export const taughtLine = (row: LessonBankRow) =>
  [`${LESSON_TEACHES} ${taughtLabel(row.taught)}`, lessonMinutesLabel(row.minutes), pretestLabel(row.x.pretest)]
    .filter(Boolean)
    .join(' · ');

export const LESSON_COLUMNS: GridColumn<LessonBankRow>[] = [
  { id: 'slug', header: 'Slug' },
  { id: 'title', header: 'Title' },
  { id: 'teaches', header: 'Teaches' },
  { id: 'minutes', header: 'Minutes', sortBy: (row) => row.minutes, numeric: true },
  { id: 'pretest', header: 'Pretest' },
  { id: 'questions', header: 'Questions', sortBy: (row) => row.questions.length, numeric: true },
];

export const lessonMinutesLabel = (n: number) => (n ? `${n} min` : '');
export const pretestLabel = (n: number) => `pretest ${n}`;

export const LESSON_TEACHES = 'teaches';
export const LESSON_NEEDS = 'needs';
export const LESSON_NEEDED_BY = 'needed by';
export const LESSON_QUESTIONS = 'Questions';
export const LESSON_BANK_NONE_MATCH = 'No lesson matches these filters.';
export const LESSON_BANK_FILTERS = { module: 'Module', topic: 'Topic', sub: 'Subtopic' };
