# Sandbox

The container a submission runs in, started by the broker for one run. The run
has no network, a read-only root filesystem, a non-root user and dropped
capabilities. Limits on memory, processes and time hold it.

## One run, a child per case

- **One container holds a whole run, and the entry process forks a child per
  case inside it.** No case observes another, as `../api/runner.md` requires. A
  container per case would pay a container's start once per case, where a fork
  costs far less.
- **The submission's image carries a Python interpreter and no engine code.**
  The broker sends the entry process's script with each run, as `python -c`, so
  the script always matches the deployed broker. The submitted code arrives on
  standard input, so a run mounts nothing.
- **Each case's child points its standard streams at `/dev/null` and returns
  its result to the entry process over a pipe.** The entry process prints one
  line per case on standard output. A solution's own prints therefore never
  reach the output the broker parses.
- **Each case's child holds an address-space limit under the container's memory
  limit, so a case that exhausts memory raises inside that child and fails
  alone.** Under the container's limit alone the host kills the whole
  container, which leaves every later case of the run unanswered.
- **Each case's child holds a process limit under the container's, for the same
  reason.** gVisor backs every process a case starts with a host process, so a
  case reaching the container's limit ends the sandbox itself. The process
  limit counts every process of a user, so the entry process sets it only where
  the broker marks the container as the run's alone.
- **gVisor mounts a tmpfs over `/tmp` inside the container, so a solution
  writes there however read-only the root filesystem is.** That tmpfs is
  removed with the container, and what it holds counts against the container's
  memory limit.
- **A run's container holds one CPU.** A container with no CPU limit takes
  every core it can, which slows the API and Postgres beside it. A `solve` call
  is single-threaded, so the limit takes nothing a solution uses, and gVisor's
  own threads share the same quota.

## gVisor

- **The container runs under gVisor, a kernel written in user space that
  answers the container's system calls.** An exploit of the host's own kernel
  reaches gVisor first. The broker names the runtime as a constant.
- **gVisor answers a system call more slowly than the host's kernel does, and a
  verdict is wall clock against the cap.** So the canonicals are timed under
  gVisor, and a separating size found on the local subprocess is measured again
  there. Installing gVisor after that measurement would spend it twice. Under
  gVisor at the sitting's cap, the 50 served problems' canonicals ran all 506
  of their cases, and none took over a tenth of the cap.
- **A virtual machine per submission is deferred until access is opened beyond
  invitations.** gVisor's KVM platform needs `/dev/kvm`, which this server does
  not offer, so the step is a microVM service rather than a flag.
- **The sandbox moves to a server of its own at the same point.** An escape
  then crosses a network before it reaches Postgres.
