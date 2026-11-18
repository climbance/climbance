# Classifier

The classifier is the model call reading an attempt's or a solution's code for
the techniques it used. This file gives the solution claims it writes. The
attempt claims it writes are still in `../log.md` `## Attempt claims`, until
`split-log-doc` moves the classifier's part here.

## Solution claims

A solution claim names which techniques a solution used. It is
product-owned and global, as the solution is.

- **A solution claim is its own record, not an attempt claim.** A claim is
  testimony about the user's own attempt, and is private. A solution claim is
  a verdict about code the engine wrote, and ships with the corpus. One record
  type for both would also make the fallback a fold over records of the type it
  falls back for.
- **The candidates are the whole vocabulary**, where an attempt is classified
  against the problem's own techniques. A problem's techniques are derived
  from these claims, so constraining a solution claim by them is circular.
- **One classifier writes two records.** The prompt, the transport and the
  staleness rule are shared with the attempt classifier. Two prompts asking
  one question would drift, and neither score would compare with the other.
- **A solution claim is a machine record like any other**: provenance whole,
  staleness keyed on the prompt hash of what was sent, and re-derivable at any
  time. A claim carries one problem's criteria, and a solution claim carries
  the whole vocabulary's, so any criteria edit re-reads every canonical.
- **Two writers, and the user's stands first**, as a claim resolves. A user
  reading adjudicates rather than testifies: nobody sat for a canonical, so the
  user's reading is of code they did not produce. The user's solution claim
  stands all the same, and it is the reference a configuration is scored
  against.
