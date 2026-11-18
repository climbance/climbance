# Knowledge log

Nine append-only tables hold the user's knowledge log, one per kind of event.
Each is private to the user, and each refuses an update and a delete by a
trigger, as `../README.md` requires.

## Every record

- **Every record carries the same base**: an engine-minted `id`, a
  `client_id`, the `user_id`, the `device` that wrote it, the moment the user
  acted, and `created_at`.
- **The client mints `client_id`, and a user's ids are unique.** A retried
  upload then writes nothing twice. A client works offline, so a record can
  reach the server long after the user acted.
- **The schedule reads the moment the user acted, never `created_at`.** A
  record uploaded a day late was still answered when the user answered it.
- **The content tables are refreshed by the seed.** Their columns follow the
  authoring format and may change with a migration. The nine tables above are
  the part that cannot.

## The nine tables

- **`answers`**: the question, whether the reply was correct, the guess flag,
  and for an open question the grade, the points missed, the traps fallen
  into and the wrong flag. A test answer also names its measure, `baseline`
  or `delayed`.
- **`stints`**: the mode, the score, the number of questions answered, and
  for an exam the level it was taken at. A certification's exam also names
  the certification, by its wire id. A `baseline` or `delayed` stint names
  its module, its topic and its level.
- **`module_status_changes`**: the module and its status.
- **`focuses`**: the module, the topic, the subtopic and the certification,
  each optional, and whether the focus is strict.
- **`lesson_marks`**: the lesson, and whether it was read or reset.
- **`certification_exams`**: the certification, the score, the number of
  questions and whether the exam passed.
- **`setting_changes`**: the setting's name and its new value.
- **`limit_raises`**: how many new questions the raise adds to today's limit.
- **`module_orders`**: the modules, first to last.
- **A certification is referenced by its module, its topic and its level.** A
  certification is derived rather than stored, so no table holds it, and the
  three minted parts name it.
