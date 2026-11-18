import type { components } from './api/schema';
import { described, type EngineClient } from './engine';
import type { Outcome } from './sittingrun';

type Served = components['schemas']['FilledItem'];
type Decided = components['schemas']['FillDecided'];

export const FILL_TITLE = 'Fill the key line';
export const FILL_NOTE = 'One line of the form is blank. Pick the line that belongs there.';
export const FILL_PICK = 'Which line goes in the blank?';
export const FILL_NEXT = 'Next';
export const FILL_NONE = 'No form is left to fill here.';
export const FILL_RIGHT = 'Right: that line belongs there.';
export const FILL_WRONG = 'Wrong: another line belongs there.';
export const fillFrom = (cardTitle: string) => `Fill ${cardTitle}`;
/** The blank as the code shows it, under the line's own indent. */
export const FILL_BLANK = '▁▁▁▁▁▁';

/** Whether the line at `index` is a row of the blank, which spans the whole statement. */
export const inBlank = (item: Served, index: number) => index + 1 >= item.blank && index + 1 <= item.blank_end;

/** The line the code shows at `index`: the blank's marker, or the form's statement once decided. */
export function filledLine(item: Served, index: number, decided: Decided | null): string {
  const line = item.lines[index] ?? '';
  if (!inBlank(item, index)) return line;
  const head = item.lines[item.blank - 1] ?? '';
  const row = index + 1 - item.blank;
  if (decided) return head + (decided.line.split('\n')[row] ?? '');
  return row === 0 ? head + FILL_BLANK : '';
}

/** The next item to fill, from every card or from one. `null` where none is left. */
export async function nextFilled(client: EngineClient, card: string | null): Promise<Outcome<Served | null>> {
  try {
    const { data, error, response } = await client.GET('/api/filling/next', {
      params: { query: card ? { card } : {} },
    });
    if (response.status === 404 && card === null) return { ok: true, value: null };
    if (response.status === 404 && error && described(error) === 'no item to fill') return { ok: true, value: null };
    return error === undefined && data ? { ok: true, value: data } : { ok: false, refused: described(error) };
  } catch (reason) {
    return { ok: false, refused: String(reason) };
  }
}

/** Sends one fill: the picked choice, by the position the item names it by. */
export async function fill(client: EngineClient, itemId: string, choice: number): Promise<Outcome<Decided>> {
  try {
    const { data, error } = await client.POST('/api/filling/{item_id}', {
      params: { path: { item_id: itemId } },
      body: { choice },
    });
    return error === undefined && data ? { ok: true, value: data } : { ok: false, refused: described(error) };
  } catch (reason) {
    return { ok: false, refused: String(reason) };
  }
}
