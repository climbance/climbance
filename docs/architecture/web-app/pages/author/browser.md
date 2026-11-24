# The content browser

The content browser is the four author pages listing content: the questions,
the lessons, the cards and the problems. The author reads a whole bank there
at once, as a learner would see each item. A question is otherwise reviewed
one at a time in a queue, where a rule broken across a bank, such as long hand
traces, goes unseen. `README.md` gives the author area these pages sit in.

## The reads

- **The browser's pages were built in this order: the questions, the lessons,
  the cards, then the problems.** The questions are the largest bank and the
  one reviewed only in a queue before the browser. The lessons read from the
  same snapshot, so the lessons page reuses the questions page's filters.
- **Each page reads the content of the engine serving it.** The questions and
  the lessons come from the snapshot, which the seed builds from the store.
  The cards and the problems come from `/api/author/`. `just app-prod` then
  shows prod's content and `just app` shows the local store's.
- **Each item is drawn with the component a learner's page draws it with.** A
  question uses the queue's answered question, a lesson the lesson page's, a
  card the card page's, and a statement the sitting's. A component of the
  browser's own could show an item differently from what a learner reads.
- **The browser only reads.** A change to a question, a lesson or a card is an
  edit in the content repository, then a seed. A problem is never edited and
  is retired with `climb problem --retire`. No press writes a log record, so
  a review leaves the author's own schedule and board unchanged.
- **The grid's rows carry only the grid's columns, and an opened item is a
  request of its own.** The cards page reads its rows from
  `/api/author/cards` and one card from `/api/author/cards/:slug`. The
  problems page reads its rows and one problem the same way. The questions
  page requests only the opened question's concept. Before this split, the
  questions page fetched 237 kB of `algo`'s concepts to draw a list that shows
  none of them.

## The grid

- **Each browser page lists its rows in one grid**: a row per item and a
  column per field, under a header naming each column. A row reads on one
  line, so a window holds about 25 rows. The author scans one column down the
  bank, such as the code's length or the ladder's gaps, and every row sets
  that field at the same place.
- **One grid component draws the four pages**, built on shadcn's table. A
  page names its columns, and the component draws the header, the rows, the
  sort and the marked row the same way on every page.
- **A press on a sortable column's header sorts the rows by that column, and
  a second press reverses the order.** The sort is in the URL as `?sort=`
  and `?order=`, as the filters are. A number or a date sorts highest first on
  the first press, and a text sorts from A. With no sort named, the rows read
  in the order the page's own file gives.
- **The filters live in the URL, and each chip counts what pressing it would
  leave**, as on the problem listing. A filtered view is then a link the author
  keeps.
- **A row expands nowhere.** An item opened in place pushed the next row out
  of sight, and several opened cards ran past the window. The dialog below
  replaced the opened row on every browser page.

## The dialog

- **A press on a row opens the item in a dialog over the grid.** The grid
  keeps its rows and its scroll under the dialog. The questions, the lessons
  and the cards read in a dialog the reading column's width, since each reads
  in a screen or two. The problems page's dialog fills the window, as
  `problems/README.md` gives.
- **One item is opened at a time, and the anchor names it**, as `#<slug>` or
  a problem's id prefix. A reload or a pasted link opens the same dialog, so
  the pages link to each other's items: a lesson to its questions, a card to
  its rungs.
- **`j` and `k` open the next and the previous row in the dialog, and the
  dialog's head reads the position, such as `5 of 133`.** Two buttons in the
  head step the same way. A review then reads each row in turn without a
  pointer.
- **Escape, the close button or a press outside closes the dialog**, and
  clears the anchor. The grid then marks the row last opened, so the author
  resumes the scan from it.
