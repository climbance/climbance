import { describe, expect, it } from 'vitest';

import { FILL_BLANK, filledLine, separatingLines } from './index';
import type { components } from './api/schema';

type Served = components['schemas']['FilledItem'];

const item = {
  lines: ['def solve(xs):', '    ', '    return lo'],
  blank: 2,
  choices: [],
} as unknown as Served;

describe('a served item', () => {
  it('marks the blank under the line its indent keeps', () => {
    expect(filledLine(item, 1, null)).toBe(`    ${FILL_BLANK}`);
    expect(filledLine(item, 0, null)).toBe('def solve(xs):');
  });

  it("fills the blank with the form's line once decided", () => {
    expect(filledLine(item, 1, { right: false, line: 'lo = 0', case: null })).toBe('    lo = 0');
  });

  it("shows a wrong choice's separating case", () => {
    const lines = separatingLines({ case: { args: [[1, 3], 3], expected: 1, outcome: 'wrong', returned: 0 } });
    expect(lines).toEqual(['solve([1,3], 3)', 'expected 1', 'the flawed code returned 0']);
  });
});
