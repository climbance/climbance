import { describe, expect, it } from 'vitest'

import { stepKey } from '@/lib/stepRows'

describe('stepKey', () => {
  const keys = ['a', 'b', 'c']
  it('starts at the first row on j and the last on k when no row is at the cursor', () => {
    expect(stepKey(keys, null, 1)).toBe('a')
    expect(stepKey(keys, null, -1)).toBe('c')
    expect(stepKey(keys, 'gone', 1)).toBe('a')
  })
  it('moves one row and holds at either end', () => {
    expect(stepKey(keys, 'a', 1)).toBe('b')
    expect(stepKey(keys, 'b', -1)).toBe('a')
    expect(stepKey(keys, 'c', 1)).toBe('c')
    expect(stepKey(keys, 'a', -1)).toBe('a')
  })
  it('answers nothing on an empty list', () => {
    expect(stepKey([], null, 1)).toBeUndefined()
  })
})
