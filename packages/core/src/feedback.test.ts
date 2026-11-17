import { describe, expect, it, vi } from 'vitest';

import { errorReport, reportError, sendFeedback, type EngineClient } from './index';

describe('an error report', () => {
  it('carries the error and where it happened, cut to the bounds the engine holds', () => {
    const report = errorReport(new TypeError('x'.repeat(3000)), 'web', 'build-1', '/problems/p1');
    expect(report).toMatchObject({ client: 'web', version: 'build-1', page: '/problems/p1' });
    expect(report.message.length).toBe(2000);
    expect(report.message.startsWith('TypeError: ')).toBe(true);
  });

  it('is sent once per message, so a render failing in a loop sends one', async () => {
    const POST = vi.fn(() => Promise.resolve({}));
    const client = { POST } as unknown as EngineClient;
    const report = errorReport(new Error('loop'), 'native', '1.0.0', '/');
    await reportError(client, report);
    await reportError(client, report);
    expect(POST).toHaveBeenCalledTimes(1);
  });

  it('never throws, since a failed report has nowhere to go', async () => {
    const client = { POST: () => Promise.reject(new Error('offline')) } as unknown as EngineClient;
    await expect(reportError(client, errorReport('down', 'web', 'b', '/'))).resolves.toBeUndefined();
  });
});

describe('feedback', () => {
  it('names a refusal rather than reading it as sent', async () => {
    const client = { POST: () => Promise.resolve({ error: { detail: 'cap' } }) } as unknown as EngineClient;
    expect(await sendFeedback(client, 'web', '/settings', 'note')).toEqual({ ok: false, refused: expect.any(String) });
  });
});
