import { describe, expect, it } from 'vitest';

import { dayLabel, retentionCells, stopLabel, uncostedLine, usersLine, writingsLine } from './author';

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

describe('retentionCells', () => {
  it('reads m of n beside the share, and none yet over no user', () => {
    expect(retentionCells({ after_days: 7, counted: 7, retained: 4 })).toEqual(['4 of 7', '57%']);
    expect(retentionCells({ after_days: 30, counted: 0, retained: 0 })).toEqual(['none yet', '']);
  });
});

describe('usersLine', () => {
  it('names the three counts as the wireframe draws them', () => {
    expect(usersLine(12, 9, 5, 7)).toBe('12 invited · 9 signed in · 5 active in the last 7 days');
  });
});

describe('dayLabel', () => {
  it('drops the year', () => {
    expect(dayLabel('2026-11-23')).toBe('11-23');
  });
});
