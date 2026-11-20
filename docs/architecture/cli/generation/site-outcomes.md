# Site outcomes

The record of what one generation call site left on one writing. A model wrote
no part of it. The record holds what the run's gates said about the answer a
call returned, and it names that call in the call log, `../calls.md`.

## The record

- **Each site's outcome is stored rather than only printed.** The run prints
  one line per stage, and that output is gone when the process ends. Without a
  stored record, nobody can later see which gate rejected an answer, which
  configuration produced it, or which prompt hash it was sent.
- **One record per site and per writing.** The six sites can run at six
  configurations, and one record over the writing could not say which of them a
  gate rejected.
- **The writing carries an id the run mints.** A rejected draft has no problem
  to key to, and the rejected writing is the one whose cost nothing else
  records.
- **The problem is named where one landed.** Its id exists only once the problem
  is stored, so the records are written at that point rather than as each site
  answers.
- **A site that made no call writes no record.** Provenance is all or none, and
  a record carrying none compares with nothing. A missing record means the site
  was never asked, which happens when the first case set already killed every
  mutant.
- **The records are written at one point, once the loop has run.** A site
  answers before its counters are known, so writing as each answers would need
  a record amended later. The cost is holding the first case set's verdict
  until then, since a gate raised after it belongs to another site.
- **The verdicts are named fields rather than a mapping.** A report groups by
  gate and averages the counters, and a mapping makes every key a field nothing
  enforces.

## Which site a count or a gate is filed under

- **A gate is filed under the site whose answer made it decidable.** A
  canonical yielding no value on a case is the generator's. A disagreement is
  the blind site's, since nothing disagrees before a second reading of the
  statement exists.
- **A kill is filed under the site whose output did it**, as a gate is filed
  under the site whose answer made it decidable. The mutants the statement's own
  cases caught are the generator's, the mutants built inputs caught are the
  inputs site's, and a round's are the discrimination site's.
- **That attribution makes the split complete.** Each site's record exists
  exactly where its own count can be other than zero: the generator always
  answered, the fuzz pass ran only where a generator was written, and a round
  killed only where one was asked. Held on the discrimination record alone, the
  three sources would go unrecorded on every writing the fuzz pass finished,
  and that writing is the one that says a round was not needed.
- **The mutants a canonical yielded sit on the site that wrote it.** The count
  is a fact about that solution, so it is readable on a writing no round
  reached, and two generator configurations compare on it.
- **A canonical contradicting its own call's declarations is counted, not
  gated.** The code and the declaration came from one call, so the count reads
  that site's arithmetic. `test-cases.md` names the record that
  settles the case instead.
- **The search's measurements are filed under both sites it judged.** The
  search times the naive solution against the canonical on an input the input
  generator made, so neither answer alone makes the verdict decidable. The
  separating size, the repeat count and the reason nothing separated go on
  both records. The gate the search raises stays on the input generator's
  record, since the search ran that site's code. A resume that re-asked
  one of the two sites writes that site's record and no other, so the separating
  size would otherwise be lost with the site the resume reused.
- **Two of a problem's records can carry different verdicts.** The input
  generator's record answers for the search that judged it when it was written,
  and a later naive solution's record answers for the search that judged the
  redraw. Each record says what one answer was worth at one configuration, and
  that is the purpose of a record.
- **The exception is the gate no answer was rejected by.** A held draft is
  rejected where the problem does not exercise the form its template claims,
  and every site answered. That gate is read from the draft, since the draft is
  the record that outlives the run.

## The counters

- **The input generator's bound is on the record, not only on the draft.** A
  landed problem clears its draft, so the largest input the statement admits is
  readable nowhere else. The bound says whether a walk that stored no case
  reached the bound or stopped under it.
- **The bound is not a denominator.** The bound counts whatever the input
  generator's `size` counts, which is a list length on one problem and a grid's
  side on another. `test-cases.md` gives what a separating size
  is comparable with.
- **The aimed difficulty is on the generator's record alone.** `generate
  --difficulty` names a level in the generator's prompt, and no other site's
  prompt names one. A landed problem clears its draft, so only the record
  keeps the aim readable. The generator still labels the problem it wrote, and
  a label differing from the aim is stored as written.
- **The discrimination record cites the last round's call.** A loop pays for up
  to two rounds, and the record carries the counters the last round left.
- **A round records what it proposed beside what landed.** A proposal that
  killed nothing is not stored, so the set alone cannot say what the call was
  paid for. The difference between the two counts is the proposals the round
  paid for and gained nothing from.
- **The kills per round are a list, in order.** A field per round would fix the
  bound in the schema, where `ROUNDS` is the number a corpus revises. The list
  is the one ordered counter, and a report reads position rather than a key.

## Asking a site again

- **A site skips an item it has answered at the current prompt hash**, as the
  classifier skips a claim. So a second configuration is paid for only where it
  has not read, and the run that wrote the problem answers for the bench it was
  written with.
- **The item is the problem, and the generator has none.** The generator writes
  a problem rather than answering one, and asking the generator again is a new
  problem by design. The other five sites are re-asked about a statement the
  store already holds.
