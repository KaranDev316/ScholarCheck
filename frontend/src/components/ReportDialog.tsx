import { useEffect, useRef, useState } from 'react'
import type { FormEvent, KeyboardEvent } from 'react'

interface ReportDialogProps {
  scholarshipTitle: string
  open: boolean
  onClose: () => void
  onSend: (reason: string, details: string) => Promise<void> | void
}

const FOCUSABLE_SELECTOR =
  'select:not(:disabled), textarea:not(:disabled), input:not(:disabled), button:not(:disabled), a[href], [tabindex]:not([tabindex="-1"])'

/** Submit a problem report; preserve user input when delivery fails. */
export function ReportDialog({ scholarshipTitle, open, onClose, onSend }: ReportDialogProps) {
  const [sending, setSending] = useState(false)
  const [error, setError] = useState('')
  const dialogRef = useRef<HTMLDialogElement>(null)
  const triggerRef = useRef<HTMLElement | null>(null)
  const wasOpenRef = useRef(false)

  useEffect(() => {
    const dialog = dialogRef.current
    if (!dialog) return

    if (open) {
      if (!wasOpenRef.current) {
        triggerRef.current =
          document.activeElement instanceof HTMLElement ? document.activeElement : null
      }
      wasOpenRef.current = true

      if (typeof dialog.showModal === 'function' && !dialog.open) {
        dialog.showModal()
      } else if (!dialog.open) {
        dialog.setAttribute('open', '')
      }

      const firstFocusable = dialog.querySelector<HTMLElement>(FOCUSABLE_SELECTOR)
      firstFocusable?.focus()
      return
    }

    if (dialog.open && typeof dialog.close === 'function') {
      dialog.close()
    } else {
      dialog.removeAttribute('open')
    }

    if (wasOpenRef.current) {
      wasOpenRef.current = false
      triggerRef.current?.focus()
    }
  }, [open])

  function handleKeyDown(event: KeyboardEvent<HTMLDialogElement>) {
    if (event.key === 'Escape') {
      event.preventDefault()
      onClose()
      return
    }

    if (event.key !== 'Tab') return
    const dialog = dialogRef.current
    if (!dialog) return

    const focusable = Array.from(dialog.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR))
    if (focusable.length === 0) return

    const first = focusable[0]
    const last = focusable[focusable.length - 1]
    const active = document.activeElement

    if (event.shiftKey) {
      if (active === first || !dialog.contains(active)) {
        event.preventDefault()
        last.focus()
      }
    } else if (active === last || !dialog.contains(active)) {
      event.preventDefault()
      first.focus()
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const form = event.currentTarget
    const data = new FormData(form)
    setSending(true)
    setError('')
    try {
      await onSend(String(data.get('reason')), String(data.get('details') ?? ''))
      form.reset()
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Could not send your report. Please try again.',
      )
    } finally {
      setSending(false)
    }
  }

  return (
    <dialog
      ref={dialogRef}
      aria-labelledby="report-heading"
      onClose={onClose}
      onKeyDown={handleKeyDown}
    >
      <form onSubmit={handleSubmit}>
        <h3 id="report-heading">Report a problem</h3>
        <p className="small muted">About: {scholarshipTitle}</p>

        <label className="rl">
          What looks wrong?
          <select name="reason" defaultValue="The amount">
            <option>The amount</option>
            <option>A deadline or round</option>
            <option>Eligibility</option>
            <option>A link doesn’t work</option>
            <option>Something else</option>
          </select>
        </label>

        <label className="rl">
          Details (optional)
          <textarea name="details" rows={4} maxLength={2000} />
        </label>

        {error ? (
          <p className="state-error" role="alert">
            {error}
          </p>
        ) : null}
        <div className="actionrow dialogactions">
          <button className="btn btn-primary" type="submit" disabled={sending}>
            {sending ? 'Sending…' : 'Send report'}
          </button>
          <button className="btn btn-secondary alt" type="button" onClick={onClose}>
            Cancel
          </button>
        </div>

        <p className="small muted">We don’t ask for your name or email.</p>
      </form>
    </dialog>
  )
}
