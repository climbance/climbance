import { describe, expect, it } from 'vitest';

import { guide, showsGuidePanel } from './guide';

describe('guide', () => {
  it('names each kind of practice the board offers', () => {
    const { title, body } = guide();
    expect(title).toBe('How practice works');
    for (const kind of ['A sitting', 'A recall', 'Judging a solution', 'Filling a key line', 'A question'])
      expect(body).toContain(`**${kind}**`);
  });
});

describe('showsGuidePanel', () => {
  it('shows only while neither log holds an act', () => {
    expect(showsGuidePanel({ acted: false }, { ready: true, acted: false })).toBe(true);
    expect(showsGuidePanel({ acted: true }, { ready: true, acted: false })).toBe(false);
    expect(showsGuidePanel({ acted: false }, { ready: true, acted: true })).toBe(false);
  });

  it('shows nothing before both logs are read', () => {
    expect(showsGuidePanel(undefined, { ready: true, acted: false })).toBe(false);
    expect(showsGuidePanel({ acted: false }, { ready: false, acted: false })).toBe(false);
  });
});
