# A cold sitting

The page at `/cold/:sitting_id`, under Practice, and the phone's Cold screen.
The page holds one cold sitting, from serving to its end.
`../../../../api/rating.md` gives the rules this page follows, and the reason
for each.

[`running.md`](running.md) and [`ended.md`](ended.md) draw the page's screens
at low fidelity.

- **`packages/core` computes what both clients' cold screens say**: the time
  left, the verdict line and the outcome. The web and the phone then read one
  cold sitting the same way.

## The way in

- **The board offers a cold sitting in a panel of its own**, below the short
  exercises, on both clients. The pick and the cards are practice, and a cold
  sitting measures the user. The panel says so, and says the sitting runs 60
  minutes with no pause, so nobody starts one expecting a drill.
- **The panel's press serves a cold sitting, or returns to the one running.**
  The engine answers a second serve with the running sitting, as
  `../../../../api/rating.md` gives. The press therefore reads the same in
  both cases, and the board makes no call to learn which case holds.
- **The page's path names the sitting, not the problem.** The routes under
  `/api/cold-sittings` read a cold sitting by its id. `/problems/:problem_id`
  draws the problem's record line, which names what a cold sitting withholds.
- **A reload reads the sitting the path names, running or ended.** The phone
  has no path, and its Practice tab's press reopens the running sitting the
  same way.

## The running sitting

- **The page draws the drill loop's sitting with what a cold sitting
  withholds left out.** The bar carries `Cold problem` in the title's place,
  and no record line sits above the statement. The statement and the editor
  keep their columns, so a user's habits from the drill loop still apply.
- **The clock counts down from the limit, and has no press.** A count up
  would make the user subtract to learn the time left. The bar keeps End and
  the way back.
- **End asks to confirm while the sitting is not solved.** An unsolved
  sitting ended counts as not solved, and the rating keeps that game. One
  stray press would otherwise record a loss.
- **The way back returns to the board, and the clock keeps running.** A
  cold sitting does not pause, as `../../../../api/rating.md` gives.
- **A failing submission reads its verdict and the number of the first case
  it failed.** The case strip and the case's arguments are left out. The
  strip would count the cases passed, and a contest shows neither.
- **A solve leaves the sitting running, and the bar says it is solved.** The
  line under the bar says End reveals the problem. A user who solved has no
  reason to wait for the limit.
- **The unsent code is kept as the drill loop keeps it**, under the problem's
  id. A reload during the sitting then keeps what was typed.

## The ended sitting

- **At `0:00` the page reads the sitting again**, and the engine has ended it
  at its limit. The page draws the ended screen from that reading, so the
  client and the engine agree on the end.
- **The ended screen shows everything the running one withheld**: the title
  in the bar, and the record line with the difficulty, its score, the
  techniques and the cards. The engine's reading of an ended cold sitting
  carries them, and the cards are read from the techniques as the problem's
  page reads them.
- **The bar reads the outcome: solved, with the time from serving, or not
  solved.** This outcome is the game the rating reads.
- **The claim and the label are asked once the sitting ends, never at a
  solve.** The claim's candidates name techniques, and a cold sitting
  withholds techniques while it runs.
- **The code is read-only, and the verdict stays as the number of the failed
  case.** The engine answers a cold submission with no case's arguments,
  running or ended.
- **The phone shows the ended sitting's code as text, in the Code tab.** The
  phone's editor has no read-only mode, and the drill loop never needed one.
- **The ended page's way back names the board.** A press opening the problem
  in the drill loop is deferred until a user asks to retry a cold problem
  there.
