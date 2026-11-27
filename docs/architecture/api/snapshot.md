# Snapshot

The snapshot is the whole content of every live module as one JSON document,
which both clients load through `packages/core`.
`../core-package/knowledge/store.md` gives how a client keeps it and
revalidates it.

- **The content reaches a client as one snapshot, at snapshot format 6.** The
  format is the module tree, the questions, the lessons and the scheduling
  rules in one JSON document, and the loader in `packages/core` reads it. A
  field added since format 6 is left out where empty: the drawings
  `../content-repo/modules.md` `## Diagrams` gives, and a topic's `sub_titles`
  and `sub_techniques`, and a module's `drills`. A module carrying none of
  them then reads as format 6 alone.
- **A module's drill items travel under `drills`, apart from `questions`.**
  An installed app reads every entry of `questions` as a format it knows, so
  a drill there would reach a build that cannot draw it.
  `../content-repo/ai-drills.md` gives the drill items.
- **The snapshot's scheduling rules keep `mastered_stability_days`** for the
  stability at which a question is retained. An installed app reads that key
  from every snapshot, so renaming it would break a build already on a
  phone.
