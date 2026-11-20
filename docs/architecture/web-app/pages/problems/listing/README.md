# The problem listing

The page at `/problems`, the root of Problems, and the phone's Problems tab:
every problem the corpus serves, filtered and read in pages.

## Filters

- **The listing filters by two things a problem carries: its techniques and its
  difficulty.** The tags it offers are the techniques the listing itself holds,
  and the difficulties are the three a problem can carry: easy, medium and
  hard. A question's level is a different field, as
  `../../../../content-repo/modules.md` gives.
- **A second pick inside one filter widens the list, and the two filters
  narrow each other.** A problem is shown where it carries any tag the user
  picked and sits at any difficulty they asked for. Two techniques ask for
  the problems of either, where a technique and a difficulty ask for the
  problems of both.
- **Each chip counts what pressing it would leave**, so the difficulties
  count what the tags left and the tags count what the difficulties left. A
  count over the whole corpus would offer a chip that returns nothing.
- **Picking a filter moves no row of the page.** The chips keep the order the
  whole listing gives and a fixed width for their count, and the press that
  clears the filters sits in the heading rather than on a line of its own. A
  reader comparing two problems otherwise loses the one they were reading as
  the chips above rewrap.
- **The URL carries the tags, the difficulties and the page**, as `?technique=`,
  `?difficulty=` and `?page=`. A filtered listing is then a link the user can
  keep, and the three are the page's whole state.
- **The phone's Problems tab reads the listing as the web's page does.** A
  row opens the phone's Problem screen, which reads the record and the
  statement. The filters live in the tab while it is open, since the phone
  has no URL to keep them in.

## Pages and rows

- **The listing is read in pages of twenty rows.** Fifty problems already scroll
  past several screens, and a reader picking one compares a handful at a time.
- **Picking either filter returns the listing to its first page.** The page the
  reader was on may hold nothing once the list is narrowed.
- **The whole listing is fetched, and a page is a slice of it.** The tags count
  every problem the corpus carries, so a page of rows cannot produce them. The
  API pages the rows instead once the corpus outgrows one request.
- **The listing names no retired problem, and the problem's own URL still
  answers.** A retired problem was never a fair test, so a reader picking one
  to sit is picking a problem the engine refuses to serve. The user's attempts
  on it stay in the log, and a link kept from before the retirement therefore
  opens a page rather than a 404.
