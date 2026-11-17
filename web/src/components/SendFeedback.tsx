import { MessageSquare } from 'lucide-react'
import { useState } from 'react'
import { useLocation } from 'react-router'

import {
  CANCEL,
  FEEDBACK_EXPLAINED,
  FEEDBACK_LABEL,
  FEEDBACK_SEND,
  FEEDBACK_SENT,
  FEEDBACK_TITLE,
  SEND_FEEDBACK,
  sendableNote,
  sendFeedback,
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
import { Textarea } from '@/components/ui/textarea'

// a note the author reads with `climb feedback`: `log.md`, Feedback
export function SendFeedback() {
  const page = useLocation().pathname
  const [open, setOpen] = useState(false)
  const [note, setNote] = useState('')
  const [sending, setSending] = useState(false)
  const [refused, setRefused] = useState<string | null>(null)
  const [sent, setSent] = useState(false)

  async function send() {
    setSending(true)
    const outcome = await sendFeedback(api, 'web', page, note)
    setSending(false)
    if (!outcome.ok) return setRefused(outcome.refused)
    setOpen(false)
    setNote('')
    setSent(true)
  }

  return (
    <Dialog
      open={open}
      onOpenChange={(next) => {
        setOpen(next)
        setRefused(null)
        if (next) setSent(false)
      }}
    >
      <div className="flex items-center gap-stack">
        <Button variant="outline" onClick={() => setOpen(true)}>
          <MessageSquare />
          {SEND_FEEDBACK}
        </Button>
        {sent && <p className="text-meta text-muted-foreground">{FEEDBACK_SENT}</p>}
      </div>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{FEEDBACK_TITLE}</DialogTitle>
          <DialogDescription>{FEEDBACK_EXPLAINED}</DialogDescription>
        </DialogHeader>
        <div className="space-y-1">
          <Label htmlFor="feedback-note">{FEEDBACK_LABEL}</Label>
          <Textarea
            id="feedback-note"
            rows={5}
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
            {FEEDBACK_SEND}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
