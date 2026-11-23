import { ScrollView, View } from 'react-native';
import { Text, useTheme } from 'react-native-paper';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { termsOfUse, lastUpdated } from '@climb/core';
import { styles, ScreenHeader } from '@/ui/common';
import { Markdown } from '@/ui/markdown';

const TERMS = termsOfUse();

/** The terms of use, the text the web serves at `/terms`, held in the app so it reads offline. */
export default function TermsScreen() {
  const theme = useTheme();
  const insets = useSafeAreaInsets();
  return (
    <View style={{ flex: 1, backgroundColor: theme.colors.background }}>
      <ScreenHeader title={TERMS.title} />
      <ScrollView contentContainerStyle={[styles.page, { paddingBottom: insets.bottom + 24 }]}>
        {TERMS.updated ? (
          <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
            {lastUpdated(TERMS.updated)}
          </Text>
        ) : null}
        <Markdown>{TERMS.body}</Markdown>
      </ScrollView>
    </View>
  );
}
