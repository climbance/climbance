// what a spot-the-flaw drill says, for every platform: `content-repo/ai-drills.md`
export const FLAW_CLEAN = 'Correct';
export const FLAW_TAP = 'Or tap the first line that is wrong.';
export const FLAW_INPUT = 'Input';
export const FLAW_GIVES = 'These lines give';
export const FLAW_CLEAN_GIVES = 'The correct lines give';
export const FLAW_MODEL_GIVES = 'A model answered these lines';
export const FLAW_MODEL_CLEAN_GIVES = 'A model answered the correct lines';
export const FLAW_MEASURED = 'Measured on each model:';
export const FLAW_CALLED_CLEAN = 'Correct, no line is wrong';

/** One line, or a span of lines, as a verdict names it. */
export function linesNamed([first, last]: [number, number]): string {
  return first === last ? `line ${first}` : `lines ${first} to ${last}`;
}

export const flawFix = (span: [number, number]) => `${capital(linesNamed(span))} should read`;
export const flawRight = '✓ Correct: no line is wrong.';
export const flawFalseAlarm = '✗ The lines were correct: no line is wrong.';
export const flawFound = (span: [number, number]) => `✓ Found: the flaw is on ${linesNamed(span)}.`;
export const flawSpotted = (span: [number, number]) =>
  `Right that a line is wrong, but the flaw is on ${linesNamed(span)}.`;
export const flawMissed = (span: [number, number]) => `✗ Missed: the flaw is on ${linesNamed(span)}.`;
export const flawTappedLine = (line: number) => `line ${line}`;

const capital = (text: string) => text[0].toUpperCase() + text.slice(1);
