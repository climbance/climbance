# API

Python and FastAPI. It answers JSON under `/api`, serves the web app's files,
signs users in and records the log. A file beside this one gives each
component.

## One origin

The web app is served from one origin. The API answers JSON under `/api`, and
the frontend is built to static files. Locally, Vite serves the files and
proxies `/api` to the API. Deployed, the API serves the built files beside
`/api`, and Caddy in front of the API holds the certificate.

- **A second origin is rejected.** Every request would need CORS, and the
  session cookie would have to cross domains.
- **A path naming no file is answered with `index.html`.** The frontend routes
  its pages by URL, so a reload of any page reaches the app rather than a 404.
  A path under `/api` naming no route stays a 404.

## Writes

- **A write is refused unless it is sent as JSON, and the pages send every
  request as JSON.** A form on another site cannot send JSON, and JSON from
  another origin needs a preflight the API never answers. So the session cookie
  carries no write another site forged.

## Client error reports

- **Each client reports an error it did not handle, and the API writes the
  report as one line of its log.** The report names the user, the client, the
  build, the page and the error's message and stack, and no code the user
  typed. A table is rejected, since the log already keeps 14 days and the
  privacy policy already states them.
- **A client sends each distinct error once per load, and the API refuses a
  user's reports past 10 a minute.** A render failing in a loop would otherwise
  fill the log. The API counts the reports in memory, per worker, since a
  report is no stored record.
