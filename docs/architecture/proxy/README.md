# Caddy

The proxy in front of the API. `../api/README.md` gives why the web app is
served from one origin.

- **Caddy terminates TLS and passes every request to the API.** Caddy issues
  and renews the certificate itself, so no certificate is handled by hand.
- **Caddy serving the files itself is rejected.** The files are built into the
  engine's image, and Caddy could reach them only through a second image the
  deploy also pushes, or a volume the API fills at start and a rollback leaves
  stale.
- **Caddy keeps its certificates on a volume.** Without the volume a redeploy
  issues a certificate again, and the certificate authority limits how often it
  issues one.
