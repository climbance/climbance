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

// pages are cut in the browser, over every matching row: `browser.md`
export const PAGE_SIZE = 50;

export interface GridPage<R> {
  rows: R[];
  page: number;
  pages: number;
}

/** The page the URL names, from 1; a page past the last reads as the last. */
export function gridPage<R>(rows: R[], page: number): GridPage<R> {
  const pages = Math.max(1, Math.ceil(rows.length / PAGE_SIZE));
  const at = Math.min(Math.max(1, page), pages);
  const start = (at - 1) * PAGE_SIZE;
  return { rows: rows.slice(start, start + PAGE_SIZE), page: at, pages };
}

export function pageNumber(get: (name: string) => string | null): number {
  const page = get('page');
  return page !== null && /^\d+$/.test(page) ? Number(page) : 1;
}

/** The page holding the row at `index` among every matching row. */
export const pageHolding = (index: number) => Math.floor(index / PAGE_SIZE) + 1;

/** The query with the page set; the first page stays out of the URL. */
export function pageQuery(query: string, page: number): string {
  const q = new URLSearchParams(query);
  if (page > 1) q.set('page', String(page));
  else q.delete('page');
  return q.toString();
}
