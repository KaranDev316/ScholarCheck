import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'

interface ReportDialogProps {
  scholarshipTitle: string
  open: boolean
  onClose: () => void
  onSend: (reason: string, details: string) => Promise<void> | void
}

/** Submit a problem report; preserve user input when delivery fails. */
export function ReportDialog({ scholarshipTitle, open, onClose, onSend }: ReportDialogProps) {
  const [sending, setSending] = useState(false)
  const [error, setError] = useState('')
  const dialogRef = useRef<HTMLDialogElement>(null)

  useEffect(() => {
    const dialog = dialogRef.current
    if (!dialog) return

    if (open) {
      if (typeof dialog.showModal === 'function' && !dialog.open) {
        dialog.showModal()
      } else if (!dialog.open) {
        dialog.setAttribute('open', '')
      }
      return
    }

    if (dialog.open && typeof dialog.close === 'function') {
      dialog.close()
    } else {
      dialog.removeAttribute('open')
    }
  }, [open])

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
      setError(err instanceof Error ? err.message : 'Could not send your report. Please try again.')
    } finally { setSending(false) }
  }

  return (
    <dialog ref={dialogRef} aria-labelledby="report-heading" onClose={onClose}>
      <form onSubmit={handleSubmit}>
        <h3 id="report-heading">Report a problem</h3>
        <p className="small mute">About: {scholarshipTitle}</p>

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

        {error ? <p role="alert">{error}</p> : null}
        <div className="actionrow dialogactions">
          <button className="btn" type="submit" disabled={sending}>
            {sending ? 'Sending…' : 'Send report'}
          </button>
          <button className="btn alt" type="button" onClick={onClose}>
            Cancel
          </button>
        </div>

        <p className="small mute">We don’t ask for your name or email.</p>
      </form>
    </dialog>
  )
}
