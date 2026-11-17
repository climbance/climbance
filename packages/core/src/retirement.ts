import { described, type EngineClient } from './engine';
import type { Outcome } from './sittingrun';

export type RetirementReason = 'defective' | 'copied';

/** Whether a note can be sent: the engine refuses a blank one and one over 2000 characters. */
export const sendableNote = (note: string) => /\S/.test(note) && note.length <= 2000;

/** Asks the author to retire a problem. A refusal is named rather than read as sent. */
export async function requestRetirement(
  client: EngineClient,
  problemId: string,
  reason: RetirementReason,
  note: string,
): Promise<Outcome<null>> {
  try {
    const { error } = await client.POST('/api/problems/{problem_id}/retirement-requests', {
      params: { path: { problem_id: problemId } },
      body: { reason, note },
    });
    return error === undefined ? { ok: true, value: null } : { ok: false, refused: described(error) };
  } catch (reason) {
    return { ok: false, refused: String(reason) };
  }
}
