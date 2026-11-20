import type { ReactNode } from 'react';
import { ScrollView, View } from 'react-native';
import { useKeyboardState } from 'react-native-keyboard-controller';
import { Modal, Portal, Text, useTheme } from 'react-native-paper';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { space } from '@/ui/tokens';

/**
 * Every overlay on the phone, as a sheet from the bottom edge: a choice, a
 * confirmation, the claim. The web opens the same as a dialog: `web-app/README.md`,
 * The structure. `actions` sit under the scrolled body, the act last.
 */
export function Sheet(props: {
  visible: boolean;
  onDismiss: () => void;
  title: string;
  note?: string;
  children?: ReactNode;
  actions?: ReactNode;
}) {
  const theme = useTheme();
  const insets = useSafeAreaInsets();
  // a field in the sheet would otherwise sit under the keyboard, with the act
  const keyboard = useKeyboardState((state) => (state.isVisible ? state.height : 0));
  return (
    <Portal>
      <Modal
        visible={props.visible}
        onDismiss={props.onDismiss}
        style={{ justifyContent: 'flex-end', margin: space[0] }}
        contentContainerStyle={{
          backgroundColor: theme.colors.surface,
          borderTopLeftRadius: 24,
          borderTopRightRadius: 24,
          maxHeight: '85%',
          // the keyboard's height counts the navigation bar the modal already clears
          marginBottom: Math.max(0, keyboard - insets.bottom),
          paddingBottom: (keyboard ? 0 : insets.bottom) + 8,
        }}
      >
        <ScrollView contentContainerStyle={{ padding: space[5], gap: space[3] }}>
          <Text variant="titleLarge">{props.title}</Text>
          {props.note ? (
            <Text variant="bodyMedium" style={{ color: theme.colors.onSurfaceVariant }}>
              {props.note}
            </Text>
          ) : null}
          {props.children}
        </ScrollView>
        {props.actions ? (
          <View
            style={{ flexDirection: 'row', justifyContent: 'flex-end', gap: space[2], paddingHorizontal: space[5] }}
          >
            {props.actions}
          </View>
        ) : null}
      </Modal>
    </Portal>
  );
}
