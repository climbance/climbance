import Constants from 'expo-constants';

import { errorReport, reportError } from '@climb/core';
import { engine } from '@/lib/engine';
import { getToken } from '@/lib/settings';

/** Sends an error the app did not handle to the author: `README.md`, Boundaries. */
export async function reported(origin: string, error: unknown, page: string) {
  const token = await getToken().catch(() => null);
  // signed out, or no engine named: the engine takes a report from a session alone
  if (!origin || !token) return;
  const version = Constants.expoConfig?.version ?? 'unknown';
  await reportError(engine(origin, token), errorReport(error, 'native', version, page));
}

/** Every error no handler caught, passed on to the handler that was there before. */
export function reportUncaught(origin: () => string, page: () => string) {
  const before = ErrorUtils.getGlobalHandler();
  ErrorUtils.setGlobalHandler((error, fatal) => {
    void reported(origin(), error, page());
    before(error, fatal);
  });
}
