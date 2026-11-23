import { router } from 'expo-router';
import { useEffect, useMemo, useState } from 'react';
import { ScrollView, View } from 'react-native';
import { Button, Text, TouchableRipple, useTheme } from 'react-native-paper';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import {
  showsGuidePanel,
  GUIDE_LINK,
  GUIDE_PANEL_NOTE,
  GUIDE_PANEL_TITLE,
  boardView,
  inProgress,
  techniqueKnowledge,
  techniqueStats,
  type Board as Learner,
  type components,
  BOARD_TITLE,
  OF,
  BOARD_NONE,
  BOARD_STUDYING,
  BOARD_NEXT,
  FILL_NOTE,
  FILL_TITLE,
  JUDGE_NOTE,
  JUDGE_TITLE,
  boardMoreCards,
  nextCards,
  BOARD_UNTOUCHED,
  BOARD_PRACTISED,
  BOARD_NOTE,
  MODULES_HEADING,
  focusLabel,
  orderedModuleRows,
  pickView,
  takePick,
  type PickTarget,
  COLD_PANEL_NOTE,
  COLD_START,
  projectedLine,
  ratingLine,
  COLD_TITLE,
  serveCold,
  sittingRefused,
} from '@climb/core';
import { useStore } from '@/lib/store';
import { engine } from '@/lib/engine';
import { getToken } from '@/lib/settings';
import { useEngine } from '@/lib/useEngine';
import { AccountMenu } from '@/ui/account';
import { CardPanel } from '@/ui/cards';
import { ErrorLine, Loaded, styles, ScreenHeader } from '@/ui/common';
import { ContinueInPanel, ContinueNotice, useContinue } from '@/ui/continue';
import { FocusCard } from '@/ui/focuscard';
import { ModuleRow } from '@/ui/modules';
import { Heading, Panel, PickPanel, PickRow } from '@/ui/rows';
import { usePullSync } from '@/ui/pull';
import { radius } from '@/ui/tokens';

type Board = components['schemas']['Board'];
type ListedCard = components['schemas']['ListedCard'];

const open = (technique: string) => router.push({ pathname: '/technique', params: { technique } });

/** The board, as the web's: the cards in progress, then the techniques by staleness. */
export default function PracticeScreen() {
  const theme = useTheme();
  const insets = useSafeAreaInsets();
  const st = useStore();
  const next = useContinue();
  // the knowledge modules, from the device's copy: the board is the overview
  // of every study, `web-app/pages/practice/board/`
  const { board: learner, courseOrder, now } = st;
  const all = useMemo(() => learner(null), [learner]);
  const modules = useMemo(() => (all ? orderedModuleRows(all, courseOrder, now) : []), [all, now, courseOrder]);
  useEffect(() => {
    // the app opens on Login until it holds a token, and returns there on sign-out
    if (st.ready && !st.hasToken) router.replace('/login');
  }, [st.ready, st.hasToken]);

  const board = useEngine('/api/board');
  const cards = useEngine('/api/cards');
  // the pick only adds to the board, so a failed one reads as none, as on the web
  const pick = useEngine('/api/pick');
  const pull = usePullSync(board.reload, cards.reload, pick.reload);
  // the cards in progress only add to the board, so a failed list reads as none, as on the web
  const error = board.error;
  const cardsIn = cards.data !== null || cards.error !== null;

  return (
    <View style={{ flex: 1, backgroundColor: theme.colors.background }}>
      <ScreenHeader title={BOARD_TITLE} back={null} aside={<AccountMenu />} />
      <ScrollView refreshControl={pull} contentContainerStyle={[styles.page, { paddingBottom: insets.bottom + 32 }]}>
        <Text variant="bodyMedium" style={{ color: theme.colors.onSurfaceVariant }}>
          {BOARD_NOTE}
        </Text>
        {showsGuidePanel(board.data, st) ? (
          <>
            <Heading title={GUIDE_PANEL_TITLE} />
            <PickPanel>
              <PickRow title={GUIDE_LINK} note={GUIDE_PANEL_NOTE} stats={[]} onPress={() => router.push('/guide')} />
            </PickPanel>
          </>
        ) : null}
        {/* the knowledge study first, from the device's copy, so it reads
            before and without the engine's answer: `web-app/pages/practice/board/` */}
        {next.focus && next.cont ? (
          <TouchableRipple
            onPress={() => router.navigate('/knowledge')}
            accessibilityRole="link"
            borderless
            style={{ borderRadius: radius(theme).xl }}
          >
            <FocusCard
              label={focusLabel(next.focus, st.catalog)}
              focus={next.focus}
              b={next.cont.b}
              queue={next.cont.queue}
              exams={st.catalog?.certExams ?? []}
              footer={<ContinueInPanel next={next} inFocus />}
            />
          </TouchableRipple>
        ) : modules.length > 0 ? (
          <Panel padded>
            <ContinueInPanel next={next} />
          </Panel>
        ) : null}
        {modules.length > 0 ? (
          <>
            <Heading title={MODULES_HEADING} count={modules.length} />
            <PickPanel>
              {modules.map((row) => (
                <ModuleRow key={row.c.slug} row={row} />
              ))}
            </PickPanel>
          </>
        ) : null}

        <Loaded
          of={OF.board}
          state={{
            data: board.data && cardsIn ? { board: board.data, cards: cards.data ?? [] } : null,
            error,
            reload: () => {
              board.reload();
              cards.reload();
            },
          }}
          blank={BOARD_NONE}
          blankWhen={(x) => x.board.rows.length === 0}
        >
          {(x) => <BoardBody board={x.board} cards={x.cards} learner={all} pick={pick.data ?? null} />}
        </Loaded>
      </ScrollView>
      <ContinueNotice next={next} />
    </View>
  );
}

// a route per target, as the cards list and the card's screen open the same acts
function openPick(target: PickTarget) {
  if (target.kind === 'recall')
    router.push({ pathname: '/recall', params: { slug: target.card, template: target.template } });
  else if (target.kind === 'problem')
    router.push({
      pathname: '/problem',
      params: { problem: target.problem, technique: target.technique, card: target.card },
    });
  else router.push({ pathname: '/card', params: { slug: target.card } });
}

function BoardBody({
  board,
  cards,
  learner,
  pick,
}: {
  board: Board;
  cards: ListedCard[];
  learner: Learner | null;
  pick: components['schemas']['BoardPick'] | null;
}) {
  const theme = useTheme();
  const [now] = useState(() => Date.now());
  // the knowledge reading, from the device's copy: `api/mastery.md`
  const known = (row: Board['rows'][number]) => (learner ? techniqueKnowledge(learner, row) : null);
  const { untouched, practised, foot } = boardView(board, known);
  // each list closes from its own heading, as the web's board does: `web-app/pages/practice/board/`
  const [closed, setClosed] = useState<ReadonlySet<string>>(new Set());
  const toggle = (id: string) =>
    setClosed((was) => {
      const next = new Set(was);
      if (!next.delete(id)) next.add(id);
      return next;
    });
  const studying = inProgress(cards);
  const next = nextCards(cards, pick?.card_slug ?? null);
  const view = pick ? pickView(pick) : null;
  const { origin } = useStore().settings;
  return (
    <>
      {/* the schedule's one act, above every list: `api/pick.md` */}
      {view ? (
        <>
          <Heading title={view.heading} />
          <PickPanel>
            <PickRow
              title={view.title}
              note={view.note}
              stats={[]}
              onPress={() => {
                // the prediction is stored as the act opens: `api/predictions.md`
                if (pick) void getToken().then((token) => takePick(engine(origin, token), pick));
                openPick(view.target);
              }}
            />
          </PickPanel>
        </>
      ) : null}
      {studying.length > 0 ? (
        <>
          <Heading title={BOARD_STUDYING} count={studying.length} />
          <CardPanel technique={null} cards={studying} />
        </>
      ) : null}
      {/* the short exercises, across every card: `web-app/pages/cards/judging/` and `web-app/pages/cards/key-line/` */}
      <Panel>
        <PickRow title={JUDGE_TITLE} note={JUDGE_NOTE} stats={[]} onPress={() => router.push('/judge')} />
        <PickRow title={FILL_TITLE} note={FILL_NOTE} stats={[]} onPress={() => router.push('/fill')} />
      </Panel>
      <ColdPanel />
      {next.cards.length > 0 ? (
        <>
          <Heading title={BOARD_NEXT} count={next.cards.length + next.more} />
          <CardPanel technique={null} cards={next.cards} />
          {next.more > 0 ? (
            <Text
              variant="bodySmall"
              accessibilityRole="link"
              onPress={() => router.navigate('/cards')}
              style={{ color: theme.colors.onSurfaceVariant }}
            >
              {boardMoreCards(next.more)}
            </Text>
          ) : null}
        </>
      ) : null}
      {untouched.length > 0 ? (
        <>
          <Heading
            title={BOARD_UNTOUCHED}
            count={untouched.length}
            closed={closed.has('untouched')}
            onToggle={() => toggle('untouched')}
          />
          {closed.has('untouched') ? null : (
            <Panel padded style={{ flexDirection: 'row', flexWrap: 'wrap', columnGap: 20, rowGap: 8 }}>
              {untouched.map((row) => (
                <Text
                  key={row.technique}
                  variant="bodyLarge"
                  accessibilityRole="link"
                  onPress={() => open(row.technique)}
                  style={{ color: theme.colors.primary }}
                >
                  {row.technique}
                </Text>
              ))}
            </Panel>
          )}
        </>
      ) : null}
      {practised.length > 0 ? (
        <>
          <Heading
            title={BOARD_PRACTISED}
            count={practised.length}
            closed={closed.has('practised')}
            onToggle={() => toggle('practised')}
          />
          {closed.has('practised') ? null : (
            <PickPanel>
              {practised.map((row) => (
                <PickRow
                  key={row.technique}
                  title={row.technique}
                  stats={techniqueStats(row, now, known(row))}
                  onPress={() => open(row.technique)}
                />
              ))}
            </PickPanel>
          )}
        </>
      ) : null}
      {foot ? (
        <Text variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
          {foot}
        </Text>
      ) : null}
    </>
  );
}

// one press, serving a cold sitting or returning to the one running: the
// engine answers a second serve with it, `web-app/pages/practice/cold/`
function ColdPanel() {
  const { origin, device } = useStore().settings;
  const [serving, setServing] = useState(false);
  const [refused, setRefused] = useState<string | null>(null);
  // a refused read leaves the line out and the press working
  const rating = ratingLine(useEngine('/api/rating').data);
  const projected = projectedLine(useEngine('/api/projection').data);
  const theme = useTheme();

  async function start() {
    setServing(true);
    setRefused(null);
    const served = await serveCold(engine(origin, await getToken()), device, () => performance.now());
    setServing(false);
    if (served.ok) router.push({ pathname: '/cold', params: { sitting: served.value.seated.sitting.id } });
    else setRefused(served.refused);
  }

  return (
    <>
      <PickPanel>
        <PickRow
          title={COLD_TITLE}
          note={COLD_PANEL_NOTE}
          stats={[]}
          aside={
            <Button mode="contained" compact disabled={serving} onPress={() => void start()}>
              {COLD_START}
            </Button>
          }
        >
          {[rating, projected].map((line) =>
            line ? (
              <Text key={line} variant="bodySmall" style={{ color: theme.colors.onSurfaceVariant }}>
                {line}
              </Text>
            ) : null,
          )}
        </PickRow>
      </PickPanel>
      {refused ? <ErrorLine>{sittingRefused(refused)}</ErrorLine> : null}
    </>
  );
}
