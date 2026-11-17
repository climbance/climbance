import { Flag } from 'lucide-react'
import { useState } from 'react'

import {
  CANCEL,
  REPORT_EXPLAINED,
  REPORT_NOTE_LABEL,
  REPORT_PROBLEM,
  REPORT_REASONS,
  REPORT_SEND,
  REPORT_SENT,
  REPORT_TITLE,
  requestRetirement,
  sendableNote,
  type RetirementReason,
} from '@climb/core'

import { api } from '@/api/client'
import { ErrorLine } from '@/components/ErrorLine'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Textarea } from '@/components/ui/textarea'

// a request the author reads before retiring the problem by hand: `corpus.md`, Problems
export function ReportProblem({ problemId }: { problemId: string }) {
  const [open, setOpen] = useState(false)
  const [reason, setReason] = useState<RetirementReason>('defective')
  const [note, setNote] = useState('')
  const [sending, setSending] = useState(false)
  const [refused, setRefused] = useState<string | null>(null)
  const [sent, setSent] = useState(false)

  async function send() {
    setSending(true)
    const outcome = await requestRetirement(api, problemId, reason, note)
    setSending(false)
    if (!outcome.ok) return setRefused(outcome.refused)
    setOpen(false)
    setSent(true)
  }

  if (sent) return <p className="text-meta text-muted-foreground">{REPORT_SENT}</p>
  return (
    <Dialog
      open={open}
      onOpenChange={(next) => {
        setOpen(next)
        setRefused(null)
      }}
    >
      <Button
        variant="link"
        size="sm"
        className="px-0 text-muted-foreground"
        onClick={() => setOpen(true)}
      >
        <Flag />
        {REPORT_PROBLEM}
      </Button>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{REPORT_TITLE}</DialogTitle>
          <DialogDescription>{REPORT_EXPLAINED}</DialogDescription>
        </DialogHeader>
        <RadioGroup value={reason} onValueChange={(value) => setReason(value as RetirementReason)}>
          {REPORT_REASONS.map((one) => (
            <div key={one.value} className="flex items-center gap-2">
              <RadioGroupItem id={`reason-${one.value}`} value={one.value} />
              <Label htmlFor={`reason-${one.value}`}>{one.label}</Label>
            </div>
          ))}
        </RadioGroup>
        <div className="space-y-1">
          <Label htmlFor="report-note">{REPORT_NOTE_LABEL}</Label>
          <Textarea
            id="report-note"
            rows={4}
            value={note}
            onChange={(event) => setNote(event.target.value)}
          />
        </div>
        {refused && <ErrorLine>{refused}</ErrorLine>}
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline">{CANCEL}</Button>
          </DialogClose>
          <Button disabled={!sendableNote(note) || sending} onClick={() => void send()}>
            {REPORT_SEND}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
