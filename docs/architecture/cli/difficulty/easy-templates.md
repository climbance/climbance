# The templates that admit an easy problem

A template admits an easy problem where its form, applied unchanged, answers a
question the platforms label easy. The sweeps write easy problems for these
templates alone.

| Card | Templates admitting easy |
|---|---|
| `binary-search` | `predicate-first-true`, `answer-space` |
| `sliding-window` | `fixed-window-match` |
| `dp-1d-linear` | `two-prev-pick-skip`, `running-aggregate` |
| `hashing` | `complement-lookup`, `count-then-query` |
| `two-pointers` | `compact-in-place`, `merge-sorted-heads`, `converge-sorted-pair` |
| `prefix-sum` | `range-sum-table` |
| `sorting` | `sort-then-sweep`, `composite-key` |
| `stack` | `match-nesting`, `collapse-adjacent`, `evaluate-postfix` |
| `linked-list` | `reverse-in-place`, `fast-slow-middle`, `merge-two-sorted` |
| `tree-traversal` | `inorder-stack`, `inorder-neighbours`, `level-order` |
| `breadth-first-search` | `unweighted-distance` |
| `depth-first-search` | `component-count`, `grid-flood-area` |
| `heap` | `top-k-bounded`, `combine-smallest-two` |
| `binary-search-tree` | `descend-floor-ceiling`, `range-sum-prune` |
| `greedy` | `smallest-sufficient-match` |

- **`converge-sorted-pair` admits easy only in its plainest uses**: a
  palindrome check, squaring a sorted array. A pair sum on a sorted array is
  medium on the platforms.
- **`answer-space` admits easy only where the predicate is given**, as in an
  integer square root. A predicate the solver has to derive makes the problem
  medium, by [`criteria.md`](criteria.md).
- **`two-prev-pick-skip` and `running-aggregate` admit easy only in their
  plainest use**: counting the ways up a staircase, the cheapest climb, the best
  single buy and sell. The adjacency ban and the best contiguous sum are
  medium.
- **`monotonic-stack`, `union-find`, `topological-sort`, `dp-knapsack-01`,
  `dp-state-design` and `backtracking` admit none.** Each form is a step past
  the basics, so its direct use is medium already. These cards take no easy
  rung.
