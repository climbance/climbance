import { errorReport, reportError } from '@climb/core'

import { api } from '@/api/client'

/** Sends an error this page did not handle to the author: `api/README.md`. */
export const reported = (error: unknown) =>
  void reportError(api, errorReport(error, 'web', __BUILT__, window.location.pathname))

/** An error no handler caught, and a promise no one awaited. */
export function reportUncaught() {
  window.addEventListener('error', (event) => reported(event.error ?? event.message))
  window.addEventListener('unhandledrejection', (event) => reported(event.reason))
}
