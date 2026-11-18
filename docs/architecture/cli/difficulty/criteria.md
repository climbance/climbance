# The criteria

The generator aims at a label by these criteria, and the bands' cuts are set
to reproduce them. A rater checks a problem against these in order, and the
first level that fits is the label. Each criterion counts the steps a solution
takes beyond one template's form, so two raters reading one statement reach
one label.

- **Easy: the solution is one basic form applied unchanged, or a direct
  approach that fits the limits.** The basic forms are the templates
  [`easy-templates.md`](easy-templates.md) names, most of them on the root
  cards of the card graph. The statement asks the form's own question about the
  input as given. A solver who holds the form types it and adapts only names
  and the return value.
- **Medium: one standard technique, plus one step the statement does not
  name.** The step transforms the input, chooses a state, or derives the
  predicate a search runs on. A search for the smallest feasible capacity is
  medium: the form is easy, and the feasibility check is the derived step.
- **Medium also covers a form that is itself a step past the basics**, applied
  directly: a monotonic stack, a disjoint set, a topological order, a knapsack,
  a backtracking search, and a choice per element under an adjacency ban.
- **Hard: a form few solvers hold, or two techniques combined, or a step the
  statement gives no hint of.** A sliding-window maximum on a deque and the
  largest rectangle in a histogram are each hard applied directly. So are
  counting the windows with exactly k distinct values by complement, placing n
  queens, and the longest cycle of a graph with one edge out of each node.
