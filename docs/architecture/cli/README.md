# Command line

`climb`, run by the author off the server. It holds generation, the by-hand
passes, seeding, invitations and difficulty fits.

## Generation is a command

Content generation is a command of the engine, beside the classifier and the
matcher, and it writes the problems, their test cases and their solutions. The
command reuses one transport, one call log and one provenance base, rather than
standing a second copy of each somewhere else.

- **Extraction to a pipeline of its own stays possible and is not planned.**
  Such a pipeline would have to preserve the minted ids, since the attempt log
  references them.
- **Generation runs off the engine's server.** The mutation loop starts many
  subprocesses at a cap well above the sitting's, so a generation run beside a
  sitting moves the wall clock that sitting's verdict is read from. Generation
  writes the corpus rather than serving a page, so it runs wherever the author
  is.
