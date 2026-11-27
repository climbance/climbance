import type { Result } from './result';
import type { Question } from './types';
import {
  FLAW_CLEAN_GIVES,
  FLAW_GIVES,
  FLAW_INPUT,
  FLAW_MEASURED,
  FLAW_MODEL_CLEAN_GIVES,
  FLAW_MODEL_GIVES,
  flawFalseAlarm,
  flawFix,
  flawFound,
  flawMissed,
  flawRight,
  flawSpotted,
} from './words/flaw';

// a spot-the-flaw drill: `content-repo/ai-drills.md`

/** One line as the drill draws it: its number, its text, and after the answer whether it was tapped and whether it is the flaw. */
export interface FlawLine {
  n: number;
  text: string;
  tapped: boolean;
  flawed: boolean; // shown once answered alone
}

export function flawLines(q: Question, tapped: number | null, answered: boolean): FlawLine[] {
  const j = q.judge;
  if (!j) return [];
  const span = answered ? j.flaw?.span : undefined;
  return j.lines.map((text, i) => ({
    n: i + 1,
    text,
    tapped: tapped === i + 1,
    flawed: !!span && i + 1 >= span[0] && i + 1 <= span[1],
  }));
}

/** What the flawed span reads clean, shown under the lines once answered. Null on a clean item. */
export function flawFixShown(q: Question): { label: string; code: string } | null {
  const flaw = q.judge?.flaw;
  return flaw ? { label: flawFix(flaw.span), code: flaw.fix.join('\n') } : null;
}

/** The verdict's head: right, a false alarm, found, spotted on the wrong line, or missed. */
export function flawHead(r: Result): { correct: boolean; text: string } {
  const flaw = r.q.judge?.flaw;
  const tapped = r.drill?.tapped;
  if (!flaw) return tapped === undefined ? { correct: true, text: flawRight } : { correct: false, text: flawFalseAlarm };
  if (tapped === undefined) return { correct: false, text: flawMissed(flaw.span) };
  return r.drill?.located ? { correct: true, text: flawFound(flaw.span) } : { correct: true, text: flawSpotted(flaw.span) };
}

/** The witness the key rests on: the input, what the correct lines gave and what these gave. */
export function flawWitness(q: Question): string[] {
  const j = q.judge;
  if (!j) return [];
  const model = j.measured.length > 0;
  const clean = j.flaw ? [`${model ? FLAW_MODEL_CLEAN_GIVES : FLAW_CLEAN_GIVES}: \`${j.flaw.cleanOutput}\``] : [];
  const measured = model ? [FLAW_MEASURED, ...j.measured.map((line) => `- ${line}`)] : [];
  return [`${FLAW_INPUT}: \`${j.input}\``, ...clean, `${model ? FLAW_MODEL_GIVES : FLAW_GIVES}: \`${j.output}\``, ...measured];
}
