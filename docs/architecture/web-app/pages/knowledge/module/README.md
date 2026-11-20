# A module

The page at `/knowledge/modules/:module` and the phone's Module screen: a
module's groups and its map, the start sheet, the focus and the module's
status. `../../../README.md` `## The structure` gives what the page holds.

- **A module's page reads each topic as a panel of subtopics by level.** Each
  group reads as covered, open, locked or holding no questions.
- **The module's page is one screen on both clients.** The two clients read
  the same numbers from `packages/core`, so the difference is the layout
  alone.
- **The module's page aims the focus and sets the module's status.** The focus
  is aimed at the module, a topic or a subtopic, by a press of its own. A
  subtopic's row carries a Focus press, since its name opens the sheet.
  Starting a queue from the sheet moves no focus, so one drill does not
  retarget Continue. The status is active, paused or archived. A status
  press asks before it archives, since an archived module leaves the home.

## The start sheet

- **The start sheet opens on four scopes, on both clients**: a group's cell,
  a subtopic's name, Start beside a topic, and Start beside the module. The
  press names the scope, and a group also names its level. The sheet adds
  the kind and the due flag, and Start counts what the choices leave.
- **Each scope is the natural drill at its depth.** The sheet narrows a scope
  and never widens one, so a scope no press opens is a drill nobody can
  start.
- **The start sheet replaces a screen of choices.** A screen of its own drew
  the module's groups a second time, beside the module's page that draws them
  already.
- **The press that opens the sheet reads Start.** Practice names the board's
  section on the web, and one word naming two places would send a reader to
  the wrong one.
