# Execution terms

Words this project gives its own meaning for running a submission. Every file
in `docs/architecture/` uses them without redefining them.

- **Sandbox**: what a submission runs under: a container with no network, a
  read-only root filesystem, a non-root user, dropped capabilities and limits
  on memory, processes and time. It shares the server's kernel.
- **Broker**: the process holding the container runtime's socket and starting
  one container per run. It answers one request, carrying the code, the
  arguments and the cap. Every other option a container is started with is
  fixed in the broker's own source.
- **Entry process**: the first process in a run's container. It reads the run
  from standard input, forks a child per case, and prints each case's result as
  one line on standard output.
