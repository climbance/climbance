# Modules

A module is one subject of declarative knowledge: Python first, then algorithms
and system design. A user answers its questions from memory.

## The tree

- **A module holds topics, and a topic holds subtopics.** A topic carries a
  tier, which orders the listing and gates nothing. A subtopic belongs to one
  topic, and its questions are listed in the order it names them.
- **A subtopic may carry a title**, given by its topic, and a client shows the
  title in place of the slug. A subtopic with no title shows its slug, so a
  module authored without titles still reads.
- **A subtopic is shown with its topic's title**, except where its topic
  already heads the view. Two topics can each hold a subtopic called basics.
- **Titles are in sentence case**, as lesson and topic titles are: the first
  word and proper nouns alone are capitalized.
- **Every question sits at one of four levels**: 0 Foundation, 1 Associate,
  2 Professional and 3 Expert. A level measures the depth of a question. A
  problem's difficulty is a different field, on a different record.
- **A group is one subtopic at one level.** Gating, coverage and the frontier
  are all counted per group.
- **A module is authored in files and seeded into Postgres**, as a card is.
  `../core-package/knowledge/` gives the rules the engine and the clients
  apply to what is seeded, and `## Authoring` gives where the rules for
  writing the files live.
- **A module, a topic, a subtopic, a question and a lesson each carry an
  engine-minted id**, and the seed matches each by its authored slug. A log
  record then references a minted id, as `../concepts/invariants.md` requires
  of every append-only record.

## Techniques

- **A subtopic may name techniques**, each by its code in the vocabulary,
  authored in `course.toml` as its topic's `sub_techniques`. The seed refuses
  a code the vocabulary does not hold.
- **A technique may be named by any number of subtopics, in any module.** A
  technique is sized for classifying code, and a subtopic for teaching, so
  neither bounds how many of the other it is paired with. Most subtopics
  name one technique, and nothing requires it.
- **A question carries its subtopic's techniques.** A knowledge reading counts
  the answers to every subtopic naming the technique. A question naming
  techniques of its own is deferred until a subtopic mixing two techniques
  needs it. `cards-and-subtopics.md` gives what a subtopic
  teaches beside a card.

## Authoring

A module's files are written to rules this repo holds, and checked by code
this repo holds. The content repository holds the modules alone.

- **The authoring rules live in `docs/authoring/`.** `modules.md` gives how a
  module is authored, the level definitions among it. `rules.md` gives the
  numbered rules every bank and lesson holds, and how each rule is checked. A
  writer session reads both without reading another module's files.
- **Each module keeps its own rules beside its files**, in the content
  repository. They are the module's `CLAUDE.md`, the `requirements.txt` its
  snippets import from, and the skip list `check.toml`. A skip names a
  question or a lesson, so the skip list is content.
- **Two checks read a module, and they stay apart.** The seed refuses a module
  whose files break the format, and executes nothing. `climb module
  check <slug>` runs every snippet and every lesson block, and judges each
  rule a program can judge. The seed then runs without the module's libraries
  installed.
- **The module check installs the module's libraries for its run alone.** A
  library a snippet imports is no dependency of the engine, so a module adds
  nothing to the engine's lock file.
- **An authoring file names a module `course`**, in `course.toml`. The word
  names the file and nothing else.

## Diagrams

A structure drawn as a graph, such as a flow, a state machine, a tree or a
lookup order, is authored as Mermaid source. It reaches both clients as an
SVG the seed drew.

- **A diagram is authored as Mermaid source**: a ` ```mermaid ` fence in a
  lesson, or a question's `diagram` that is one ` ```mermaid ` fence alone.
  The source stays in the content, so a later seed can draw it again.
- **The seed draws each source to SVG, once in the light scheme and once in
  the dark.** On 2026-11-12 one diagram on a Redmi Note 13 Pro 5G showed in
  about 0.2 s as the seed's SVG. Drawn on the phone instead, Mermaid loaded a
  5.5 MB library into a WebView and showed the diagram after 2.2 to 2.8 s.
- **The seed draws with mermaid-cli in headless Chromium, on the author's
  machine.** The drawing tool lives in `tools/diagrams/`, outside the npm
  workspace, so installing the engine downloads no browser. A seed that meets
  a source it has not drawn, without the tool installed, fails.
- **The seed prepares each SVG for `react-native-svg`, the phone's drawer.**
  Labels are SVG text rather than HTML, styles are inlined, markers sit in
  `<defs>`, and each label's words are joined into one span. Entities in text
  are decoded, and text holding `<` is wrapped in CDATA. The phone drew each
  of these wrongly when the SVG was left as Mermaid wrote it.
- **A drawing is stored once per source**, in the `diagrams` table, keyed by
  the hash of the source and of the drawing tool's version. A re-seed draws
  only what it has not drawn, since a draw costs about a second.
- **The snapshot carries the drawings beside the courses**, as `diagrams`,
  mapping each source to its light and its dark SVG. The format number stays
  6, since a client reading format 6 alone ignores the field. 160 diagrams
  add about 1.4 MB to the 4.8 MB snapshot, and 0.35 MB gzipped.
- **A client draws the SVG of its scheme, scaled to the reading width.** A
  diagram wider than the screen shrinks rather than scrolls, so a source is
  laid out top to bottom, with at most three nodes side by side.
- **A source with no drawing reads as its monospace text**, as a `text` block
  does. An older client and a snapshot taken before a seed drew the source
  both meet one.
- **The drawings use Mermaid's own default and dark themes.** Matching the
  app's palette is deferred until real use shows the difference matters.
- **The drawings turn off the gradient and the drop shadow.** Mermaid 12's
  default look, `neo`, strokes each box with a gradient and shadows it, and
  the gradient reads as a fault on a phone. The `classic` look drops both but
  lays a flowchart out wider, and 30 diagrams then passed 460 pixels.
