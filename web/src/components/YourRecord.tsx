import { Download, Trash2 } from 'lucide-react'
import { useState } from 'react'

import {
  confirmsDeletion,
  DELETE_ACCOUNT,
  DELETE_ACCOUNT_TITLE,
  deleteAccount,
  deleteAccountWarning,
  EXPORT_NOTE,
  EXPORT_RECORD,
  exportedRecord,
  KEEP_ACCOUNT,
  named,
  RECORD_FILE,
  YOUR_RECORD,
} from '@climb/core'

import { api, type Me } from '@/api/client'
import { ErrorLine } from '@/components/ErrorLine'
import { Panel } from '@/components/Panel'
import { SectionHeading } from '@/components/SectionHeading'
import {
  AlertDialog,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useKnowledge } from '@/knowledge/context'

// the record exported as a file, and the account deleted with it: `concepts/log-records.md`
export function YourRecord({ me }: { me: Me | undefined }) {
  const { leave } = useKnowledge()
  const [failed, setFailed] = useState<string | null>(null)
  const [asking, setAsking] = useState(false)
  const [typed, setTyped] = useState('')
  const [deleting, setDeleting] = useState(false)

  async function exported() {
    setFailed(null)
    const record = await exportedRecord(api)
    if (!record.ok) return setFailed(record.refused)
    const url = URL.createObjectURL(new Blob([record.value], { type: 'application/json' }))
    const link = Object.assign(document.createElement('a'), { href: url, download: RECORD_FILE })
    link.click()
    URL.revokeObjectURL(url)
  }

  async function deleted() {
    setDeleting(true)
    const gone = await deleteAccount(api, typed)
    setDeleting(false)
    if (!gone.ok) {
      setAsking(false)
      return setFailed(gone.refused)
    }
    // forced: the outbox belongs to a log that no longer exists
    await leave(true)
  }

  return (
    <section className="space-y-stack">
      <SectionHeading title={YOUR_RECORD} />
      <Panel>
        <div className="flex flex-wrap items-center gap-stack">
          <p className="flex-1 text-meta text-muted-foreground">{EXPORT_NOTE}</p>
          <Button variant="outline" onClick={() => void exported()}>
            <Download />
            {EXPORT_RECORD}
          </Button>
          <Button
            variant="outline"
            disabled={!me}
            onClick={() => {
              setTyped('')
              setAsking(true)
            }}
          >
            <Trash2 />
            {DELETE_ACCOUNT}
          </Button>
        </div>
        {failed && <ErrorLine>{failed}</ErrorLine>}
      </Panel>
      <AlertDialog open={asking} onOpenChange={setAsking}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>{DELETE_ACCOUNT_TITLE}</AlertDialogTitle>
            <AlertDialogDescription>{deleteAccountWarning(named(me))}</AlertDialogDescription>
          </AlertDialogHeader>
          <Input
            aria-label={DELETE_ACCOUNT}
            autoComplete="off"
            value={typed}
            onChange={(event) => setTyped(event.target.value)}
          />
          <AlertDialogFooter>
            <AlertDialogCancel>{KEEP_ACCOUNT}</AlertDialogCancel>
            <Button
              variant="destructive"
              disabled={!confirmsDeletion(typed, me) || deleting}
              onClick={() => void deleted()}
            >
              <Trash2 />
              {DELETE_ACCOUNT}
            </Button>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </section>
  )
}
