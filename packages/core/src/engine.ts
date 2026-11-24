import createClient, { type Client } from 'openapi-fetch';

import type { paths } from './api/schema';

export type EngineClient = Client<paths>;

export interface EngineOptions {
  // the app's bearer token; the pages send a session cookie instead: `api/app-tokens.md`
  token?: () => string | null | undefined | Promise<string | null | undefined>;
  // a request refused for want of a session or a token
  signedOut?: (response: Response) => void;
  fetch?: (request: Request) => Promise<Response>;
}

export function engineClient(baseUrl: string, options: EngineOptions = {}): EngineClient {
  // every request says JSON, since the API refuses a write that does not, and
  // a write with no body would otherwise send no content type
  const client = createClient<paths>({
    baseUrl,
    headers: { 'Content-Type': 'application/json' },
    ...(options.fetch ? { fetch: options.fetch } : {}),
  });
  client.use({
    async onRequest({ request }) {
      const token = await options.token?.();
      if (token) request.headers.set('Authorization', `Bearer ${token}`);
      return request;
    },
    async onResponse({ response }) {
      if (response.status === 401) options.signedOut?.(response);
      // a proxy's 502 comes with no body, which openapi-fetch reads as neither
      // data nor error, so a caller took the refusal as done
      if (response.status >= 400 && (await response.clone().text()) === '') {
        return new Response(JSON.stringify({ detail: unanswered(response.status) }), {
          status: response.status,
          statusText: response.statusText,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      return undefined;
    },
  });
  return client;
}

type Get<P extends GetPath> = paths[P]['get'];

export type GetPath = { [P in keyof paths]: paths[P] extends { get: object } ? P : never }[keyof paths];

export type GetData<P extends GetPath> =
  Get<P> extends { responses: { 200: { content: { 'application/json': infer T } } } } ? T : never;

export type GetParams<P extends GetPath> = Get<P> extends { parameters: { path: infer Q } } ? Q : never;

export const unanswered = (status: number) => `the engine answered ${status} with no reason; try again`;

export function described(error: unknown): string {
  // the API refuses with the domain's own sentence
  if (error && typeof error === 'object' && 'detail' in error && error.detail != null) return String(error.detail);
  if (error instanceof Error) return error.message;
  if (typeof error === 'string') return error;
  return JSON.stringify(error) ?? String(error);
}
