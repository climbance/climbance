import { useIsFocused } from 'expo-router';
import type { ReactNode } from 'react';
import { Freeze } from 'react-freeze';

import { StoreRelay, useStore } from '@/lib/store';

// Expo Router turns the navigators' own `freezeOnBlur` off. The store is
// provided again below the freeze: `native-app/README.md`
export function Frozen({ children }: { children: ReactNode }) {
  const store = useStore();
  const focused = useIsFocused();
  return (
    <Freeze freeze={!focused}>
      <StoreRelay value={store}>{children}</StoreRelay>
    </Freeze>
  );
}
