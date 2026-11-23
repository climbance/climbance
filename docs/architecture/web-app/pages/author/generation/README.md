# The generation page

The page at `/author/generation`, in the author area: how problem generation
goes, read from the drafts, the site outcomes, the problems and the template
matches. `../README.md` gives who reaches it.

[`generation.md`](generation.md) draws the page at low fidelity.

- **The drafts read as a count per writing state.** The store keeps a draft
  until it lands, so the counts name what is held and what was rejected. A
  held state's row names its oldest draft's age, since a held draft waits for
  `generate --resume`. The draft stores no time, so the age is read from the
  first site outcome of the writing the draft's id names.
- **The landing rate counts writings, not drafts.** A writing is named by its
  writing id on the site outcomes. A writing landed when one of its site
  outcomes names a problem. The rate is the landed writings over all writings
  in the period, since a landed writing leaves no draft to count.
- **A writing with no generator outcome is a replay, and is not counted.** A
  replay runs the five answering sites over a problem already landed. Its
  outcomes name that problem, so counting them would add a landing that never
  happened.
- **A rejected or held writing is counted under the gate that stopped it, by
  the site the gate is filed under.** The table reads one row per site and
  gate, such as `screen · copied`, so the author sees which site loses the
  most writings. `unexercised` is read from the draft and names no site,
  since no site's answer raised it. A held writing with no gate reads `held
  at` its state.
- **The spend per landed problem divides every writing's cost by the
  landed writings.** A rejected writing's calls were paid for too, so a cost
  counted only over landed writings would understate what a problem costs.
  The cost is the `cost` on each site outcome, as the router charged it. The
  page names how many site outcomes carry no cost, since a sum over a missing
  value reads lower than the truth.
- **The spend leaves out the first of two discrimination rounds.** The
  discrimination outcome cites the last round's call, and the call log names
  no writing. A writing that ran two rounds therefore reads cheaper than it
  was. Recording each round's call is deferred until the spend is read
  against the router's own bill.
- **The corpus reads as a table of templates by difficulty band.** A row is a
  card's template, and a cell counts the problems written for it whose
  standing difficulty falls in the band. A retired problem is counted apart,
  since it is no longer served. A core template no solution displays reads
  as a gap on its row, as `climb gaps` reports it today. A served problem
  with neither a rating nor the generator's label is counted as unlabelled,
  in a column shown only when one exists. The page names how many problems
  were written for a technique, since those sit on no template's row.
- **The period is the last 30 days, by the writing's first site outcome.** The
  drafts and the corpus read as they stand now, since each is a state rather
  than a flow. A period the author chooses is deferred until 30 days is seen
  to be the wrong one.
