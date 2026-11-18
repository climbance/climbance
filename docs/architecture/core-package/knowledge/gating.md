# Gating

New questions open as earlier ones are passed. A question already seen is
reviewed whatever gates it.

- **Levels open in order within a subtopic.** A level opens when every lower
  level of the same subtopic is done or holds no questions. Level 0 is always
  open.
- **A module may carry a prerequisite graph between subtopics.** An edge from
  one subtopic to another, at an offset, opens the first subtopic's level only
  once the second subtopic is done up to that level plus the offset. Levels
  above a configured bound match at the bound.
- **A gate restricts new questions alone.** Every review reaches a seen
  question in a locked group, so a reordered graph never hides a fact the
  user already met.
- **The graph is content, and an unlock is never stored.** Each unlock is
  derived from the answers and the current graph, so editing the graph needs
  no migration and loses no progress.
- **The frontier is the open groups that are not done**, ordered by the
  length of the prerequisite chain below each subtopic, then by listing
  order.
- **A new question comes from the first frontier group with an unseen
  question no lesson holds.** A group stays on the frontier until enough of it
  is passed, so the first group can hold no new question at all.
- **A module names that same group as next up**, with its passed share. A
  module whose open groups all wait for a lesson names that lesson instead.
  Continue and the module then point at one place.
- **A graph that fails its own check opens everything.** A cycle or an
  unknown slug would otherwise lock questions nobody can unlock.
