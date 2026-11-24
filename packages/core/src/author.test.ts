import { describe, expect, it } from 'vitest';

import {
  CLEAR,
  NO_CORRECTION,
  dayLabel,
  gapsLine,
  attentionLine,
  inboxEntry,
  retentionCells,
  stopLabel,
  timeLabel,
  uncostedLine,
  usersLine,
  waitingLine,
  writingsLine,
} from './author';

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

describe('waitingLine', () => {
  it("counts in the pass's terms, and names a missing correction", () => {
    expect(waitingLine({ command: 'claim --by-hand', count: 14 })).toBe('14 of your attempts carry no claim of yours');
    expect(waitingLine({ command: 'match --by-hand', count: 1 })).toBe('1 canonical carries no match of yours');
    expect(waitingLine({ command: 'difficulty judge', count: null })).toBe(NO_CORRECTION);
  });

  it('reads a pass counting nothing as clear', () => {
    expect(waitingLine({ command: 'judge build', count: 0 })).toBe(CLEAR);
  });
});

describe('attentionLine', () => {
  it('counts the flagged served problems, and reads none as clear', () => {
    expect(attentionLine(9)).toBe('9 served problems carry a flag');
    expect(attentionLine(1)).toBe('1 served problem carries a flag');
    expect(attentionLine(0)).toBe(CLEAR);
  });
});

describe('timeLabel', () => {
  it('reads the UTC month, day and minute', () => {
    expect(timeLabel('2026-11-20T14:02:31Z')).toBe('11-20 14:02');
  });
});

describe('gapsLine', () => {
  it('counts the gaps over the core templates alone', () => {
    const rows = [
      { optional: false, gap: true },
      { optional: false, gap: false },
      { optional: true, gap: false },
    ];
    expect(gapsLine(rows)).toBe('1 of 2 core templates carry no solution');
  });
});

describe('inboxEntry', () => {
  it('counts the waiting rows, and reads bare with none', () => {
    expect(inboxEntry(5)).toBe('Inbox 5');
    expect(inboxEntry(0)).toBe('Inbox');
  });
});
