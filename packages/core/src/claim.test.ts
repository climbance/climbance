import { describe, expect, it } from 'vitest';

import { attemptCode, attemptLine, claimDefault, claimMissing, claimReady, claimToggled, type components } from './index';

type Attempt = components['schemas']['Attempt'];

describe('the claim', () => {
  it('ticks the drilled technique where the problem carries it, and nothing else', () => {
    expect(claimDefault('dp', ['dp', 'greedy'])).toEqual(['dp']);
    expect(claimDefault('bfs', ['dp', 'greedy'])).toEqual([]);
    expect(claimDefault(null, ['dp'])).toEqual([]);
  });

  it('toggles a tick on and off', () => {
    expect(claimToggled(['dp'], 'greedy')).toEqual(['dp', 'greedy']);
    expect(claimToggled(['dp', 'greedy'], 'dp')).toEqual(['greedy']);
  });

  it('saves once it names a technique or declines, and says how sure', () => {
    expect(claimReady(['dp'], false, 'sure')).toBe(true);
    expect(claimReady([], true, 'guess')).toBe(true);
    expect(claimReady([], false, 'sure')).toBe(false);
    expect(claimReady(['dp'], false, null)).toBe(false);
  });

  it('names what Save still waits for, the technique before the confidence', () => {
    /** the label is optional, so a disabled Save has to say which required answer is missing */
    expect(claimMissing([], false, null)).toMatch(/technique/);
    expect(claimMissing(['dp'], false, null)).toMatch(/how sure/);
    expect(claimMissing([], true, 'guess')).toBeNull();
  });

  it('shows an earlier attempt its own code, and the last none', () => {
    /** the editor behind the sheet holds the last attempt's code, so only earlier ones need theirs */
    const attempt = { code: 'def solve(): pass' } as Attempt;
    expect(attemptCode(0, 2, attempt)).toBe('def solve(): pass');
    expect(attemptCode(1, 2, attempt)).toBeNull();
  });

  it('names the attempt, its verdict and its time', () => {
    const attempt = { solved: true, time_to_solve_sec: 125 } as Attempt;
    expect(attemptLine(0, 2, attempt)).toBe('Attempt 1 of 2 · solved · 2:05');
    expect(attemptLine(1, 2, { solved: false, time_to_solve_sec: null } as Attempt)).toBe(
      'Attempt 2 of 2 · not solved',
    );
  });
});
