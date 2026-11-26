// the knowledge pages' paths, as `web-app/README.md` gives them

export const KNOWLEDGE = '/knowledge'
export const LESSONS = '/knowledge/lessons'
export const CERTIFICATIONS = '/knowledge/certifications'
export const EXAM = '/knowledge/exam'

/** A topic's placement, run on the exam page: `core-package/knowledge/placement.md`. */
export function placementPath(module: string, topic: string): string {
  return `${EXAM}?place=${encodeURIComponent(module)}&topic=${encodeURIComponent(topic)}`
}

/** A lesson's page, at one of its sections where `part` names one. */
export function lessonPath(module: string, slug: string, part = ''): string {
  return `${LESSONS}/${module}/${slug}${part ? `#${part}` : ''}`
}

/** A module's page; `from` names the page its way back returns to, as `?from=` does on a problem. */
export function modulePath(module: string, from?: 'board'): string {
  return `${KNOWLEDGE}/modules/${module}${from ? `?from=${from}` : ''}`
}

/** A subtopic's page, a step down from its module. */
export function subtopicPath(module: string, sub: string): string {
  return `${KNOWLEDGE}/modules/${module}/${encodeURIComponent(sub)}`
}
