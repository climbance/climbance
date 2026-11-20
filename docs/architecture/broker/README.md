# Broker

A submission runs in a container the broker starts, and the API reaches no
container runtime. The image, the flags and the limits are fixed in the
broker's source. No field of a request names an image, a mount or a capability.

## Holding the socket

- **An API holding the container runtime's socket would turn its own compromise
  into a root shell on the server.** A request to that socket can start a
  privileged container with the host's filesystem mounted into it, and the API
  is the process running whatever a signed-in person submits.
- **The broker starts a container with the docker CLI, and the fixed flags are
  one argument list in the broker's source.** The request reaches the entry
  process on standard input through `docker run -i`. Docker's HTTP API needs a
  hijacked connection to write a container's standard input, and the Docker SDK
  for Python is untyped.
- **The broker names the submission's image by digest, and pulls that image
  when it starts.** A tag moves under the run a stored verdict was measured by.
  The host's daemon carries out the pull on the broker's behalf, since the
  broker's own network leads nowhere outside.
- **The broker runs from the engine's image, under a command of its own.** An
  import contract keeps the broker's module from importing the rest of the
  package, so the process holding the socket loads no engine code. A second
  image would add a second digest to every deploy.
- **The broker runs as a non-root user in the host's `docker` group.** That
  group already controls the host through the socket, so running the broker as
  root would add only write access inside the broker's own container. The
  group's id differs between servers, so the server writes it into the secrets
  file and compose reads it from there.
- **The API reaches the broker over HTTP, on a compose network that only the
  API and the broker join.** Caddy and Postgres cannot open a connection to the
  broker. A shared token was rejected, since the separate network guards the
  broker with no secret to rotate.
- **A submission runs in the local subprocess wherever no broker is
  configured.** gVisor runs only on Linux, so a sitting on the author's laptop
  uses the subprocess. The broker's own tests run where Docker and gVisor are
  installed.

## Admitting a run

- **Submissions run one at a time, and the broker admits them.** A verdict is
  wall clock against the cap, so a submission running beside another measures
  the contention between them. The broker is one process, so the limit holds
  however many API workers there are, where a limit inside the API would hold
  only within one worker.
- **A submission waiting for the broker is refused once the wait passes a
  bound.** A submission that waits without a bound looks to the user like a
  sandbox that hung. The wait changes no verdict, since the cap is measured in
  the child around the `solve` call.
- **Several submissions run at once only where each run holds a core of its
  own.** Two runs sharing a core measure each other, and two runs on separate
  cores share memory bandwidth alone. A longer queue admits more submissions
  without changing what either one measures.
