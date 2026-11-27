import { baselineBefore, baselinePlan, baselineTopics, skipBaseline, type BaselineItem } from './baseline';
import type { CertRecord } from './certs';
import { delayedDue, delayedPlan, type DelayedItem } from './delayed';
import { topicKey, type Catalog } from './courses';
import { examOutcome, examTitle, type ExamOutcome, type ExamPlan } from './exam';
import { isLessonItem, NEW_STEP, type LessonItem, type Queue } from './queue';
import { isoNow, makeAttempt } from './records';
import type { Result } from './result';
import { Board } from './schedule';
import { offersRaise, queueLine, type QueueCounts } from './screens';
import { newRecord } from './sync';
import { BASELINE_NAME, DELAYED_NAME, PLACEMENT_NAME } from './words/queue';
import type { AttemptRecord, Course, Question, RaiseRecord, SessionRecord, Status } from './types';

export type QueueItem =
  | { q: Question; tag: Status; fresh: boolean; early: boolean }
  | { lesson: LessonItem }
  | { baseline: BaselineItem }
  | { delayed: DelayedItem };

/** What a client's copy holds when the run reads it: the catalog and every attempt stored so far. */
export interface QueueSource {
  catalog: Catalog | null;
  attempts: AttemptRecord[];
  sessions?: SessionRecord[]; // the stints, which name each topic's baseline test
}

const attemptKey = (a: AttemptRecord) => `${a.t}|${a.course}|${a.id}`;

/**
 * A running queue, as both clients draw it. A method returns the record the client stores,
 * and the client re-renders from the fields after each call.
 */
export class QueueRun {
  current: QueueItem | null = null;
  done = false;
  results: Result[] = [];
  introduced = 0;
  shown = 0; // counts the picks, so a client keys each question's view on it
  // this queue's answers, so a pick never waits for the copy to catch up
  private mine: AttemptRecord[] = [];
  private stinted = false;

  readonly queue: Queue;
  readonly mode: SessionRecord['mode'];
  readonly course: string | null;
  readonly include: string | null;

  constructor(
    queue: Queue,
    mode: SessionRecord['mode'],
    course: string | null,
    include: string | null,
    src: QueueSource,
  ) {
    this.queue = queue;
    this.mode = mode;
    this.course = course;
    this.include = include;
    this.current = this.pick(src);
    this.done = !this.current;
  }

  private built: { catalog: Catalog; attempts: AttemptRecord[]; mine: number; b: Board } | null = null;

  /** The board over the log and this queue's own answers, built again only once either moved. */
  board(src: QueueSource): Board | null {
    if (!src.catalog) return null;
    const was = this.built;
    if (was && was.catalog === src.catalog && was.attempts === src.attempts && was.mine === this.mine.length)
      return was.b;
    const known = new Set(src.attempts.map(attemptKey));
    const extra = this.mine.filter((a) => !known.has(attemptKey(a)));
    const b = Board.build(src.catalog, [...src.attempts, ...extra], this.course, this.include);
    this.built = { catalog: src.catalog, attempts: src.attempts, mine: this.mine.length, b };
    return b;
  }

  private pick(src: QueueSource, now = Date.now()): QueueItem | null {
    const delayed = this.delayedFirst(src, now);
    if (delayed) return { delayed };
    const b = this.board(src);
    const picked = b ? this.queue.pick(b, now) : null;
    this.shown++;
    if (!picked || !b) return null;
    if (isLessonItem(picked)) return { lesson: picked };
    const test = this.baselineBefore(b, picked, src);
    if (test && this.testsOffered.size > 1) {
      // one test per run: the topic's new questions wait for the next run
      this.queue.withheld.add(topicKey(test.course.slug, test.topic));
      this.shown--;
      return this.pick(src, now);
    }
    if (test) {
      // sampled at the offer, so the stop counts the questions the test asks
      this.testPlan = baselinePlan(b, test);
      return { baseline: test };
    }
    return {
      q: picked,
      tag: b.status(picked, now),
      fresh: !b.attempts(picked).length,
      early: this.queue.early(b, picked, now),
    };
  }

  /** Records the answer to the current question, and returns the attempt to store. */
  answer(r: Result): AttemptRecord {
    const rec = makeAttempt(isoNow(), r.q.course, r.q.id, r.correct, r.guess, r.grade, r.card, undefined, r.estimate);
    this.mine.push(rec);
    this.results = [...this.results, r];
    if (this.current && 'q' in this.current && this.current.fresh) this.introduced++;
    return rec;
  }

  /** Moves to the next pick. The queue is done where nothing is left to serve. */
  next(src: QueueSource): void {
    this.current = this.pick(src);
    if (!this.current) this.done = true;
  }

  stop(): void {
    this.done = true;
  }

  // a topic's first new question waits for its baseline test: `core-package/knowledge/baseline-tests.md`.
  // Once per topic in a run, whatever the answer
  private testsOffered = new Set<string>();

  private baselineBefore(b: Board, q: Question, src: QueueSource): BaselineItem | null {
    if (this.queue.kind !== 'mix' && this.queue.kind !== 'focus') return null;
    if (b.attempts(q).length || this.testsOffered.has(topicKey(q.course, q.topic))) return null;
    const item = baselineBefore(b, q, baselineTopics(src.sessions ?? []));
    if (item) this.testsOffered.add(topicKey(q.course, q.topic));
    return item;
  }

  private testPlan: ExamPlan | null = null;

  // a stop at the start of the run, offered again each run until taken:
  // `core-package/knowledge/baseline-tests.md`
  private delayedFirst(src: QueueSource, now: number): DelayedItem | null {
    if (this.shown > 0 || !src.catalog) return null;
    if (this.queue.kind !== 'mix' && this.queue.kind !== 'focus') return null;
    const item = delayedDue(src.catalog, src.sessions ?? [], now);
    if (!item) return null;
    const plan = delayedPlan(src.catalog, item, src.attempts);
    if (!plan.questions.length) return null;
    this.testPlan = plan;
    this.shown++;
    return item;
  }

  /** The current stop's delayed test. */
  get delayedPlan(): ExamPlan | null {
    return this.current && 'delayed' in this.current ? this.testPlan : null;
  }

  /** The current stop's baseline test. */
  get baselinePlan(): ExamPlan | null {
    return this.current && 'baseline' in this.current ? this.testPlan : null;
  }

  /** Skips the current stop's baseline test. Returns the stint to store, before `next`. */
  skipBaseline(): SessionRecord | null {
    if (!this.current || !('baseline' in this.current)) return null;
    return skipBaseline(this.current.baseline, isoNow());
  }

  /** The stint to store once the queue is done or left: once, and none where nothing was answered. */
  end(): SessionRecord | null {
    if (this.stinted || !this.results.length) return null;
    this.stinted = true;
    return newRecord.session(this.mode, this.score, this.results.length);
  }

  /** Raises today's limit, and reopens a queue that ended with nothing left. Returns the raise to store. */
  raise(src: QueueSource): RaiseRecord {
    this.queue.raise(NEW_STEP);
    if (!this.current) {
      const p = this.pick(src);
      if (p) {
        this.current = p;
        this.done = false;
        this.stinted = false;
      }
    }
    return newRecord.raise();
  }

  get score(): number {
    return this.results.filter((r) => r.correct).length;
  }

  /** The counts line, whether a raise is offered, and the summary's inputs. */
  reading(src: QueueSource, now: number) {
    const b = this.board(src);
    const counts: QueueCounts = b
      ? {
          reviews: this.queue.reviews(b, now).length,
          learning: this.queue.stepping(b, now).count,
          newLeft: this.queue.newLeft(b, now),
        }
      : { reviews: 0, learning: 0, newLeft: 0 };
    const unseenLeft = !!b && this.queue.scope.some((q) => !b.attempts(q).length);
    return {
      counts,
      left: queueLine(counts),
      raise: offersRaise(this.mode, counts.newLeft, unseenLeft),
      summary: {
        answered: this.results.length,
        correct: this.score,
        introduced: this.introduced,
        stopped: !!this.current,
      },
    };
  }
}

export type ExamPhase = 'ask' | 'done' | 'review';

/** What an exam stores at its end, together. */
export interface ExamRecords {
  attempts: AttemptRecord[];
  session: SessionRecord;
  cert: CertRecord | null;
}

/** An exam's records as the lines a client stores, in order: the answers, the stint, then the certification's. */
export type ExamLine =
  | { kind: 'attempt'; record: AttemptRecord }
  | { kind: 'session'; record: SessionRecord }
  | { kind: 'cert'; record: CertRecord };

export function examLines(r: ExamRecords | null): ExamLine[] {
  if (!r) return [];
  return [
    ...r.attempts.map((record) => ({ kind: 'attempt' as const, record })),
    { kind: 'session' as const, record: r.session },
    ...(r.cert ? [{ kind: 'cert' as const, record: r.cert }] : []),
  ];
}

/** A running exam: the questions asked one by one, the results, and the missed ones read back. */
export class ExamRun {
  phase: ExamPhase = 'ask';
  index = 0;
  reviewAt = 0;
  results: Result[] = [];
  private stored = false;

  readonly plan: ExamPlan;
  private readonly courses: Course[];
  // a placement's questions grow one at a time, each picked after the answer before it
  private readonly asked: Question[];
  private ended = false;

  constructor(plan: ExamPlan, courses: Course[]) {
    this.plan = plan;
    this.courses = courses;
    this.asked = [...plan.questions];
  }

  get total(): number {
    return this.asked.length;
  }

  get question(): Question | undefined {
    return this.phase === 'ask' ? this.asked[this.index] : undefined;
  }

  /** The last question: known before the answer for a fixed sample, after it for a placement. */
  get last(): boolean {
    if (this.plan.follow) return this.ended;
    return this.index + 1 === this.total;
  }

  answer(r: Result): void {
    this.results = [...this.results, r];
    if (!this.plan.follow) return;
    const q = this.plan.follow(this.results);
    if (q) this.asked.push(q);
    else this.ended = true;
  }

  /** The next question, or the end after the last. */
  next(): ExamRecords | null {
    if (this.index + 1 < this.total) {
      this.index++;
      return null;
    }
    return this.stop();
  }

  /** Ends the exam and returns its records to store, once; none where nothing was answered. */
  stop(): ExamRecords | null {
    this.phase = 'done';
    return this.end();
  }

  /** The records, as `stop` gives them, for a client leaving the exam without a press. */
  end(): ExamRecords | null {
    if (this.stored || !this.results.length) return null;
    this.stored = true;
    const out = examOutcome(this.plan, this.results, isoNow(), this.courses);
    return {
      attempts: out.attempts,
      session: testStint(newRecord.session(this.plan.mode, out.score, out.n), this.plan),
      cert: out.cert ? newRecord.cert(out.cert) : null,
    };
  }

  /** The score, the topics and the missed results, as the summary and the review read them. */
  get outcome(): ExamOutcome {
    return examOutcome(this.plan, this.results, '', this.courses);
  }

  get reviewed(): Result | undefined {
    return this.phase === 'review' ? this.outcome.missed[this.reviewAt] : undefined;
  }

  get reviewLast(): boolean {
    return this.reviewAt + 1 === this.outcome.missed.length;
  }

  review(): void {
    this.reviewAt = 0;
    this.phase = this.outcome.missed.length ? 'review' : 'done';
  }

  /** The next missed question, or the summary after the last. */
  nextMissed(): void {
    if (this.reviewAt + 1 < this.outcome.missed.length) this.reviewAt++;
    else this.phase = 'done';
  }

  /** Leaves the review for the summary. */
  closeReview(): void {
    this.phase = 'done';
  }

  get title(): string {
    const measure = this.plan.test?.measure;
    const name =
      measure === 'baseline'
        ? BASELINE_NAME
        : measure === 'delayed'
          ? DELAYED_NAME
          : measure === 'placement'
            ? PLACEMENT_NAME
            : undefined;
    // a placement's length is not known ahead, so its title counts the question alone
    if (this.plan.follow && this.phase === 'ask') return `${name ?? ''} · ${this.index + 1}`;
    return examTitle(this.phase, this.index, this.total, this.reviewAt, this.outcome.missed.length, name);
  }
}

/** A test's stint names its topic and level: `core-package/knowledge/baseline-tests.md`. */
function testStint(s: SessionRecord, plan: ExamPlan): SessionRecord {
  if (!plan.test) return s;
  const { course, topic, level } = plan.test;
  return level === undefined ? { ...s, course, topic } : { ...s, course, topic, level };
}
