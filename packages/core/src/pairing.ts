import type { components } from './api/schema';
import { levelName, levels } from './courses';
import type { Lesson } from './graph';
import { inGraphOrder } from './lessons';
import { groupCell } from './module';
import type { Board } from './schedule';
import type { Course } from './types';

// a card and a subtopic are paired by technique code alone: `content-repo/cards-and-subtopics.md`,
// Cards and subtopics

type ListedCard = components['schemas']['ListedCard'];

export const CARD_SUBTOPICS = 'Subtopics';
export const LESSON_CARDS = 'Cards';
export const TEMPLATE_CITES = 'Rests on';
export const SUBTOPIC_LESSONS = 'Lessons';
export const SUBTOPIC_CARDS = 'Cards';
export const SUBTOPIC_LEVELS = 'Levels';
export const SUBTOPIC_MISSING = 'This subtopic is not in the module.';
export const SUBTOPIC_NO_LESSONS = 'No lesson teaches this subtopic yet.';

export interface PairedSubtopic {
  module: string;
  moduleTitle: string;
  topic: string;
  sub: string;
  title: string;
}

export const subtopicLabel = (one: PairedSubtopic) => `${one.title}, ${one.moduleTitle}`;

/** Every subtopic naming the card's technique, the primary module's first. */
export function cardSubtopics(courses: Course[], card: { technique: string; module: string }): PairedSubtopic[] {
  const found = courses
    .filter((course) => !course.archived)
    .flatMap((course) =>
      course.topics.flatMap((topic) =>
        topic.subs
          .filter((sub) => (topic.subTechniques[sub] ?? []).includes(card.technique))
          .map((sub) => ({
            module: course.slug,
            moduleTitle: course.title,
            topic: topic.slug,
            sub,
            title: topic.subTitles[sub] ?? sub,
          })),
      ),
    );
  // stable, so each module keeps the order the catalog lists it in
  return found.sort((a, b) => Number(b.module === card.module) - Number(a.module === card.module));
}

/** The techniques a module's subtopics name, each subtopic's codes together. */
function named(course: Course, subs: Set<string>): Set<string> {
  return new Set(
    course.topics.flatMap((topic) =>
      topic.subs.filter((sub) => subs.has(sub)).flatMap((sub) => topic.subTechniques[sub] ?? []),
    ),
  );
}

/** The subtopics a template cites, as `<module>/<topic>/<subtopic>`, in its order. One the catalog does not hold is left out. */
export function citedSubtopics(courses: Course[], cites: readonly string[]): PairedSubtopic[] {
  return cites.flatMap((cited) => {
    const [module, topic, sub] = cited.split('/');
    const course = courses.find((one) => one.slug === module && !one.archived);
    const held = course?.topics.find((one) => one.slug === topic && one.subs.includes(sub));
    if (!course || !held) return [];
    return [{ module, moduleTitle: course.title, topic, sub, title: held.subTitles[sub] ?? sub }];
  });
}

/** Every card paired with a subtopic the lesson teaches, in the list's order. */
export function lessonCards<C extends Pick<ListedCard, 'technique'>>(course: Course, lesson: Lesson, cards: C[]): C[] {
  const codes = named(course, new Set(lesson.teaches.map(([sub]) => sub)));
  return cards.filter((card) => codes.has(card.technique));
}

export interface SubtopicView {
  topic: string;
  title: string;
  // one line per level holding questions, as the module's cells count them
  levels: string[];
  lessons: Lesson[];
}

/** A subtopic's page: its levels, then the lessons teaching it in the module's order. Null for a subtopic the module does not hold. */
export function subtopicView(b: Board, course: Course, sub: string): SubtopicView | null {
  const topic = course.topics.find((one) => one.subs.includes(sub));
  if (!topic) return null;
  const lines = levels(b.rules).flatMap((level) => {
    const cell = groupCell(b, { course: course.slug, topic: topic.slug, sub, level });
    return cell.state === 'empty' ? [] : [`${levelName(b.rules, level)} · ${cell.line}`];
  });
  return {
    topic: topic.slug,
    title: topic.subTitles[sub] ?? sub,
    levels: lines,
    lessons: inGraphOrder(
      course,
      b.lessons(course).filter((lesson) => lesson.teaches.some(([one]) => one === sub)),
    ),
  };
}

/** Every card paired with the subtopic, in the list's order. */
export function subtopicCards<C extends Pick<ListedCard, 'technique'>>(course: Course, sub: string, cards: C[]): C[] {
  const codes = named(course, new Set([sub]));
  return cards.filter((card) => codes.has(card.technique));
}
