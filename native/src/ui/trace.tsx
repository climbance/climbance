import { Pressable, View } from 'react-native';
import { Text, useTheme } from 'react-native-paper';

import { TRACE_TAP, traceCorrectedShown, traceRows, type Question, type TraceRow } from '@climb/core';
import { font, radius, space } from '@/ui/tokens';

/**
 * A read-the-trace drill's steps, each a tap target until answered, then the
 * first wrong step marked and the corrected run. `content-repo/ai-drills.md`
 */
export function TraceStated({
  q,
  tapped,
  answered,
  onTap,
}: {
  q: Question;
  tapped: number | null;
  answered: boolean;
  onTap?: (step: number) => void;
}) {
  const theme = useTheme();
  if (!q.trace) return null;
  const muted = { color: theme.colors.onSurfaceVariant };
  const corrected = answered ? traceCorrectedShown(q) : null;
  return (
    <View style={{ gap: space[2] }}>
      <Steps rows={traceRows(q, tapped, answered)} onTap={onTap} />
      {!answered ? <Text style={muted}>{TRACE_TAP}</Text> : null}
      {corrected ? (
        <View style={{ gap: space[1] }}>
          <Text style={muted}>{corrected.label}</Text>
          <Steps rows={corrected.rows} />
        </View>
      ) : null}
    </View>
  );
}

function Steps({ rows, onTap }: { rows: TraceRow[]; onTap?: (step: number) => void }) {
  const theme = useTheme();
  const muted = { color: theme.colors.onSurfaceVariant };
  return (
    <View style={{ borderRadius: radius(theme).xl, overflow: 'hidden', backgroundColor: theme.colors.surfaceVariant }}>
      {rows.map((row) => (
        <Pressable
          key={row.n}
          disabled={!onTap}
          onPress={() => onTap?.(row.n)}
          accessibilityRole="button"
          accessibilityLabel={`step ${row.n}: ${row.call ?? row.say}`}
          style={{
            flexDirection: 'row',
            gap: space[2],
            paddingVertical: 5,
            paddingHorizontal: space[2],
            backgroundColor: row.tapped ? theme.colors.secondaryContainer : undefined,
            borderLeftWidth: row.wrong ? 4 : 0,
            borderLeftColor: theme.colors.error,
          }}
        >
          <Text style={[{ fontFamily: font.mono, width: 22, textAlign: 'right' }, muted]}>{row.n}</Text>
          {row.call !== null ? (
            <View style={{ flex: 1 }}>
              <Text style={{ fontFamily: font.mono }}>{row.call}</Text>
              <Text style={[{ fontFamily: font.mono }, muted]}>→ {row.result}</Text>
            </View>
          ) : (
            <Text style={{ flex: 1 }}>{row.say}</Text>
          )}
        </Pressable>
      ))}
    </View>
  );
}
