import { useState } from 'react';
import { Button, RadioButton, Text, TextInput, useTheme } from 'react-native-paper';

import {
  CANCEL,
  REPORT_EXPLAINED,
  REPORT_NOTE_LABEL,
  REPORT_PROBLEM,
  REPORT_REASONS,
  REPORT_SEND,
  REPORT_SENT,
  REPORT_TITLE,
  requestRetirement,
  sendableNote,
  type RetirementReason,
} from '@climb/core';
import { engine } from '@/lib/engine';
import { getToken } from '@/lib/settings';
import { useStore } from '@/lib/store';
import { ErrorLine } from '@/ui/common';
import { Sheet } from '@/ui/sheet';

/** A request the author reads before retiring the problem by hand, as the web's dialog sends it. */
export function ReportProblem({ problemId }: { problemId: string }) {
  const st = useStore();
  const theme = useTheme();
  const [open, setOpen] = useState(false);
  const [reason, setReason] = useState<RetirementReason>('defective');
  const [note, setNote] = useState('');
  const [sending, setSending] = useState(false);
  const [refused, setRefused] = useState<string | null>(null);
  const [sent, setSent] = useState(false);

  const send = async () => {
    setSending(true);
    const outcome = await requestRetirement(engine(st.settings.origin, await getToken()), problemId, reason, note);
    setSending(false);
    if (!outcome.ok) return setRefused(outcome.refused);
    setOpen(false);
    setSent(true);
  };

  if (sent)
    return (
      <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
        {REPORT_SENT}
      </Text>
    );
  return (
    <>
      <Button
        mode="text"
        icon="flag-outline"
        compact
        style={{ alignSelf: 'flex-start' }}
        textColor={theme.colors.onSurfaceVariant}
        onPress={() => {
          setRefused(null);
          setOpen(true);
        }}
      >
        {REPORT_PROBLEM}
      </Button>
      <Sheet
        visible={open}
        onDismiss={() => setOpen(false)}
        title={REPORT_TITLE}
        note={REPORT_EXPLAINED}
        actions={
          <>
            <Button onPress={() => setOpen(false)}>{CANCEL}</Button>
            <Button mode="contained" disabled={!sendableNote(note) || sending} onPress={() => void send()}>
              {REPORT_SEND}
            </Button>
          </>
        }
      >
        <RadioButton.Group value={reason} onValueChange={(value) => setReason(value as RetirementReason)}>
          {REPORT_REASONS.map((one) => (
            <RadioButton.Item
              key={one.value}
              value={one.value}
              mode="android"
              position="leading"
              label={one.label}
              labelStyle={{ textAlign: 'left' }}
            />
          ))}
        </RadioButton.Group>
        <TextInput
          mode="outlined"
          label={REPORT_NOTE_LABEL}
          value={note}
          onChangeText={setNote}
          multiline
          numberOfLines={4}
        />
        {refused ? <ErrorLine>{refused}</ErrorLine> : null}
      </Sheet>
    </>
  );
}
