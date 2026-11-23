import { describe, expect, it } from 'vitest';

import { stopLabel, uncostedLine, writingsLine } from './author';

describe('writingsLine', () => {
  it('rounds the rate and names none over no writing', () => {
    expect(writingsLine(42, 17)).toBe('42 writings · 17 landed · 40%');
    expect(writingsLine(0, 0)).toBe('0 writings · 0 landed');
  });
});

describe('stopLabel', () => {
  it('names the site beside its gate, and a gate no site raised alone', () => {
    expect(stopLabel({ site: 'screen', gate: 'copied', held_at: null, writings: 1 })).toBe('screen · copied');
    expect(stopLabel({ site: null, gate: 'unexercised', held_at: null, writings: 1 })).toBe('unexercised');
    expect(stopLabel({ site: null, gate: null, held_at: 'paced', writings: 1 })).toBe('held at paced');
  });
});

describe('uncostedLine', () => {
  it('says nothing where every outcome carries a cost', () => {
    expect(uncostedLine(0)).toBeNull();
    expect(uncostedLine(1)).toBe('1 site outcome carries no cost');
  });
});
