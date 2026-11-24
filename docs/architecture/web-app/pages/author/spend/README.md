# The spend page

The page at `/author/spend`, in the author area: what each part's model calls
cost. `../README.md` gives who reaches it.

[`spend.md`](spend.md) draws the page at low fidelity.

- **The spend reads by the part whose record cites the call**, for the last
  30 days. A call record names no domain, as `../../../../cli/calls.md` gives,
  so the part is read from the record citing its `call_id`: generation by
  site, difficulty, the classifier, the matcher and the diagnoser. A call no
  record cites, such as a failure, reads as `uncited`. The cost is the
  call's own `cost`, and the page names how many calls carry none.
- **The spend has a page of its own, beside the product and the generation.**
  The spend is a figure the author measures, and it covers every part that
  makes calls. The generation page's spend per landed problem covers
  generation alone, as `../generation/README.md` gives.
