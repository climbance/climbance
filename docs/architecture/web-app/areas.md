# A page's areas

The parts every page of both clients is built from: the header, the body, the
act, the rows and panels, and the sections of a long page.
`design-system.md` gives the tokens each part reads.

## The header, the body and the act

- **A page carries a header and a body.** The header holds the way back, the
  title, and the one line that identifies what the title names, such as the
  technique a card teaches.
- **The header reads in every reading of the page**, loading and failed
  included. A page whose header waits for its record leaves a reader on a
  failed load with no title and no way back.
- **Each part of a page is one shared component per client**: the header,
  the four readings, a row, a section's heading and its panel. Every page
  uses it, the knowledge pages and the engine pages alike. A part copied
  into one page drifts from the rest, and the two families of pages read as
  two apps.
- **A page has four readings: loading, failed, empty and the content.** One
  component renders the first three, so a page that failed reads the same
  whichever request failed.
- **One page asks for one act.** The board asks what to practise next, a card in
  progress or a technique. The candidates ask for a problem, and the sitting
  asks for a submission. The clock's press sits in the bar as a control, not as
  an act the page waits on. A page offering two acts of equal weight makes the
  user choose before the flow asks them to.
- **The act reads as the page's one primary press.** The phone holds it in
  the bar at the bottom of the screen, where the thumb rests, and the web
  holds it in the page. A second way in reads at a lower weight, as the
  knowledge home's Exam does beside Continue.
  The board is the exception, since it holds several studies, and its
  Continue sits in the focus's panel, as `pages/practice/board/README.md`
  gives.

## The width

- **The body reads in one column of at most 56rem.** A line of prose wider than
  that is hard to track back to the next line's start.
- **The sitting is the exception, and reads in two columns.** The statement and
  the editor sit side by side, and a reading column is too narrow to hold both.
- **The author area adds its navigation's column beside the reading
  column.** Each author page's body keeps the 56rem column, as
  `pages/author/README.md` gives, and its problems page opens a problem in a
  dialog as wide as the window.
- **Every page but the sitting reads at phone width.** A sitting on the web
  wants a wide window, and a narrow one stacks the statement above the editor
  rather than shrinking both. The phone's sitting holds the two as tabs
  instead, as `pages/problems/problem/README.md` gives.

## Rows and panels

- **A bordered chip is a control, and a destination reads as a link.** The
  listing's filters are chips, since a press toggles one. The techniques the
  board offers are names that underline on hover, since a press opens the
  technique. Two shapes that look alike and act differently teach a reader the
  wrong thing about both.
- **A list of picks reads as rows, and the whole row is the link.** The board's
  techniques, a technique's problems and the cards are each such a list. A
  table spreads one pick over four columns, and the reader then joins the
  columns back together to judge the pick.
- **A list split into sections reads each section under a plain heading with
  its count, above a bordered panel of rows.** The board and the cards list
  split their lists the same way, so a reader learns one shape.
- **One record reads as one row wherever it is listed.** A card in progress on
  the board is the same row as on the cards list, so a reader never learns a
  second shape for it.
- **A row's progress reads as one bar, the same on a card and a module.** A
  card's bar counts the rungs solved, and a module's counts the questions
  passed. A reader then compares two studies by one shape.
- **A row's counts read as one cluster at its right**, each count beside the
  word it counts. A row with nothing counted says so in one word, since three
  counts of nothing say less than `never` does.
- **Below 640px the counts read on a line under the title, on both clients.**
  At the right, the counts keep their width and leave the title a column a
  word or two wide.
- **A panel holds what a page carries beside its reading**: a bordered block on
  the card surface. The counts a card run reached and a submission's verdict
  are each one. Every panel carries the same
  border, radius and ground, so a reader tells a panel from the reading by its
  shape alone.
- **A panel's header strip names a record, and opens it.** A strip that named
  a record and opened nothing would be a dead end.

## The section bar

- **A page longer than a screen carries a bar naming its sections.** The bar
  stays at the top of the window while the page scrolls, and it marks the
  section the reader is in. A press on it jumps to that section.
- **The bar scrolls sideways to keep the marked section in view**, as the
  navigation does at phone width. A phone holds two or three of a lesson's
  sections, and a mark the reader cannot see says nothing.
- **An edge of the bar fades where more sections lie past it.** A row cut at
  the screen's edge reads as a row that ends there.
- **At the end of the page the bar marks the last section.** The last section
  is often shorter than the screen, so its heading never reaches the top, and
  the mark would otherwise stay on the section before it.
- **A section pressed on the bar stays marked until the reader scrolls by
  hand.** A jump near the end lands at the end of the page, where the rule
  above would mark the last section rather than the one pressed.

## Sections

- **A section collapses from its own heading**, and every section is open until
  the reader closes it. The count beside the heading stays readable while the
  section is closed.
- **Which sections a reader closed is not stored**, in the browser or
  anywhere else, so a reload opens every section again.
- **A section of rows sits in a bordered panel under its heading**, the rows
  edge to edge. The border groups the rows into one list.
- **A section of prose reads bare under its heading.** A code block inside it
  is then the only box on the page. A panel around the prose put a box inside
  a box and cost four characters of a phone's code width.
- **A lesson and a card's brief are cut at their `##` headings**, each heading
  a section of the page. Without a panel, a heading inside a section would
  read as a section of its own, so no section holds one. Text before the first
  heading reads under the brief's own title.
