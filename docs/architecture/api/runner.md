# Runner

How a solution is run. The runner is a component and can be replaced. A
`Verification` is append-only and cannot. So the meaning of a stored result is
fixed here rather than by whatever executed it.

## The cap and the verdict

- **The cap is wall clock around the `solve` call, measured in the child.**
  Interpreter start is excluded, since it moves with the machine's load. Two
  runs storing one number would otherwise not be comparable.
- **A case is decided by JSON equality on the returned value**, encoded with
  sorted keys. A tuple and a list are one answer under that rule, and `True`
  and `1` are two.
- **A statement asks for a value that compares exactly**: integers, strings,
  booleans and lists of those. A floating-point answer is compared bit for bit,
  and two correct solutions computing a ratio in different orders disagree in
  the last bits. Such a draft is rejected as `disagreed` however sound the
  statement is. A ratio is asked for as a reduced numerator and denominator.
- **A problem admitting several correct returns does not land.** The
  alternative is a checker per problem, and every stored verdict would then
  depend on code the record does not name. The statement says how ties are
  broken, and a canonical and a reference disagreeing catches a statement
  that does not. The rule excludes a problem asking for any valid answer of
  many, and that cost is accepted until a core template needs one.
- **A return that JSON cannot encode is `CRASHED`.** The fault is the
  solution's rather than the case's. `WRONG` would file it beside an answer
  that was computed and is merely incorrect. The child does the encoding, so
  every runner uses the encoder `as_json` uses, or the same return would be
  decided differently by where it ran.
- **A solution defining no module-level `solve` fails every case as
  `CRASHED`.** Code that does not parse is rejected the same way. It is a
  verdict rather than an error, because a sitting reads this path for an
  attempt, and a submission with a syntax error is the ordinary case.
- **The stored cap is the child's**, since that is the number the case was
  judged by. The parent runs a slack timer of its own, which the runner owns.
- **A child reporting nothing is read from how it died.** The parent's timer
  firing is `TIMEOUT`. A signal is `CRASHED`, and a segfault and a kill under
  memory pressure both land there. Anything else is the runner's own fault and
  is raised, since it says nothing about the solution.

## What a case result keeps

- **A crashed case carries what raised it**, as a traceback prints it over the
  solution's own lines. The runner's frames are left out, since they name no
  line the solver wrote. The solver reads which line raised, and a diagnosis
  reads a compile error the outcome alone would lose.
- **The error is stored on the case result**, not only shown. `../log.md` has a
  diagnosis read a compile error months after the attempt, when only the record
  is left.
- **A wrong case stores the JSON it returned**, up to 64 KiB. A reopened
  sitting reads the failing case back from the record, and no rerun is spent
  on it. A larger return is not kept, since a 1 MiB case answered wrong on
  every submission would grow the log by that much each time. A case result
  written before the field existed keeps no return either, and the page says
  so.
- **A case result carries what the child measured.** The separating input a
  speedup search looks for is found from those numbers, and a result holding
  only the outcome would make every later search re-run the whole set.

## The runner's boundary

- **No case observes another.** A solution memoising in a module global would
  otherwise answer one case from a cache built for a different one, and a wrong
  key would pass. Which mechanism gives that isolation is the runner's to
  choose.
- **A runner fault is raised, never recorded.** A subprocess that fails to
  start says nothing about the solution, and a stored `CRASHED` would reject a
  sound draft over the runner's own defect.
- **Comparison stays outside the runner.** A runner is handed code, the
  arguments and a cap, and returns what each call produced. The runner is
  never told what a case expects, so the rule deciding a case cannot vary by
  where the code ran.
- **A case yielding no value is read by the solution's role.** A canonical that
  crashed or timed out rejects the draft, since nothing establishes what the
  case returns. A reference that crashed or timed out is the ordinary path
  beyond its reach, and the case takes the canonical's answer, with
  `expected_from` naming the canonical.
