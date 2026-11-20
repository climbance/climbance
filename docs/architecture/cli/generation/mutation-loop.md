# Mutation loop

Step 10 of `README.md` `## Generating a problem`. Mutants of the canonical run
against the cases, then against inputs the input generator builds, in the
fuzz pass. A round then asks the discrimination site for cases that kill
whichever mutant survived both, and the cases that killed are appended to the
set. `test-cases.md` gives the cases the loop stores.

## The mutants

- **No model is asked how good the cases are.** A model asked whether its own
  cases suffice says yes. A model asked to break its own solution writes the
  mistakes it expects a solver to make, which is a sample nobody chose and no
  run reproduces. A tree walk enumerates the mutants instead, so the set is
  deterministic and re-derivable, and nothing about the set is stored.
- **A mutant is the canonical with one semantic change**, made on the parsed
  tree rather than the text, so a comparison inside a string is untouched. A
  mutant is killed when it fails at least one case, and a surviving mutant is
  a case that has to exist.
- **A mutant runs under a cap paced by the canonical**, never under the one
  the reference needs. A change that breaks a loop's progress never returns,
  and the solution a mutant has to beat is the canonical it is a copy of.
- **An operator changes one decision the code makes**, and each operator is a
  mistake a solver makes. A mutant nobody would write asks for a case that
  catches nothing. The set of operators is in `climb.mutation`.

## The fuzz pass

- **The fuzz pass runs only where a mutant is standing.** A case set that
  already kills every mutant builds nothing, so a problem the statement's
  own cases decide costs no execution here.
- **The canonical is the oracle for killing, and the reference settles the
  case.** A mutant is killed by answering a built input differently from the
  canonical, which needs no expected value. The reference runs on the kept
  inputs alone.
- **A kept input is shrunk before it is stored.** The mistake it catches
  usually needs a few elements, and every later verification saves the
  difference. The shrink keeps every mutant that input killed, and shortens
  lists alone, since a smaller number may break the statement's constraints.
  It runs on a budget of candidates, each costing a run per mutant.
- **The shrunk input is answered again, and weighed after the shrink.** The
  canonical computes its answer, and an input over the ceiling may fit once it
  is only as large as the kill needs.

## The rounds

- **The call that answers a survivor proposes arguments, never returns.** The
  reference computes what the arguments return, so no model writes an
  expected output that could agree with the mistake the case was asked for.
- **A round is shown what the pass kept.** Those cases are in the set the
  survivors were decided against, so re-proposing one would win a case that
  kills nothing.
- **A proposed case that killed nothing does not land.** Every later
  verification runs the stored set, and a case no mutant fails catches nothing
  a case already there does not. Which mutants each proposal killed is read
  from the kill pass the round already pays for, so nothing extra runs.
- **Two proposals killing one mutant land the first.** The second proposal
  decides nothing the set does not already decide, so the order the round
  proposed them in settles which one lands. The fuzz pass keeps its inputs by
  the same rule, building smallest first, so a kept input is the smallest that
  separates.
- **A dropped proposal is still shown to the next round.** The dropped
  proposal is not in the set, and a round shown neither the set nor the
  dropped proposal could propose an input that already killed nothing.
- **The set written with the statement is exempt.** Those cases describe what
  the problem asks rather than what a mutant fails, so they land whether or
  not they kill.
- **The loop stops after two rounds, at one call each, never on a score.** A
  survivor two rounds did not kill is usually equivalent to the canonical, and
  no case kills an equivalent mutant. A round that kills nothing stops the
  loop early. The bound was set before a corpus existed, and how much the
  second round still kills revises it. On the first landings it killed
  nothing: the statement's own cases killed 46 of 53 and 17 of 22 mutants,
  round one killed none of the survivors, and each survivor was equivalent by
  inspection.

## What an answer does to the draft

- **A proposed or built input the canonical cannot answer drops the case, not
  the problem.** No check reads an input against the constraints the statement
  gives, so a crash or a timeout on a proposed input is as likely to be an
  input the problem excludes as a defect in the solution. The canonical was
  already run against the cases written with the statement, and those cases
  decide it.
- **A proposed or kept case the two solutions answer differently rejects the
  draft**, as a disagreement on any other case does. The round asks for
  boundary inputs, and the loop exists to find a canonical wrong at a boundary
  the first set never reached.
- **A round that proposes nothing is a verdict, never a failure.** No input
  separates a mutant equivalent to the canonical, and the loop's bound already
  expects such a mutant. A round read as a failed call would hold the draft,
  and every resume would then ask the same question of the same survivors.
- **A round whose call fails holds the draft.** The problem passed every gate
  that judges it, and its set was never measured against the bound. Landing
  the problem would store a set no round was paid for, where a resume asks
  the loop again.
