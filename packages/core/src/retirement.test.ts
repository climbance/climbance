import { describe, expect, it } from 'vitest';

import { requestRetirement, sendableNote, type EngineClient } from './index';

describe('a retirement request', () => {
  it('needs a written note within the bound the engine holds', () => {
    expect(sendableNote('The cases expect sorted indices.')).toBe(true);
    expect(sendableNote(' \n ')).toBe(false);
    expect(sendableNote('x'.repeat(2001))).toBe(false);
  });

  it('names a refusal rather than reading it as sent', async () => {
    const client = { POST: () => Promise.resolve({ error: { detail: 'retired' } }) } as unknown as EngineClient;
    expect(await requestRetirement(client, 'p1', 'defective', 'note')).toEqual({ ok: false, refused: expect.any(String) });
  });
});
