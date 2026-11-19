import { TagChip } from './Chips'
import { DeadlineRow } from './DeadlineRow'
import { fundingTypeFor } from '../data/funding'
import { formatAward, formatDate, formatScholarshipSummary } from '../data/format'
import type { Scholarship } from '../data/types'
import { scholarshipHref } from '../routing/routes'

interface ScholarshipCardProps {
  record: Scholarship
  isDevelopment: boolean
}

export function ScholarshipCard({ record, isDevelopment }: ScholarshipCardProps) {
  const fundingType = fundingTypeFor(record.coverage)
  const href = scholarshipHref(record.id)
  const award = record.headline
    ? formatAward(
        record.headline.amount,
        record.headline.currency !== undefined ? record.headline.currency : record.currency,
        record.headline.basis,
      )
    : null
  const summary = formatScholarshipSummary(record)

  return (
    <article className="card">
      {fundingType === 'Fully funded' ? (
        <div>
          <span className="chip ff">Fully funded</span>{' '}
          <span className="small mute">Tuition, living costs and flights covered</span>
        </div>
      ) : null}

      <div className="meta">
        {record.provider}, {record.country}
      </div>
      <h3>
        <a href={href}>{record.title}</a>
      </h3>
      <p className="mute">{summary}</p>

      <div className="tags">
        {record.levels.map((level) => (
          <TagChip key={level}>{level}</TagChip>
        ))}
        <TagChip>{fundingType ?? 'Funding type not established'}</TagChip>
        <TagChip>{record.country}</TagChip>
        {record.tags.map((tag) => (
          <TagChip key={tag}>{tag}</TagChip>
        ))}
        {isDevelopment ? <span className="chip unspec">Development preview</span> : null}
      </div>

      <div className="foot">
        <div>
          {award ? (
            <>
              <div className="amt">{award.amountText}</div>
              <div className="mute small">
                {[record.headline?.component, award.qualifierText].filter(Boolean).join(' · ')}
              </div>
              {award.currencyNote ? (
                <div className="mute small award-note">{award.currencyNote}</div>
              ) : null}
            </>
          ) : (
            <div className="ph">Amount not stated in the source</div>
          )}
          <DeadlineRow deadline={record.deadline} />
          <div className="small mute checkedline">
            {record.sourceCheck
              ? `Source checked ${formatDate(record.sourceCheck.checkedAt)}`
              : 'Not source checked yet'}
          </div>
        </div>
        <a className="btn alt sm" href={href}>
          See scholarship details
        </a>
      </div>
    </article>
  )
}
