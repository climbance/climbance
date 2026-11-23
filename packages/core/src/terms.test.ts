import { describe, expect, it } from 'vitest';

import { termsOfUse } from './index';

describe('the terms of use', () => {
  it('holds the text both clients render, dated', () => {
    expect(termsOfUse().title).toBe('Terms of use');
    expect(termsOfUse().updated).not.toBeNull();
  });

  it('links no page of the app, which the phone would hand to the system', () => {
    expect(termsOfUse().body).not.toMatch(/\]\(\//);
  });
});
