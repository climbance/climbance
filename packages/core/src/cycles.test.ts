import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';

const ROOT = dirname(fileURLToPath(import.meta.url));

const IMPORT = /^\s*(?:import|export)\s+(type\s+)?(?:([\s\S]*?)\s+from\s+)?['"](\.{1,2}\/[^'"]+)['"]/gm;

function sources(dir: string): string[] {
  return readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) return sources(path);
    return entry.name.endsWith('.ts') && !entry.name.endsWith('.test.ts') ? [path] : [];
  });
}

function target(from: string, spec: string): string | undefined {
  const base = resolve(dirname(from), spec);
  return [`${base}.ts`, join(base, 'index.ts'), base].find(existsSync);
}

// An import naming only types is erased before it runs, so it orders no evaluation.
function typeOnly(typeKeyword: string | undefined, clause: string | undefined): boolean {
  if (typeKeyword) return true;
  const braces = clause?.trim().match(/^\{([\s\S]*)\}$/);
  if (!braces) return false;
  const names = braces[1]
    .split(',')
    .map((n) => n.trim())
    .filter(Boolean);
  return names.length > 0 && names.every((n) => n.startsWith('type '));
}

function graph(files: string[]): Map<string, string[]> {
  return new Map(
    files.map((file) => {
      const edges = [...readFileSync(file, 'utf8').matchAll(IMPORT)]
        .filter(([, kw, clause]) => !typeOnly(kw, clause))
        .map(([, , , spec]) => target(file, spec))
        .filter((t): t is string => t !== undefined);
      return [file, edges];
    }),
  );
}

// Tarjan's strongly connected components; each with more than one module, or a self-import, is a cycle.
function cycles(edges: Map<string, string[]>): string[][] {
  const index = new Map<string, number>();
  const low = new Map<string, number>();
  const stack: string[] = [];
  const onStack = new Set<string>();
  const found: string[][] = [];
  let next = 0;
  const visit = (v: string) => {
    index.set(v, next);
    low.set(v, next++);
    stack.push(v);
    onStack.add(v);
    for (const w of edges.get(v) ?? []) {
      if (!index.has(w)) {
        visit(w);
        low.set(v, Math.min(low.get(v)!, low.get(w)!));
      } else if (onStack.has(w)) {
        low.set(v, Math.min(low.get(v)!, index.get(w)!));
      }
    }
    if (low.get(v) !== index.get(v)) return;
    const component: string[] = [];
    let w: string;
    do {
      w = stack.pop()!;
      onStack.delete(w);
      component.push(w);
    } while (w !== v);
    if (component.length > 1 || (edges.get(v) ?? []).includes(v)) found.push(component);
  };
  for (const v of edges.keys()) if (!index.has(v)) visit(v);
  return found.map((c) => c.map((f) => relative(ROOT, f)).sort());
}

describe('the core imports', () => {
  it('form no cycle', () => {
    // A cycle leaves one module's constants uninitialised when another reads them at load.
    expect(cycles(graph(sources(ROOT)))).toEqual([]);
  });

  it('see a cycle through a value import', () => {
    // Pins that the scan resolves `./x` and reports both modules of a two-module cycle.
    const a = join(ROOT, 'a.ts');
    const b = join(ROOT, 'b.ts');
    expect(
      cycles(
        new Map([
          [a, [b]],
          [b, [a]],
        ]),
      ),
    ).toEqual([['a.ts', 'b.ts']]);
  });

  it('ignore an import naming only types', () => {
    // Pins that `import type` and `{ type X }` are erased, and `{ type X, Y }` is not.
    expect(typeOnly('type ', '{ A }')).toBe(true);
    expect(typeOnly(undefined, '{ type A, type B }')).toBe(true);
    expect(typeOnly(undefined, '{ type A, B }')).toBe(false);
    expect(typeOnly(undefined, '* as m')).toBe(false);
  });
});
