import { termsOfUse, lastUpdated, BACK_SIGN_IN } from '@climb/core'

import { LOGIN } from '@/api/client'
import { Markdown } from '@/components/Markdown'
import { PageHeader } from '@/components/PageHeader'

const TERMS = termsOfUse()

export function TermsPage() {
  return (
    <article className="space-y-section">
      {/* the login is the page this one is reached from, so it is the way
          back. No section: the page opens with no session */}
      <PageHeader
        back={{ to: LOGIN, label: BACK_SIGN_IN }}
        title={TERMS.title}
        note={TERMS.updated && lastUpdated(TERMS.updated)}
      />
      <Markdown>{TERMS.body}</Markdown>
    </article>
  )
}
