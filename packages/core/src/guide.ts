// the guide, one text both clients render: the web at `/start`, the phone's
// Guide screen. `pages.md`, Sections
const GUIDE = `# How practice works

Climbance trains algorithmic problem solving in a few kinds of practice. Each
one trains a different part of the skill.

## The kinds of practice

**A sitting** is one problem, solved in the editor and run against the
problem's own cases. It trains writing a correct solution once you know the
technique. The clock is yours to start, pause or leave off.

**A recall** asks you to write one form of a technique from memory, and runs
it against a few cases. It trains holding the form, so you can reach for it in
a sitting. A hint is there when you are stuck, and a pass after a hint counts
as a miss.

**Judging a solution** shows a short solution, clean or carrying one flaw, and
asks which. Where it is flawed, you mark the line. It trains reading code for
the mistake a test would catch.

**Filling a key line** blanks one line of a form and offers a few choices for
it. It trains knowing which line makes the form work.

**A question** asks one fact about a subject, such as Python or system design.
The knowledge modules hold the questions, each with short lessons, and the
schedule brings each question back before you would forget it.

## Where to start

**For the algorithms**, open the board's pick. On a new account it names a
card with no requirements. Read the card, then solve the problems on its
ladder. The board brings each form back as a recall once it is due.

**For the knowledge**, press Continue on the board. The queue offers each
lesson before its new questions, and may ask two of a lesson's questions
before you read it.

The schedule then names the next step on the board each day.
`;

export interface Guide {
  title: string;
  body: string;
}

export function guide(text: string = GUIDE): Guide {
  return {
    title: /^#\s+(.+)$/m.exec(text)?.[1] ?? 'How practice works',
    body: text.replace(/^#\s+.+$/m, '').trimStart(),
  };
}

export const GUIDE_LINK = 'How practice works';
export const GUIDE_PANEL_TITLE = 'New here?';
export const GUIDE_PANEL_NOTE = 'Read what each kind of practice trains, and where to start.';

/**
 * The board's panel linking the guide: while neither the engine's log nor the
 * device's copy holds an act. Either one unread shows none, so the panel never
 * flashes for a user who has acted.
 */
export function showsGuidePanel(
  board: { acted: boolean } | null | undefined,
  device: { ready: boolean; acted: boolean },
): boolean {
  return board != null && device.ready && !board.acted && !device.acted;
}
