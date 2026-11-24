# Deployment

The engine runs on one virtual server, and Docker Compose starts its
containers. The API, the frontend's files, Postgres and the sandbox share that
server. A host running only functions is rejected, since a submission needs a
container runtime. This file gives the shape the engine depends on: one server,
what shares it, and what a failure costs. The provider, the sizes and the
commands that build the server are in the deployment repo.

## The server

- **Postgres writes to storage that outlives the server.** A lost server is
  replaced by creating another and attaching that storage again, so losing the
  server costs the time a rebuild takes rather than the log.
- **The database is dumped on a schedule, and the dump is copied off the
  server.** A dump left on the same storage as the database is lost with it.
- **A second daily timer deletes the accounts unused for a year**, by running
  `climb log prune` in the API's container. `../api/sign-in.md` gives the rule
  it applies.
- **Every service logs to the host's journal, which keeps 14 days.** Docker's
  default log driver keeps every line until the disk fills. The privacy policy
  states the 14 days, and the deployment repo sets the journal's retention.
- **One server carries no failover, and that is accepted.** A second server
  carries a second Postgres, which needs replication, automatic failover and a
  rule stopping both servers from accepting writes at once. The failures this
  size of deployment meets are a bad deploy, a full disk and a submission
  eating the memory, and a second server answers none of them.
- **The server, the volume, the firewall and the commands that rebuild them
  live in a private repo of their own.** This repo is read as public, and the
  server's address is not.

## Deploying an image

- **The image carries the compose file it is deployed with, at
  `/app/deploy/compose.yaml`, and the server extracts that file from the image
  it pulled.** The server clones no repository and holds no credential reading
  one, and deploying an older image restores the service definitions that image
  was built with.
- **A push to main builds the image, pushes it to the registry, and sends the
  server one command naming that image by digest.** The key that command
  arrives on carries a forced command, so a holder of the key deploys an image
  and runs nothing else.
- **Secrets reach the server as a file the server alone holds.** Whoever can
  pull an image can read what was built into it, so a secret is never built in.

## Reaching the store

- **Postgres listens on the server's loopback address, and a command run off
  the server reaches it through an SSH tunnel.** The generation commands write
  to the store from wherever the author runs them, and the tunnel gives them
  the store over the port that is already open.
- **Opening the database's port to the author's address is rejected.** An open
  port is reachable from outside the server, and a password guards it. The
  tunnel is guarded by a key instead, and it opens no further port.
