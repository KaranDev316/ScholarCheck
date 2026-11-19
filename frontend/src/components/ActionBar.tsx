import { applicationAction } from '../data/application'
import { isOpenRound, passedRoundDates } from '../data/funding'
import type { Scholarship } from '../data/types'

interface ActionBarProps {
  record: Scholarship
  isDevelopment: boolean
}

export function ActionBar({ record, isDevelopment }: ActionBarProps) {
  const passed = passedRoundDates(record)
  const datesPassed = passed.length > 0
  const applyAction = applicationAction(record)
  const upcomingRound = record.rounds.find((round) => isOpenRound(round))
  const hasDistinctApply = Boolean(
    applyAction && applyAction.href !== record.links.requirements,
  )

  const dateNote = datesPassed
    ? upcomingRound
      ? `The ${passed.join('; ')} deadline has passed. Another round has a published deadline; confirm it with the provider before applying.`
      : `The published dates (${passed.join('; ')}) have passed, and the next round isn’t published yet.`
    : record.application.note

  const applyLabel =
    record.application.kind === 'none'
      ? 'Apply for admission'
      : "Apply on the provider's site"

  return (
    <div className="actions action-bar-sticky">
      {isDevelopment ? (
        <p className="small note warn">
          Development preview. This record is not published and has not passed the automated
          source check.
        </p>
      ) : null}
      {dateNote ? <p className="small note warn">{dateNote}</p> : null}

      <div className="actionpair">
        <div className="act">
          <a
            className={
              hasDistinctApply && applyAction?.emphasised
                ? 'btn btn-secondary alt'
                : 'btn btn-primary'
            }
            href={record.links.requirements}
            target="_blank"
            rel="noreferrer"
          >
            Read the requirements
          </a>
          <p className="small muted">
            What the official page says about eligibility and funding.
          </p>
        </div>
        {hasDistinctApply && applyAction ? (
          <div className="act">
            <a
              className={
                applyAction.emphasised ? 'btn btn-primary' : 'btn btn-secondary alt'
              }
              href={applyAction.href}
              target="_blank"
              rel="noreferrer"
            >
              {applyLabel}
            </a>
            <p className="small muted">{applyAction.note}</p>
          </div>
        ) : null}
      </div>
    </div>
  )
}
