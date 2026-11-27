// what a read-the-trace drill says, for every platform: `content-repo/ai-drills.md`
export const TRACE_TAP = 'Tap the first step that is wrong.';
export const TRACE_ENDS = 'The run ends with';
export const TRACE_CORRECTED_ENDS = 'The corrected run ends with';
export const TRACE_AGENT = 'Agent';

export const traceStep = (n: number) => `step ${n}`;
export const traceCorrected = (k: number) => `From step ${k}, the corrected run`;
export const traceFound = (k: number) => `✓ Found: step ${k} is the first wrong step.`;
export const traceMissed = (k: number) => `✗ The first wrong step is step ${k}.`;
