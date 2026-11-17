import { usePathname } from 'expo-router';
import { useState } from 'react';
import { View } from 'react-native';
import { Button, Text, TextInput, useTheme } from 'react-native-paper';

import {
  CANCEL,
  FEEDBACK_EXPLAINED,
  FEEDBACK_LABEL,
  FEEDBACK_SEND,
  FEEDBACK_SENT,
  FEEDBACK_TITLE,
  SEND_FEEDBACK,
  sendableNote,
  sendFeedback,
} from '@climb/core';
import { engine } from '@/lib/engine';
import { getToken } from '@/lib/settings';
import { useStore } from '@/lib/store';
import { ErrorLine } from '@/ui/common';
import { Sheet } from '@/ui/sheet';
import { space } from '@/ui/tokens';

/** A note the author reads with `climb feedback`, as the web's dialog sends it. */
export function SendFeedback() {
  const st = useStore();
  const theme = useTheme();
  const page = usePathname();
  const [open, setOpen] = useState(false);
  const [note, setNote] = useState('');
  const [sending, setSending] = useState(false);
  const [refused, setRefused] = useState<string | null>(null);
  const [sent, setSent] = useState(false);

  const send = async () => {
    setSending(true);
    const outcome = await sendFeedback(engine(st.settings.origin, await getToken()), 'native', page, note).catch(
      (reason: unknown) => ({ ok: false as const, refused: String(reason) }),
    );
    setSending(false);
    if (!outcome.ok) return setRefused(outcome.refused);
    setOpen(false);
    setNote('');
    setSent(true);
  };

  return (
    <>
      <View style={{ flexDirection: 'row', alignItems: 'center', gap: space.stack }}>
        <Button
          mode="outlined"
          icon="message-outline"
          onPress={() => {
            setRefused(null);
            setSent(false);
            setOpen(true);
          }}
        >
          {SEND_FEEDBACK}
        </Button>
        {sent ? (
          <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
            {FEEDBACK_SENT}
          </Text>
        ) : null}
      </View>
      <Sheet
        visible={open}
        onDismiss={() => setOpen(false)}
        title={FEEDBACK_TITLE}
        note={FEEDBACK_EXPLAINED}
        actions={
          <>
            <Button onPress={() => setOpen(false)}>{CANCEL}</Button>
            <Button mode="contained" disabled={!sendableNote(note) || sending} onPress={() => void send()}>
              {FEEDBACK_SEND}
            </Button>
          </>
        }
      >
        <TextInput
          mode="outlined"
          label={FEEDBACK_LABEL}
          value={note}
          onChangeText={setNote}
          multiline
          numberOfLines={5}
        />
        {refused ? <ErrorLine>{refused}</ErrorLine> : null}
      </Sheet>
    </>
  );
}
