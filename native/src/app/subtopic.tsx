import { router, useLocalSearchParams } from 'expo-router';
import { useMemo } from 'react';
import { ScrollView, View } from 'react-native';
import { Text, useTheme } from 'react-native-paper';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import {
  lessonRow,
  lessonStats,
  OF,
  SUBTOPIC_CARDS,
  SUBTOPIC_LESSONS,
  SUBTOPIC_LEVELS,
  SUBTOPIC_MISSING,
  SUBTOPIC_NO_LESSONS,
  subtopicCards,
  subtopicView,
} from '@climb/core';
import { useStore } from '@/lib/store';
import { useEngine } from '@/lib/useEngine';
import { Blank, fromCopy, Loaded, styles, ScreenHeader } from '@/ui/common';
import { Heading, PickPanel, PickRow } from '@/ui/rows';
import { space } from '@/ui/tokens';

/** A subtopic's levels, its lessons and its cards, as the web's page. Its presses stay on Module. */
export default function SubtopicScreen() {
  const st = useStore();
  const theme = useTheme();
  const insets = useSafeAreaInsets();
  const { course = '', sub = '' } = useLocalSearchParams<{ course: string; sub: string }>();
  // the cards add to the screen, so a failed list reads as none, as on the web
  const listed = useEngine('/api/cards');
  const { board } = st;
  const page = useMemo(() => {
    const c = st.catalog?.courses.find((one) => one.slug === course);
    const b = board(null);
    return c && b ? { c, b, view: subtopicView(b, c, sub) } : null;
  }, [st.catalog, board, course, sub]);

  return (
    <View style={{ flex: 1, backgroundColor: theme.colors.background }}>
      <ScreenHeader title={page?.view?.title ?? sub} note={page ? [page.c.title] : []} />
      <ScrollView contentContainerStyle={[styles.page, { paddingBottom: insets.bottom + 24 }]}>
        <Loaded
          of={OF.subtopic}
          state={fromCopy(st, st.catalog ? { page } : null)}
          blank={SUBTOPIC_MISSING}
          blankWhen={(x) => !x.page?.view}
        >
          {({ page }) => {
            if (!page?.view) return null;
            const { c, b, view } = page;
            const cards = subtopicCards(c, sub, listed.data ?? []);
            return (
              <View style={{ gap: space[4] }}>
                {view.levels.length ? (
                  <View style={{ gap: space[1.5] }}>
                    <Heading sub title={SUBTOPIC_LEVELS} />
                    {view.levels.map((line) => (
                      <Text key={line} variant="bodyMedium">
                        {line}
                      </Text>
                    ))}
                  </View>
                ) : null}
                <Heading title={SUBTOPIC_LESSONS} count={view.lessons.length} />
                {view.lessons.length ? (
                  <PickPanel>
                    {view.lessons.map((x) => {
                      const row = lessonRow(b, c, x);
                      return (
                        <PickRow
                          key={x.slug}
                          title={x.title}
                          stats={lessonStats(row.status, row.minutes)}
                          dim={row.state === 'locked'}
                          onPress={() => router.push({ pathname: '/lesson', params: { course: c.slug, slug: x.slug } })}
                        />
                      );
                    })}
                  </PickPanel>
                ) : (
                  <Blank>{SUBTOPIC_NO_LESSONS}</Blank>
                )}
                {cards.length ? (
                  <View style={{ gap: space[1.5] }}>
                    <Heading sub title={SUBTOPIC_CARDS} />
                    <View style={{ flexDirection: 'row', flexWrap: 'wrap', columnGap: 16, rowGap: 6 }}>
                      {cards.map((card) => (
                        <Text
                          key={card.slug}
                          variant="bodyMedium"
                          accessibilityRole="link"
                          onPress={() => router.push({ pathname: '/card', params: { slug: card.slug } })}
                          style={{ color: theme.colors.primary }}
                        >
                          {card.title}
                        </Text>
                      ))}
                    </View>
                  </View>
                ) : null}
              </View>
            );
          }}
        </Loaded>
      </ScrollView>
    </View>
  );
}
