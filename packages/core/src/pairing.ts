import type { components } from './api/schema';
import type { Lesson } from './graph';
import type { Course } from './types';

// a card and a subtopic are paired by technique code alone: `content.md`,
// Cards and subtopics

type ListedCard = components['schemas']['ListedCard'];

export const CARD_SUBTOPICS = 'Subtopics';
export const LESSON_CARDS = 'Cards';

export interface PairedSubtopic {
  module: string;
  moduleTitle: string;
  topic: string;
  sub: string;
  title: string;
}

export const subtopicLabel = (one: PairedSubtopic) => `${one.title}, ${one.moduleTitle}`;

/** Every subtopic naming the card's technique, the primary module's first. */
export function cardSubtopics(
  courses: Course[],
  card: { technique: string; module: string },
): PairedSubtopic[] {
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

/** Every card paired with a subtopic the lesson teaches, in the list's order. */
export function lessonCards<C extends Pick<ListedCard, 'technique'>>(
  course: Course,
  lesson: Lesson,
  cards: C[],
): C[] {
  const taught = new Set(lesson.teaches.map(([sub]) => sub));
  const codes = new Set(
    course.topics.flatMap((topic) =>
      topic.subs.filter((sub) => taught.has(sub)).flatMap((sub) => topic.subTechniques[sub] ?? []),
    ),
  );
  return cards.filter((card) => codes.has(card.technique));
}
