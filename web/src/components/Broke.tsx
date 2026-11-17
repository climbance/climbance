import { Component, type ReactNode } from 'react'
import { useLocation } from 'react-router'

import { BROKE_EXPLAINED, BROKE_TITLE, RELOAD } from '@climb/core'

import { PageHeader } from '@/components/PageHeader'
import { SendFeedback } from '@/components/SendFeedback'
import { Button } from '@/components/ui/button'
import { reported } from '@/lib/reported'

// a render that threw unmounts the whole tree, which leaves a blank page
export function Broke({ children }: { children: ReactNode }) {
  return <Boundary page={useLocation().pathname}>{children}</Boundary>
}

type Props = { children: ReactNode; page: string }
// the page that threw: leaving it through the navigation renders again
type State = { brokeAt: string | null }

class Boundary extends Component<Props, State> {
  state: State = { brokeAt: null }

  static getDerivedStateFromError() {
    return { brokeAt: '' }
  }

  static getDerivedStateFromProps(props: Props, state: State) {
    if (state.brokeAt === '') return { brokeAt: props.page }
    return state.brokeAt !== null && state.brokeAt !== props.page ? { brokeAt: null } : null
  }

  componentDidCatch(error: unknown) {
    reported(error)
  }

  render() {
    if (this.state.brokeAt === null) return this.props.children
    return (
      <section className="space-y-stack">
        <PageHeader title={BROKE_TITLE} note={BROKE_EXPLAINED} />
        <div className="flex flex-wrap items-center gap-stack">
          <Button onClick={() => window.location.reload()}>{RELOAD}</Button>
          {/* the page that broke, which the note can say how it was reached */}
          <SendFeedback />
        </div>
      </section>
    )
  }
}
