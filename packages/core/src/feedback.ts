import { described, type EngineClient } from './engine';
import type { Outcome } from './sittingrun';

export type Client = 'web' | 'native';

/** Sends the user's note to the author, with the page it was sent from. */
export async function sendFeedback(
  client: EngineClient,
  from: Client,
  page: string,
  note: string,
): Promise<Outcome<null>> {
  try {
    const { error } = await client.POST('/api/feedback', {
      body: { client: from, page: page.slice(0, 200), note },
    });
    return error === undefined ? { ok: true, value: null } : { ok: false, refused: described(error) };
  } catch (reason) {
    return { ok: false, refused: String(reason) };
  }
}

export interface ErrorReport {
  client: Client;
  version: string;
  page: string;
  message: string;
  stack: string | null;
}

/** An error as the engine takes it, cut to the bounds it holds. */
export function errorReport(error: unknown, from: Client, version: string, page: string): ErrorReport {
  const message = error instanceof Error ? `${error.name}: ${error.message}` : String(error);
  const stack = error instanceof Error && error.stack ? error.stack.slice(0, 8000) : null;
  return { client: from, version: version.slice(0, 50), page: page.slice(0, 200), message: message.slice(0, 2000), stack };
}

// once per message per load: a render failing in a loop sends one report
const reported = new Set<string>();

/** Sends the report once, and never throws: a failed report has nowhere else to go. */
export async function reportError(client: EngineClient, report: ErrorReport): Promise<void> {
  if (reported.has(report.message)) return;
  reported.add(report.message);
  try {
    await client.POST('/api/errors', { body: report });
  } catch {
    // offline, or the engine is the thing that broke
  }
}
