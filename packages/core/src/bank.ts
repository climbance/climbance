import { answerResult, gradeResult } from './answer';
import { LETTERS, levelName, subTitle, topicTitle, type Catalog } from './courses';
import { block } from './reply';
import type { AnswerRow, Result } from './result';
import type { Course, Format, Question } from './types';

// the author's questions page: `web-app/pages/author/questions/`

/** A question's format as the glossary names it: the wire's `card` is an open question. */
export type BankFormat = 'choice' | 'short' | 'open';
export const BANK_FORMATS: BankFormat[] = ['choice', 'short', 'open'];
const bankFormat = (format: Format): BankFormat => (format === 'card' ? 'open' : format);

export interface BankFilter {
  module: string;
  topic: string | null;
  sub: string | null;
  level: number | null;
  kind: string | null;
  format: BankFormat | null;
}

type Field = Exclude<keyof BankFilter, 'module'>;

/**
 * The filters a URL carries, degraded as a filtered queue's are: an unknown
 * subtopic keeps its topic. With no module named, or an unknown one, the
 * snapshot's first. Null where the snapshot holds no module.
 */
export function bankFilter(get: (name: string) => string | null, catalog: Catalog): BankFilter | null {
  const c = catalog.courses.find((x) => x.slug === get('module')) ?? catalog.courses[0];
  if (!c) return null;
  const t = c.topics.find((x) => x.slug === get('topic'));
  const sub = get('sub');
  const level = get('level');
  const kind = get('kind');
  const format = get('format');
  const held = catalog.questions.some((q) => q.course === c.slug && String(q.level) === level);
  return {
    module: c.slug,
    topic: t?.slug ?? null,
    sub: t && sub && t.subs.includes(sub) ? sub : null,
    level: level !== null && held ? Number(level) : null,
    kind: kind && c.kinds.includes(kind) ? kind : null,
    format: BANK_FORMATS.find((x) => x === format) ?? null,
  };
}

/** The filter as its URL's query, the module always named so the link keeps it. */
export function bankQuery(f: BankFilter): string {
  const q = new URLSearchParams({ module: f.module });
  if (f.topic) q.set('topic', f.topic);
  if (f.sub) q.set('sub', f.sub);
  if (f.level !== null) q.set('level', String(f.level));
  if (f.kind) q.set('kind', f.kind);
  if (f.format) q.set('format', f.format);
  return q.toString();
}

/** The filter after a chip's press: a press on the chip already on clears its filter. */
export function bankPressed(f: BankFilter, field: Field | 'module', value: string | number): BankFilter {
  if (field === 'module') return { ...BANK_CLEAR, module: String(value) };
  const on = f[field] === value;
  const next = { ...f, [field]: on ? null : value };
  // a subtopic belongs to one topic, so a new topic drops it
  if (field === 'topic') next.sub = null;
  return next;
}

const BANK_CLEAR: Omit<BankFilter, 'module'> = {
  topic: null,
  sub: null,
  level: null,
  kind: null,
  format: null,
};
export const bankCleared = (f: BankFilter): BankFilter => ({ ...BANK_CLEAR, module: f.module });

export interface BankChip {
  value: string | number;
  label: string;
  count: number;
  on: boolean;
}

/** A closed row: what the author scans a bank by. */
export interface BankRow {
  q: Question;
  format: BankFormat;
  first: string; // the prompt's first line
  lines: number; // the code's length, 0 where the question carries none
}

export interface BankGroup {
  key: string;
  heading: string;
  rows: BankRow[];
}

export interface BankView {
  course: Course;
  modules: BankChip[];
  topics: BankChip[];
  subs: BankChip[]; // offered once a topic is picked
  levels: BankChip[];
  kinds: BankChip[];
  formats: BankChip[];
  filtered: boolean;
  shown: number;
  groups: BankGroup[];
}

const matches = (q: Question, f: BankFilter, skip?: Field) =>
  (skip === 'topic' || !f.topic || q.topic === f.topic) &&
  (skip === 'topic' || skip === 'sub' || !f.sub || q.sub === f.sub) &&
  (skip === 'level' || f.level === null || q.level === f.level) &&
  (skip === 'kind' || !f.kind || q.kind === f.kind) &&
  (skip === 'format' || !f.format || bankFormat(q.format) === f.format);

/**
 * One module's bank under `f`. Each chip counts what pressing it would leave,
 * and the rows read by topic, subtopic, level, then the question's position.
 */
export function bankView(catalog: Catalog, f: BankFilter): BankView {
  const course = catalog.courses.find((c) => c.slug === f.module)!;
  const bank = catalog.questions.filter((q) => q.course === f.module);
  const chips = (field: Field, values: { value: string | number; label: string }[], of: (q: Question) => unknown) => {
    const pool = bank.filter((q) => matches(q, f, field));
    return values.map(({ value, label }) => ({
      value,
      label,
      count: pool.filter((q) => of(q) === value).length,
      on: f[field] === value,
    }));
  };
  const topic = course.topics.find((t) => t.slug === f.topic);
  const heldLevels = [...new Set(bank.map((q) => q.level))].sort((a, b) => a - b);

  const shown = bank.filter((q) => matches(q, f));
  const groups: BankGroup[] = [];
  for (const q of shown) {
    const key = `${q.topic}/${q.sub}`;
    let group = groups.find((g) => g.key === key);
    if (!group) {
      group = { key, heading: `${topicTitle(course, q.topic)} · ${subTitle(course, q.sub)}`, rows: [] };
      groups.push(group);
    }
    group.rows.push(bankRow(q));
  }
  // sorts are stable, so a level keeps its questions' positions
  for (const g of groups) g.rows.sort((a, b) => a.q.level - b.q.level);

  return {
    course,
    modules: catalog.courses.map((c) => ({
      value: c.slug,
      label: c.slug,
      count: catalog.questions.filter((q) => q.course === c.slug).length,
      on: c.slug === f.module,
    })),
    topics: chips(
      'topic',
      course.topics.map((t) => ({ value: t.slug, label: t.title })),
      (q) => q.topic,
    ),
    subs: topic
      ? chips(
          'sub',
          topic.subs.map((s) => ({ value: s, label: topic.subTitles[s] ?? s })),
          (q) => q.sub,
        )
      : [],
    levels: chips(
      'level',
      heldLevels.map((l) => ({ value: l, label: `${l} ${levelName(catalog.rules, l)}` })),
      (q) => q.level,
    ),
    kinds: chips(
      'kind',
      course.kinds.map((k) => ({ value: k, label: k })),
      (q) => q.kind,
    ),
    formats: chips(
      'format',
      BANK_FORMATS.map((x) => ({ value: x, label: x })),
      (q) => bankFormat(q.format),
    ),
    filtered: Object.values({ ...f, module: null }).some((v) => v !== null),
    shown: shown.length,
    groups,
  };
}

function bankRow(q: Question): BankRow {
  const code = q.code.replace(/\n+$/, '');
  return {
    q,
    format: bankFormat(q.format),
    first: block(q.prompt).split('\n')[0],
    lines: code ? code.split('\n').length : 0,
  };
}

export const codeLength = (n: number) => (n ? `${n} ${n === 1 ? 'line' : 'lines'}` : '');

/**
 * The question as answered right, through the queue's own grading: every
 * correct choice picked in the authored order, the first accepted reply, or
 * every point of the key recalled and no trap fallen into.
 */
export function answeredRight(q: Question): Result {
  const order = q.choices.map((_, i) => i);
  if (q.format === 'card')
    return gradeResult(q, order, new Set(q.key.keys()), new Set(), false);
  return answerResult(q, order, { text: q.accept[0] ?? '', picked: [...q.answer], guessing: false });
}

/**
 * What the author reads beside each choice: its reason, and on a wrong one
 * the misconception it embodies, by id. A `short` question's every accepted
 * reply, and an open question's key and traps, each with its detail.
 */
export function bankAnswer(q: Question): AnswerRow[] {
  const row = (key: string, ok: boolean, label: string, note = '', mark?: string): AnswerRow => ({
    key,
    ok,
    mark: mark ?? (ok ? '✓' : '✗'),
    label,
    note: note ? block(note) : '',
    yours: false,
  });
  if (q.format === 'choice')
    return q.choices.map((choice, i) => {
      const ok = q.answer.includes(i);
      const why = q.why[i] ? block(q.why[i]) : '';
      const assumes = !ok && q.misconceptions[i] ? `${q.misconceptionIds[i] || 'assumes'}: ${q.misconceptions[i]}` : '';
      return row(`o${i}`, ok, `${LETTERS[i]}) ${block(choice)}`, [why, assumes].filter(Boolean).join('\n'));
    });
  if (q.format === 'short')
    return [
      ...q.accept.map((reply, i) => row(`a${i}`, true, reply)),
      row('case', true, q.caseSensitive ? CASE_COUNTS : CASE_IGNORED, '', '·'),
    ];
  return [
    ...q.key.map((point, i) => row(`k${i}`, true, `${i + 1}. ${block(point)}`, q.keyDetail[i])),
    ...q.traps.map((trap, i) => row(`t${i}`, false, `${'abc'[i]}) ${block(trap)}`, q.trapsDetail[i])),
  ];
}

export const BANK_ANSWER = 'Answer';
export const CASE_COUNTS = 'Case counts';
export const CASE_IGNORED = 'Case is ignored';
export const QUESTIONS_TITLE = 'Questions';
export const BANK_NONE = 'No module is seeded.';
export const BANK_NONE_MATCH = 'No question matches these filters.';
export const BANK_CLEAR_LABEL = 'Clear';
export const OPEN_ALL = 'Open all';
export const CLOSE_ALL = 'Close all';
export const CONCEPT = 'Concept';
export const TAUGHT_BY = 'Taught by';
export const BANK_FILTERS = { module: 'Module', topic: 'Topic', sub: 'Subtopic', level: 'Level', kind: 'Kind', format: 'Format' };
export const conceptLine = (slug: string, level: number) => `${slug} · level ${level}`;
