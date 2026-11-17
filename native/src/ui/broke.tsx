import { usePathname } from 'expo-router';
import { Component, useEffect, useRef, type ReactNode } from 'react';
import { View } from 'react-native';
import { Button, Text, useTheme } from 'react-native-paper';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { BROKE_EXPLAINED, BROKE_TITLE, RELOAD } from '@climb/core';
import { reported, reportUncaught } from '@/lib/reported';
import { useStore } from '@/lib/store';
import { SendFeedback } from '@/ui/feedback';
import { space } from '@/ui/tokens';

/** The screens, with a screen that threw replaced by one saying so, as the web's does. */
export function Broke({ children }: { children: ReactNode }) {
  const st = useStore();
  const page = usePathname();
  const now = useRef({ origin: st.settings.origin, page });
  now.current = { origin: st.settings.origin, page };
  useEffect(() => {
    reportUncaught(
      () => now.current.origin,
      () => now.current.page,
    );
  }, []);
  return <Boundary onError={(error) => void reported(st.settings.origin, error, page)}>{children}</Boundary>;
}

class Boundary extends Component<{ children: ReactNode; onError: (error: unknown) => void }, { broke: boolean }> {
  state = { broke: false };

  static getDerivedStateFromError() {
    return { broke: true };
  }

  componentDidCatch(error: unknown) {
    this.props.onError(error);
  }

  render() {
    if (!this.state.broke) return this.props.children;
    return <Fallback onReload={() => this.setState({ broke: false })} />;
  }
}

function Fallback({ onReload }: { onReload: () => void }) {
  const theme = useTheme();
  const insets = useSafeAreaInsets();
  return (
    <View
      style={{
        flex: 1,
        padding: space.gutter,
        paddingTop: insets.top + space.gutter,
        gap: space.stack,
        backgroundColor: theme.colors.background,
      }}
    >
      <Text variant="headlineSmall">{BROKE_TITLE}</Text>
      <Text variant="bodyMedium" style={{ color: theme.colors.onSurfaceVariant }}>
        {BROKE_EXPLAINED}
      </Text>
      <Button mode="contained" style={{ alignSelf: 'flex-start' }} onPress={onReload}>
        {RELOAD}
      </Button>
      <SendFeedback />
    </View>
  );
}
