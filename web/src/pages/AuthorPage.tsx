import { AUTHOR_NONE, AUTHOR_TITLE, BACK_BOARD, OF } from '@climb/core'
import { Link } from 'react-router'

import { api } from '@/api/client'
import { useLoaded } from '@/api/useLoaded'
import { Loaded } from '@/components/Loaded'
import { PageHeader } from '@/components/PageHeader'
import { NotFoundPage } from '@/pages/NotFoundPage'

// the author area's index: `web-app/pages/author/README.md`. The API's 403
// guards it; a learner reads the not-found page rather than a refusal
export function AuthorPage() {
  const me = useLoaded((signal) => api.GET('/api/me', { signal }), 'me')
  const area = useLoaded((signal) => api.GET('/api/author', { signal }), 'author')
  if (me.data && !me.data.author) return <NotFoundPage />
  // held at loading until the session is read, so a learner never sees the refusal
  const pages = me.data
    ? { ...area, data: area.data?.pages }
    : { retry: me.retry, error: me.error, data: undefined }

  return (
    <section className="space-y-section">
      <PageHeader back={{ to: '/', label: BACK_BOARD }} title={AUTHOR_TITLE} />
      <Loaded of={OF.author} state={pages} blank={AUTHOR_NONE}>
        {(pages) => (
          <ul className="space-y-stack">
            {pages.map((page) => (
              <li key={page}>
                <Link to={`/author/${page}`}>{page}</Link>
              </li>
            ))}
          </ul>
        )}
      </Loaded>
    </section>
  )
}
