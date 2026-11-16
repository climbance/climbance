import { useLocalSearchParams } from 'expo-router';
import { useEffect, useState } from 'react';
import { Pressable, ScrollView, View } from 'react-native';
import { Text, useTheme } from 'react-native-paper';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import {
  FILL_NEXT,
  FILL_NONE,
  FILL_PICK,
  FILL_RIGHT,
  FILL_TITLE,
  FILL_WRONG,
  type components,
  fill,
  filledLine,
  judgeDepth,
  judgeExample,
  nextFilled,
  separatingLines,
} from '@climb/core';
import { engine } from '@/lib/engine';
import { getToken } from '@/lib/settings';
import { useStore } from '@/lib/store';
import { BottomBar, ErrorLine, optionTile, Press, ScreenHeader, styles, tones } from '@/ui/common';
import { font, space } from '@/ui/tokens';

type FilledItem = components['schemas']['FilledItem'];
type FillDecided = components['schemas']['FillDecided'];

/** Filling a key line, as the web's page: `pages.md`, Filling a key line. */
export default function FillScreen() {
  const theme = useTheme();
  const insets = useSafeAreaInsets();
  const st = useStore();
  const { card } = useLocalSearchParams<{ card?: string }>();
  const [item, setItem] = useState<FilledItem | null | undefined>(undefined);
  const [picked, setPicked] = useState<number | null>(null);
  const [decided, setDecided] = useState<FillDecided | null>(null);
  const [refused, setRefused] = useState<string | null>(null);
  const [round, setRound] = useState(0);

  useEffect(() => {
    let live = true;
    void (async () => {
      const next = await nextFilled(engine(st.settings.origin, await getToken()), card ?? null);
      if (!live) return;
      if (next.ok) setItem(next.value);
      else setRefused(next.refused);
    })();
    return () => {
      live = false;
    };
  }, [card, round, st.settings.origin]);

  const send = async (choice: number) => {
    if (!item) return;
    setPicked(choice);
    const answered = await fill(engine(st.settings.origin, await getToken()), item.item_id, choice);
    if (answered.ok) setDecided(answered.value);
    else setRefused(answered.refused);
  };

  const another = () => {
    setPicked(null);
    setDecided(null);
    setRefused(null);
    setRound((one) => one + 1);
  };

  const muted = { color: theme.colors.onSurfaceVariant };
  const verdictColor = decided?.right ? tones(theme.dark).done : theme.colors.error;
  return (
    <View style={{ flex: 1, backgroundColor: theme.colors.background }}>
      <ScreenHeader
        title={item ? item.template_title : FILL_TITLE}
        note={[item ? `${item.card_title} · ${judgeDepth(item.depth)}` : null]}
      />
      <ScrollView contentContainerStyle={[styles.page, { paddingBottom: insets.bottom + 160 }]}>
        {refused ? <ErrorLine>{refused}</ErrorLine> : null}
        {item === null ? <Text style={muted}>{FILL_NONE}</Text> : null}
        {item ? (
          <>
            <Text style={muted}>{item.asks}</Text>
            <Text style={{ fontFamily: font.mono }}>{judgeExample(item.example)}</Text>
            <View style={{ borderRadius: 12, overflow: 'hidden', backgroundColor: theme.colors.surfaceVariant }}>
              {item.lines.map((_, index) => {
                const number = index + 1;
                const blank = number === item.blank;
                return (
                  <View
                    key={number}
                    style={{
                      flexDirection: 'row',
                      gap: space[2],
                      paddingVertical: 3,
                      paddingHorizontal: space[2],
                      backgroundColor: blank ? theme.colors.secondaryContainer : undefined,
                      borderLeftWidth: blank && decided ? 4 : 0,
                      borderLeftColor: verdictColor,
                    }}
                  >
                    <Text style={[{ fontFamily: font.mono, width: 22, textAlign: 'right' }, muted]}>{number}</Text>
                    <Text style={{ fontFamily: font.mono, flex: 1 }}>{filledLine(item, index, decided) || ' '}</Text>
                  </View>
                );
              })}
            </View>
            {!decided ? <Text style={muted}>{FILL_PICK}</Text> : null}
            <View style={{ gap: space[2] }}>
              {item.choices.map((one) => (
                <Pressable
                  key={one.choice}
                  disabled={picked !== null}
                  onPress={() => void send(one.choice)}
                  accessibilityRole="radio"
                  accessibilityState={{ checked: picked === one.choice, disabled: picked !== null }}
                  style={optionTile(picked === one.choice, theme)}
                >
                  <Text style={{ fontFamily: font.mono }}>{one.text}</Text>
                </Pressable>
              ))}
            </View>
            {decided ? (
              <View style={{ gap: space[1] }}>
                <Text variant="titleSmall" style={{ color: verdictColor }}>
                  {decided.right ? FILL_RIGHT : FILL_WRONG}
                </Text>
                {separatingLines(decided).map((line) => (
                  <Text key={line} style={{ fontFamily: font.mono }}>
                    {line}
                  </Text>
                ))}
              </View>
            ) : null}
          </>
        ) : null}
      </ScrollView>
      {item && decided ? (
        <BottomBar bottom={insets.bottom}>
          <Press onPress={another}>{FILL_NEXT}</Press>
        </BottomBar>
      ) : null}
    </View>
  );
}
