import { describe, expect, it } from 'vitest';

import { gridPressed, gridQuery, gridSort, gridSorted, type GridColumn } from './index';

type Row = { name: string; score: number | null };

const columns: GridColumn<Row>[] = [
  { id: 'name', header: 'Name', sortBy: (r) => r.name },
  { id: 'score', header: 'Score', sortBy: (r) => r.score, numeric: true },
  { id: 'note', header: 'Note' },
];
const rows: Row[] = [
  { name: 'b', score: 2 },
  { name: 'a', score: null },
  { name: 'c', score: 9 },
];
const params = (query: string) => {
  const q = new URLSearchParams(query);
  return (name: string) => q.get(name);
};

describe('the grid', () => {
  it('sorts a number highest first and a text from A on the first press', () => {
    expect(gridPressed(null, columns[1])).toEqual({ column: 'score', order: 'desc' });
    expect(gridPressed(null, columns[0])).toEqual({ column: 'name', order: 'asc' });
  });

  it('reverses the order on a second press of the same header', () => {
    const once = gridPressed(null, columns[1]);

    expect(gridPressed(once, columns[1])).toEqual({ column: 'score', order: 'asc' });
    expect(gridPressed(once, columns[0])).toEqual({ column: 'name', order: 'asc' });
  });

  it('keeps a row with no value last in either order', () => {
    const by = (order: 'asc' | 'desc') => gridSorted(rows, columns, { column: 'score', order }).map((r) => r.name);

    expect(by('desc')).toEqual(['c', 'b', 'a']);
    expect(by('asc')).toEqual(['b', 'c', 'a']);
  });

  it("keeps the page's own order with no sort, or a sort naming a column that does not sort", () => {
    expect(gridSort(params('sort=note'), columns)).toBeNull();
    expect(gridSorted(rows, columns, null)).toBe(rows);
  });

  it("writes the sort to the URL, the column's first order left out", () => {
    expect(gridQuery('module=py', { column: 'score', order: 'desc' }, columns)).toBe('module=py&sort=score');
    expect(gridQuery('', { column: 'score', order: 'asc' }, columns)).toBe('sort=score&order=asc');
    expect(gridSort(params('sort=score&order=asc'), columns)).toEqual({ column: 'score', order: 'asc' });
    expect(gridSort(params('sort=score'), columns)).toEqual({ column: 'score', order: 'desc' });
  });
});
