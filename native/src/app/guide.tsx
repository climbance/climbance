import { ScrollView, View } from 'react-native';
import { useTheme } from 'react-native-paper';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { guide } from '@climb/core';
import { styles, ScreenHeader } from '@/ui/common';
import { Markdown } from '@/ui/markdown';

const GUIDE = guide();

/** The guide, the text the web serves at `/start`, held in the app so it reads offline. */
export default function GuideScreen() {
  const theme = useTheme();
  const insets = useSafeAreaInsets();
  return (
    <View style={{ flex: 1, backgroundColor: theme.colors.background }}>
      <ScreenHeader title={GUIDE.title} />
      <ScrollView contentContainerStyle={[styles.page, { paddingBottom: insets.bottom + 24 }]}>
        <Markdown>{GUIDE.body}</Markdown>
      </ScrollView>
    </View>
  );
}
