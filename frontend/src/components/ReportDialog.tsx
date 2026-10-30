import { useEffect, useRef } from 'react'
import type { FormEvent } from 'react'

interface ReportDialogProps {
  scholarshipTitle: string
  open: boolean
  onClose: () => void
  onSend: () => void
}

/**
 * Report dialog. The feedback endpoint does not exist yet, so sending only
 * closes the dialog and tells the visitor the report was not sent — it never
 * pretends a report was received.
 */
export function ReportDialog({ scholarshipTitle, open, onClose, onSend }: ReportDialogProps) {
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

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    event.currentTarget.reset()
    onSend()
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
          <textarea name="details" rows={4} />
        </label>

        <div className="actionrow dialogactions">
          <button className="btn" type="submit">
            Send report
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
