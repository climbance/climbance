import { router, useLocalSearchParams } from 'expo-router';
import { useCallback, useEffect, useRef, useState } from 'react';
import { ScrollView, View } from 'react-native';
import { Button, IconButton, SegmentedButtons, Text, TouchableRipple, useTheme } from 'react-native-paper';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import {
  BACK_BOARD,
  COLD_END_TITLE,
  COLD_KEEP,
  COLD_SOLVED_LINE,
  COLD_TITLE,
  type ColdRead,
  type Draft,
  cardsOffered,
  coldEndNote,
  coldOutcome,
  coldVerdict,
  endCold,
  keyboardToggle,
  OF,
  problemCards,
  readCold,
  revealedFacts,
  secondsLeft,
  SITTING_CODE,
  SITTING_END,
  SITTING_STATEMENT,
  sittingRefused,
  submitCold,
  submitLabel,
  timeLeft,
  TOUCH_MS,
} from '@climb/core';
import { engine } from '@/lib/engine';
import type { Key } from '@/lib/keys';
import { getToken } from '@/lib/settings';
import { draftOf, keepDraft } from '@/lib/sitting';
import { useStore } from '@/lib/store';
import { useEngine } from '@/lib/useEngine';
import { ClaimSheet } from '@/ui/claim';
import { ErrorLine, Loaded, ScreenHeader, styles } from '@/ui/common';
import { CodeEditor, type EditorHandle } from '@/ui/editor';
import { KeyPad } from '@/ui/keys';
import { Markdown } from '@/ui/markdown';
import { ReportProblem } from '@/ui/report';
import { Badge } from '@/ui/rows';
import { Sheet } from '@/ui/sheet';
import { font, space, textSize } from '@/ui/tokens';

const now = () => performance.now();

// a cold sitting, running or ended: the Problem screen with what a cold
// sitting withholds left out, `web-app/pages/practice/cold/`
export default function ColdScreen() {
  const theme = useTheme();
  const insets = useSafeAreaInsets();
  const { sitting: sittingId = '' } = useLocalSearchParams<{ sitting: string }>();
  const { origin } = useStore().settings;
  const [read, setRead] = useState<ColdRead | null>(null);
  const [failed, setFailed] = useState<string | null>(null);
  const [kept, setKept] = useState<Draft | null | undefined>(undefined);
  const [running, setRunning] = useState(false);
  const [refused, setRefused] = useState<string | null>(null);
  const [answered, setAnswered] = useState(false);
  const [ending, setEnding] = useState(false);
  const [tab, setTab] = useState<'statement' | 'code'>('statement');
  const [keys, setKeys] = useState(true);
  const [names, setNames] = useState<string[]>([]);
  const editor = useRef<EditorHandle>(null);
  const onKey = useCallback((key: Key) => editor.current?.press(key), []);
  const code = useRef<string | null>(null);

  const reread = useCallback(async () => {
    const again = await readCold(engine(origin, await getToken()), sittingId, now);
    if (again.ok) {
      setRead(again.value);
      setFailed(null);
    } else setFailed(again.refused);
  }, [origin, sittingId]);

  useEffect(() => {
    void reread();
  }, [reread]);

  const problemId = read?.seated.sitting.problem_id ?? null;
  useEffect(() => {
    if (problemId !== null) void draftOf(problemId).then(setKept);
  }, [problemId]);

  const ended = read?.seated.sitting.ended_at != null;

  // a read touches the sitting, so the idle bound does not end it while the
  // user thinks; the cold clock runs with the app in the background too
  useEffect(() => {
    if (read === null || ended) return;
    const tick = setInterval(() => void reread(), TOUCH_MS);
    return () => clearInterval(tick);
  }, [read === null, ended, reread]);

  // at 0:00 the engine has ended the sitting at its limit, and the screen
  // reads that end rather than deciding one of its own
  useEffect(() => {
    if (read === null || ended) return;
    const left = secondsLeft(read.seated.sitting, read.seated.elapsed_sec ?? null, read.at, now());
    const limit = setTimeout(() => void reread(), (left + 1) * 1000);
    return () => clearTimeout(limit);
  }, [read, ended, reread]);

  // the cards name techniques, so they are read once the sitting ends
  const listed = useEngine(ended ? '/api/cards' : null);

  if (read === null || kept === undefined)
    return (
      <View style={{ flex: 1, backgroundColor: theme.colors.background }}>
        <ScreenHeader title={COLD_TITLE} />
        <View style={styles.page}>
          <Loaded of={OF.problem} state={{ data: null, error: failed, reload: () => void reread() }}>
            {() => null}
          </Loaded>
        </View>
      </View>
    );

  const { seated } = read;
  const last = seated.last ?? null;
  const solved = last?.attempt.solved === true;
  const opening =
    kept !== null && kept.sitting === sittingId
      ? kept.code
      : (last?.attempt.code ?? (seated.signature ? `${seated.signature}\n    ` : ''));
  const revealed = seated.revealed ?? null;
  const facts = revealed && revealedFacts(revealed);
  const offered = revealed ? problemCards(listed.data ?? [], revealed.techniques, null) : [];
  const muted = { color: theme.colors.onSurfaceVariant };

  async function submit() {
    if (running || ended) return;
    setRunning(true);
    setRefused(null);
    const sent = await submitCold(engine(origin, await getToken()), sittingId, code.current ?? opening, now);
    // the reading carries the verdict as `last`, and the engine's clock
    if (sent.ok) await reread();
    else setRefused(sent.refused);
    setRunning(false);
  }

  async function end() {
    setRefused(null);
    const out = await endCold(engine(origin, await getToken()), sittingId, now);
    if (out.ok) await reread();
    else setRefused(out.refused);
  }

  const toggleKeys = () => {
    setKeys(!keys);
    setTimeout(() => editor.current?.measure(), 100);
  };

  return (
    <View style={{ flex: 1, backgroundColor: theme.colors.background, paddingBottom: insets.bottom + 8 }}>
      <ScreenHeader title={revealed?.title ?? COLD_TITLE} />
      <View style={[styles.row, { paddingHorizontal: space[3], paddingVertical: space[1], gap: space[2] }]}>
        {ended ? (
          <Text variant="titleSmall">{coldOutcome(last)}</Text>
        ) : (
          <ColdClock read={read} />
        )}
        <View style={{ flex: 1 }} />
        {ended ? (
          <Button mode="contained" compact onPress={() => router.back()}>
            {BACK_BOARD}
          </Button>
        ) : (
          <Button mode="outlined" compact onPress={() => setEnding(true)}>
            {SITTING_END}
          </Button>
        )}
      </View>
      {refused ? (
        <View style={{ paddingHorizontal: space[3] }}>
          <ErrorLine>{sittingRefused(refused)}</ErrorLine>
        </View>
      ) : null}
      {solved && !ended ? (
        <Text variant="bodySmall" style={[muted, { paddingHorizontal: space[3] }]}>
          {COLD_SOLVED_LINE}
        </Text>
      ) : null}
      <SegmentedButtons
        value={tab}
        onValueChange={(value) => setTab(value as 'statement' | 'code')}
        style={{ marginHorizontal: space[3], marginVertical: space[1.5] }}
        buttons={[
          { value: 'statement', label: SITTING_STATEMENT, icon: 'text-box-outline' },
          { value: 'code', label: SITTING_CODE, icon: 'code-tags' },
        ]}
      />
      <ScrollView
        style={{ display: tab === 'statement' ? 'flex' : 'none' }}
        contentContainerStyle={[styles.page, { paddingTop: space[1] }]}
      >
        {facts ? (
          <>
            <View style={[styles.row, { flexWrap: 'wrap' }]}>
              <Badge label={facts.difficulty} />
              <Text variant="bodySmall" style={muted}>
                {facts.techniques}
              </Text>
            </View>
            {offered.length > 0 ? (
              <View style={[styles.row, { flexWrap: 'wrap' }]}>
                <Text variant="bodySmall" style={muted}>
                  {cardsOffered(offered.length)}
                </Text>
                {offered.map((one) => (
                  <TouchableRipple
                    key={one.slug}
                    accessibilityRole="link"
                    onPress={() => router.push({ pathname: '/card', params: { slug: one.slug } })}
                  >
                    <Text variant="bodySmall" style={{ color: theme.colors.primary }}>
                      {one.title}
                    </Text>
                  </TouchableRipple>
                ))}
              </View>
            ) : null}
          </>
        ) : null}
        <Markdown>{seated.statement}</Markdown>
        {/* the retirement sheet names the problem, so it waits for the end */}
        {ended ? <ReportProblem problemId={seated.sitting.problem_id} /> : null}
      </ScrollView>
      <View style={{ flex: 1, display: tab === 'code' ? 'flex' : 'none' }}>
        {/* the phone's editor has no read-only mode, so the ended screen
            shows the submitted code as text */}
        {ended ? (
          <ScrollView style={{ flex: 1 }} contentContainerStyle={{ padding: space[3] }}>
            <Text selectable style={{ fontFamily: font.mono, fontSize: textSize.codeInline }}>
              {last?.attempt.code ?? opening}
            </Text>
          </ScrollView>
        ) : (
          <CodeEditor
            ref={editor}
            onNames={setNames}
            initial={opening}
            onChange={(typed) => {
              code.current = typed;
              void keepDraft(seated.sitting.problem_id, sittingId, typed);
            }}
          />
        )}
        {ended ? null : (
          <View style={[styles.row, { paddingHorizontal: space[2], paddingVertical: space[1.5], gap: space[2] }]}>
            <Button mode="contained" onPress={() => void submit()} disabled={running}>
              {submitLabel(running)}
            </Button>
            <IconButton
              icon={keys ? 'keyboard-close' : 'keyboard'}
              accessibilityLabel={keyboardToggle(keys)}
              style={{ marginLeft: 'auto' }}
              onPress={toggleKeys}
            />
          </View>
        )}
        {last ? (
          <Text
            variant="titleSmall"
            style={{ paddingHorizontal: space[3], color: solved ? undefined : theme.colors.error }}
          >
            {coldVerdict(last)}
          </Text>
        ) : null}
        {keys && !ended ? (
          <View style={{ paddingHorizontal: space[2], paddingTop: space[1.5] }}>
            <KeyPad lines names={names} onKey={onKey} />
          </View>
        ) : null}
      </View>
      {/* the claim's candidates name techniques, so it is asked at the end alone */}
      <ClaimSheet
        sittingId={sittingId}
        drilled={null}
        visible={ended && last !== null && !answered}
        onDone={() => setAnswered(true)}
      />
      <Sheet
        visible={ending}
        onDismiss={() => setEnding(false)}
        title={COLD_END_TITLE}
        note={coldEndNote(solved)}
        actions={
          <>
            <Button onPress={() => setEnding(false)}>{COLD_KEEP}</Button>
            <Button
              mode="contained"
              onPress={() => {
                setEnding(false);
                void end();
              }}
            >
              {SITTING_END}
            </Button>
          </>
        }
      />
    </View>
  );
}

// its own component: it renders every second, and the editor beside it must not
function ColdClock({ read }: { read: ColdRead }) {
  const [at, setAt] = useState(() => now());
  useEffect(() => {
    const tick = setInterval(() => setAt(now()), 1000);
    return () => clearInterval(tick);
  }, []);
  const left = secondsLeft(read.seated.sitting, read.seated.elapsed_sec ?? null, read.at, at);
  return (
    <Text variant="titleMedium" style={{ fontFamily: font.mono }}>
      {timeLeft(left)}
    </Text>
  );
}
