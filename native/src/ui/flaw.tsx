import { Pressable, View } from 'react-native';
import { Text, useTheme } from 'react-native-paper';

import { FLAW_CLEAN, FLAW_TAP, flawFixShown, flawLines, type Question } from '@climb/core';
import { Press } from '@/ui/common';
import { font, radius, space } from '@/ui/tokens';

/**
 * A spot-the-flaw drill's lines, each a tap target until answered, then the
 * flawed span marked and what it reads clean. `content-repo/ai-drills.md`
 */
export function FlawStated({
  q,
  tapped,
  answered,
  onTap,
}: {
  q: Question;
  tapped: number | null;
  answered: boolean;
  onTap?: (line: number) => void;
}) {
  const theme = useTheme();
  if (!q.judge) return null;
  const muted = { color: theme.colors.onSurfaceVariant };
  const fix = answered ? flawFixShown(q) : null;
  return (
    <View style={{ gap: space[2] }}>
      <View
        style={{ borderRadius: radius(theme).xl, overflow: 'hidden', backgroundColor: theme.colors.surfaceVariant }}
      >
        {flawLines(q, tapped, answered).map((line) => (
          <Pressable
            key={line.n}
            disabled={!onTap}
            onPress={() => onTap?.(line.n)}
            accessibilityRole="button"
            accessibilityLabel={`line ${line.n}: ${line.text}`}
            style={{
              flexDirection: 'row',
              gap: space[2],
              paddingVertical: 3,
              paddingHorizontal: space[2],
              backgroundColor: line.tapped ? theme.colors.secondaryContainer : undefined,
              borderLeftWidth: line.flawed ? 4 : 0,
              borderLeftColor: theme.colors.error,
            }}
          >
            <Text style={[{ fontFamily: font.mono, width: 22, textAlign: 'right' }, muted]}>{line.n}</Text>
            <Text style={{ fontFamily: font.mono, flex: 1 }}>{line.text || ' '}</Text>
          </Pressable>
        ))}
      </View>
      {fix ? (
        <View style={{ gap: space[1] }}>
          <Text style={muted}>{fix.label}</Text>
          <Text style={{ fontFamily: font.mono }}>{fix.code}</Text>
        </View>
      ) : null}
    </View>
  );
}

/** Before the answer: the press calling the lines correct, beside the hint to tap instead. */
export function FlawCall({ on, onClean }: { on: boolean; onClean: () => void }) {
  const theme = useTheme();
  return (
    <View style={{ gap: space[1] }}>
      <Press mode={on ? 'contained' : 'outlined'} onPress={onClean} accessibilityState={{ selected: on }}>
        {FLAW_CLEAN}
      </Press>
      <Text style={{ color: theme.colors.onSurfaceVariant }}>{FLAW_TAP}</Text>
    </View>
  );
}
