# The design system

The tokens and the shared shapes every page of both clients reads: colour,
type, code, tables and diagrams. `areas.md` gives the parts of a page, and the
gallery, `pages/gallery/README.md`, shows every token and component.

## Tokens and shapes

- **Consistency across pages outranks fitting one page better.** A shape that
  reads one way on one page and another way on the next teaches the reader two
  rules for one thing. A page that wants an exception gets a different layout
  of the shared shapes instead, and a shape changes everywhere or nowhere.
- **The tokens are the only place a colour, a radius, a spacing step, a type
  size or a font family is defined**: `web/src/index.css` on the web and
  `native/src/ui/tokens.ts` on the phone, named by the same roles. Every
  component reads a token. A value set inside one component alone is a design
  no other component follows.
- **The app takes the site's palette and shapes**, so the product reads as one
  thing from the landing page to a sitting. The neutrals, the type, the code
  colours and the verdict colours were already shared. The flame and the
  rounder shapes come from the site.
- **Each colour token carries both schemes in one declaration**, and the root
  says which of the two is read. A token declared twice would be a value in
  two places, and the two drift.
- **Every radius is derived from one base**, so a single edit rounds or squares
  the whole app. The base follows the site's rounder panels.
- **A press is a pill**, as on the site. The pill is set once in
  `web/src/index.css`, so the copied button component stays as it ships.

## Colour

- **The flame marks the brand, the focus and progress, and nothing else.** The
  wordmark carries a flame dot, the focus ring is its deep shade, and a
  ladder's progress is a thin flame bar. Progress is the study's own rather
  than a verdict, so it reads in the brand. The press a page
  asks for is an ink pill, as the site's navigation press is: a flame press on
  every working page read louder than the page around it. No verdict reads in
  the flame either: its hue sits between wrong and timed out.
- **The knowledge focus reads in the flame**, on the subtopic or the
  module it is aimed at. The focus names the groups the study aims at next,
  so it reads as progress does. A node picked on the map is a selection and
  reads neutral.
- **A state that asks for an act reads neutral.** A certification ready for
  its exam, one that needs a refresh and a lesson ready to read are states
  rather than progress. In the flame each would read as progress made.
- **Each of a verdict's four outcomes carries a token**: passed, wrong, timed
  out and crashed. One `destructive` token cannot separate a wrong answer from a
  timeout, and the drill loop shows that difference on every failing submission.
- **A recall's pass and fail read in the verdict's colours**, since they are the
  same outcomes: a clean recall in passed, a failed one in wrong. A hinted pass
  and a form never recalled stay grey.
- **A running clock carries a green dot.** The press's label alone left a
  running clock and a stopped one looking alike. The dot has a token of its
  own, since a running clock is not a passed case.
- **The phone's colours come from the device's Material palette**, and the
  colours that palette holds no role for live in one file of the phone's
  own. A verdict's four outcomes are among them, each apart, as on the web.
- **The neutrals carry a warm cast, and the light ground is paper rather than
  white.** A solver reads a statement for many minutes, and a warm ground is
  easier to sit in front of than white. The dark ground is a warm charcoal for
  the same reason.
- **The web opens in the browser's colour-scheme and carries a switch.** The
  switch writes the chosen scheme to the browser, and a reader who never
  presses it follows their browser for as long as they never press it. No
  store holds the choice, since the choice is about the machine the reader is
  at rather than about the user.

## Type and code

- **The type scale is named by the role a page reads a size in**: title,
  heading, body, meta, code and micro. Micro is a chart's smallest label, such
  as a ring's share. A page asking for a size by its role cannot choose a size
  no other page uses.
- **Code inside a line of prose takes a step below the code role.** The mono
  family has a larger x-height than the sans beside it, so mono set at the code
  role reads larger than the prose around it. The step is its own token.
- **Code reads in one mono family, named as a token.** The editor, a template's
  form and a failing case's arguments are all code, and a reader who sees three
  mono families reads three kinds of thing.
- **One mapping colours Python wherever it appears.** The editor and a
  template's form read the same mapping from the language's tags to the five
  code tokens, so a form on a card is coloured as the editor colours it. A
  form on a card is rendered from that mapping rather than by mounting an
  editor, which takes no input and would ship the editor to show ten lines.
- **A long line of code wraps, and continues under its own indent.** This
  holds for a question's code, a detail's example, a template's form and a
  fenced block whose fence names a language or `output`, on both clients. A
  phone fits some forty characters, and a block scrolled sideways hides the
  end of a line, which is often the part a question asks about. The indent
  keeps the structure readable across the wrap, as the editor does.
- **A wrapped part opens on a dim `↪`, which no copy carries.** Without the
  mark a reader cannot tell a wrap from a new line, and in a question about
  what code prints the difference is the answer. Python has no symbol for a
  wrap the screen adds, and the backslash would read as Python's own line
  joining.
- **`packages/core` cuts the rows, at a column count each client measures.**
  The phone and the web then break a line at the same place. A line breaks
  where VS Code breaks one: at a space, after a comma, a dot or a closing
  bracket, or before an opening bracket. A word is cut only where none of
  those sits near the edge.
- **A copy returns the lines as written.** A wrap is drawn and never copied,
  as in every editor's soft wrap. Code copied with a break at each wrap would
  not run as it was written.

## Diagrams and tables

- **A diagram keeps its lines whole and scrolls sideways.** A detail's diagram
  and a fence naming `text` or no language may be drawn in characters, and
  wrapping would break the drawing. A program's output is fenced `output`
  instead, so its long lines wrap as code does.
- **A Mermaid diagram reads as the drawing the seed made, in the page's
  scheme**, scaled to the reading width and never wider than drawn.
  `../content-repo/modules.md` `## Diagrams` gives how it is drawn. A source
  with no drawing reads as its text, which a diagram drawn on the device would
  replace only after a second or more.
- **A detail's diagram that is one markdown table alone reads as a table**,
  as a table in a lesson does. A table drawn in characters scrolls sideways on
  a phone, and the reader sees a third of its columns at a time.
- **A markdown table reads as a grid where its columns fit the reading
  width, and as one block per row where they do not, on both clients.** A
  phone is too narrow for most tables of three columns. A grid squeezed to fit
  wraps each cell to a few words a line, and a grid scrolled sideways hides
  its last columns.
- **A table read as blocks opens each row on its first cell, and gives every
  other cell under its header.** A table's first column usually names the
  row, so the name stays beside its values.
- **`packages/core` decides a table's shape**, from the length of each cell's
  text and a column count each client measures in characters of prose. A
  table then reads the same on the phone and in a narrow window on the web.

## Authored prose

- **Authored prose reads on these tokens too.** The markdown renderer ships a
  scale and a palette of its own, and each of its variables is bound to a
  token. A document's own title reads at the title role, and its headings at
  the heading role.
- **A link in authored prose that leaves the app carries a `↗` after its
  text, on both clients.** A lesson's links to the Python docs read like its
  links to other lessons, and a reader pressing one leaves the lesson
  unwarned. The web opens such a link in a new tab, and the phone in the
  browser.
