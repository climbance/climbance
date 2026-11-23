# The generation page

The page at `/author/generation`, in the author area: how problem generation
goes, read from the drafts, the site outcomes, the problems and the template
matches. `../README.md` gives who reaches it.

[`generation.md`](generation.md) draws the page at low fidelity.

- **The drafts read as a count per writing state.** The store keeps a draft
  until it lands, so the counts name what is held and what was rejected. A
  held state's row names its oldest draft's age, since a held draft waits for
  `generate --resume`.
- **The landing rate counts writings, not drafts.** A writing is named by its
  writing id on the site outcomes. A writing landed when one of its site
  outcomes names a problem. The rate is the landed writings over all writings
  in the period, since a landed writing leaves no draft to count.
- **A rejected or held writing is counted under the gate that stopped it, by
  the site the gate is filed under.** The table reads one row per site and
  gate, such as `screen · copied`, so the author sees which site loses the
  most writings.
- **The spend per landed problem divides every writing's cost by the
  landed writings.** A rejected writing's calls were paid for too, so a cost
  counted only over landed writings would understate what a problem costs.
  The cost is the `cost` on each site outcome, as the router charged it. The
  page names how many site outcomes carry no cost, since a sum over a missing
  value reads lower than the truth.
- **The corpus reads as a table of templates by difficulty band.** A row is a
  card's template, and a cell counts the problems written for it whose
  standing difficulty falls in the band. A retired problem is counted apart,
  since it is no longer served. A core template no solution displays reads
  as a gap on its row, as `climb gaps` reports it today.
- **The period is the last 30 days, by the writing's first site outcome.** The
  drafts and the corpus read as they stand now, since each is a state rather
  than a flow. A period the author chooses is deferred until 30 days is seen
  to be the wrong one.
