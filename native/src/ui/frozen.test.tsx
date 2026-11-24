// @vitest-environment happy-dom
import { act, createContext, memo, type ReactNode, useContext, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { expect, test, vi } from 'vitest';

const nav = vi.hoisted(() => ({ focused: true }));

vi.mock('expo-router', () => ({ useIsFocused: () => nav.focused }));

// the real module opens SQLite and imports react-native, and its relay is its context's provider alone
vi.mock('@/lib/store', async () => {
  const { createContext: make, useContext: read } = await import('react');
  const Ctx = make<{ focus: string } | null>(null);
  return { Ctx, StoreRelay: Ctx.Provider, useStore: () => read(Ctx)! };
});

import * as store from '@/lib/store';
import { Frozen } from './frozen';

const { Ctx } = store as unknown as { Ctx: ReturnType<typeof createContext<{ focus: string } | null>> };

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

let setFocus: (focus: string) => void;
let setShown: (shown: boolean) => void;

// memoized, as a navigator's screen is: a plain child re-renders on thaw and reads the latest anyway
const Screen = memo(function Screen() {
  return <Focus />;
});

function Focus() {
  return <p>{useContext(Ctx)!.focus}</p>;
}

function Provider({ children }: { children: ReactNode }) {
  const [focus, set] = useState('every module');
  setFocus = set;
  return <Ctx.Provider value={{ focus }}>{children}</Ctx.Provider>;
}

function Tab({ children }: { children: ReactNode }) {
  const [, show] = useState(true);
  setShown = (shown) => {
    nav.focused = shown;
    show(shown);
  };
  return <Frozen>{children}</Frozen>;
}

test('a thawed tab shows the store value set while it was frozen', async () => {
  /** The Practice tab kept the focus it froze with, so Continue served every module. */
  const host = document.createElement('div');
  const root = createRoot(host);
  await act(async () =>
    root.render(
      <Provider>
        <Tab>
          <Screen />
        </Tab>
      </Provider>,
    ),
  );
  await act(async () => setShown(false));
  await act(async () => setFocus('py'));
  await act(async () => setShown(true));
  expect(host.textContent).toBe('py');
  root.unmount();
});
