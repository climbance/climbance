import { Directory } from 'expo-file-system';
import { router } from 'expo-router';
import { useState } from 'react';
import { View } from 'react-native';
import { Button, Text, TextInput, useTheme } from 'react-native-paper';

import {
  type components,
  confirmsDeletion,
  DELETE_ACCOUNT,
  DELETE_ACCOUNT_TITLE,
  deleteAccount,
  deleteAccountWarning,
  EXPORT_NOTE,
  EXPORT_RECORD,
  exportedRecord,
  KEEP_ACCOUNT,
  named,
  RECORD_FILE,
  recordSaved,
  YOUR_RECORD,
} from '@climb/core';
import { engine } from '@/lib/engine';
import { getToken } from '@/lib/settings';
import { useStore } from '@/lib/store';
import { ErrorLine, styles } from '@/ui/common';
import { Heading } from '@/ui/rows';
import { Sheet } from '@/ui/sheet';

type Me = components['schemas']['Me'];

/** The record exported as a file, and the account deleted with it, as the web's Settings page holds them. */
export function YourRecord({ me }: { me: Me | undefined }) {
  const st = useStore();
  const theme = useTheme();
  const [said, setSaid] = useState<string | null>(null);
  const [failed, setFailed] = useState<string | null>(null);
  const [asking, setAsking] = useState(false);
  const [typed, setTyped] = useState('');
  const [deleting, setDeleting] = useState(false);

  const client = async () => engine(st.settings.origin, await getToken());

  const exported = async () => {
    setSaid(null);
    setFailed(null);
    const record = await exportedRecord(await client());
    if (!record.ok) return setFailed(record.refused);
    let folder: Directory;
    try {
      folder = await Directory.pickDirectoryAsync();
    } catch {
      return; // the picker was dismissed
    }
    try {
      folder.createFile(RECORD_FILE, 'application/json').write(record.value);
      // Android names a picked folder by its volume too: `primary:Documents`
      setSaid(recordSaved(folder.name.split(/[:/]/).pop() ?? folder.name));
    } catch (reason) {
      setFailed(String(reason));
    }
  };

  const deleted = async () => {
    setDeleting(true);
    const gone = await deleteAccount(await client(), typed);
    setDeleting(false);
    setAsking(false);
    if (!gone.ok) return setFailed(gone.refused);
    // forced: the outbox belongs to a log that no longer exists
    await st.signOut(true);
    router.replace('/login');
  };

  return (
    <>
      <Heading title={YOUR_RECORD} />
      <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
        {EXPORT_NOTE}
      </Text>
      <View style={styles.row}>
        <Button mode="outlined" icon="download" onPress={() => void exported()}>
          {EXPORT_RECORD}
        </Button>
        <Button
          mode="outlined"
          icon="delete-outline"
          disabled={!me}
          onPress={() => {
            setTyped('');
            setAsking(true);
          }}
        >
          {DELETE_ACCOUNT}
        </Button>
      </View>
      {said ? <Text variant="bodySmall">{said}</Text> : null}
      {failed ? <ErrorLine>{failed}</ErrorLine> : null}
      <Sheet
        visible={asking}
        onDismiss={() => setAsking(false)}
        title={DELETE_ACCOUNT_TITLE}
        note={deleteAccountWarning(named(me))}
        actions={
          <>
            <Button onPress={() => setAsking(false)}>{KEEP_ACCOUNT}</Button>
            <Button
              mode="contained"
              buttonColor={theme.colors.error}
              textColor={theme.colors.onError}
              disabled={!confirmsDeletion(typed, me) || deleting}
              onPress={() => void deleted()}
            >
              {DELETE_ACCOUNT}
            </Button>
          </>
        }
      >
        <TextInput
          mode="outlined"
          accessibilityLabel={DELETE_ACCOUNT}
          value={typed}
          onChangeText={setTyped}
          autoCapitalize="none"
          autoCorrect={false}
        />
      </Sheet>
    </>
  );
}
