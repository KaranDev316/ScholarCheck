import { formatDeadline } from '../data/format'
import type { ScholarshipDeadline } from '../data/types'

interface DeadlineRowProps {
  deadline?: ScholarshipDeadline | null
  now?: Date
}

export function DeadlineRow({ deadline, now }: DeadlineRowProps) {
  const formatted = formatDeadline(deadline, now)

  return (
    <div className="deadline-row">
      <div className="deadline-head">
        <span className="deadline-label">Deadline</span>
        {formatted.text ? <span className="deadline-value">{formatted.text}</span> : null}
        <span className={`chip deadline-badge deadline-${formatted.badgeTone}`}>
          {formatted.badgeLabel}
        </span>
      </div>
      {formatted.note ? <div className="small mute deadline-note">{formatted.note}</div> : null}
    </div>
  )
}
