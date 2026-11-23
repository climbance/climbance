import { lazy } from 'react'
import { useParams } from 'react-router'

// the editor is the bulk of the bundle, as on the problem's page
const ColdSittingView = lazy(() =>
  import('@/components/ColdSittingView').then((m) => ({ default: m.ColdSittingView })),
)

// the path names the sitting, so a reload reads it, running or ended:
// `web-app/pages/practice/cold/`
export function ColdPage() {
  const { sittingId = '' } = useParams()
  return <ColdSittingView key={sittingId} sittingId={sittingId} />
}
