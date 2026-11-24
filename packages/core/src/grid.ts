// a browser page's grid, its columns and its sort: `web-app/pages/author/browser.md`

export type SortOrder = 'asc' | 'desc';

export interface GridSort {
  column: string;
  order: SortOrder;
}

export interface GridColumn<R> {
  id: string;
  header: string;
  /** What the column sorts by; a column without one does not sort. */
  sortBy?: (row: R) => string | number | null;
  /** A number or a date: highest first on the first press. */
  numeric?: boolean;
}

const firstOrder = (column: GridColumn<never>): SortOrder => (column.numeric ? 'desc' : 'asc');

/** The sort the URL names, or none where it names no sortable column. */
export function gridSort<R>(get: (name: string) => string | null, columns: GridColumn<R>[]): GridSort | null {
  const column = columns.find((one) => one.sortBy && one.id === get('sort'));
  if (!column) return null;
  const order = get('order');
  return { column: column.id, order: order === 'asc' || order === 'desc' ? order : firstOrder(column) };
}

/** A press on a header: the column's first order, or the order reversed on a second press. */
export function gridPressed<R>(sort: GridSort | null, column: GridColumn<R>): GridSort {
  if (sort?.column === column.id) return { column: column.id, order: sort.order === 'asc' ? 'desc' : 'asc' };
  return { column: column.id, order: firstOrder(column) };
}

/** The page's own query with the sort added; the column's first order stays out of the URL. */
export function gridQuery<R>(query: string, sort: GridSort | null, columns: GridColumn<R>[]): string {
  const q = new URLSearchParams(query);
  const column = sort && columns.find((one) => one.id === sort.column);
  if (sort && column) {
    q.set('sort', sort.column);
    if (sort.order !== firstOrder(column)) q.set('order', sort.order);
  }
  return q.toString();
}

/** Stable, so the page's own order breaks a tie; a row with no value reads last in either order. */
export function gridSorted<R>(rows: R[], columns: GridColumn<R>[], sort: GridSort | null): R[] {
  const by = sort && columns.find((one) => one.id === sort.column)?.sortBy;
  if (!sort || !by) return rows;
  const sign = sort.order === 'asc' ? 1 : -1;
  return [...rows].sort((a, b) => {
    const x = by(a);
    const y = by(b);
    if (x === null || y === null) return x === y ? 0 : x === null ? 1 : -1;
    return sign * (typeof x === 'number' && typeof y === 'number' ? x - y : String(x).localeCompare(String(y)));
  });
}
