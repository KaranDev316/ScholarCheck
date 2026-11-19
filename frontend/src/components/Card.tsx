import { formatAward, formatComponentLabel, formatDate } from '../data/format'
import { fundingTypeFor } from '../data/funding'
import type { Scholarship } from '../data/types'
import { scholarshipHref } from '../routing/routes'
import { TagChip } from './Chips'
import { UnknownBadge } from './UnknownBadge'

export interface CardProps {
  record: Scholarship
  isDevelopment: boolean
}

export function Card({ record, isDevelopment }: CardProps) {
  const fundingType = fundingTypeFor(record.coverage)
  const href = scholarshipHref(record.id)
  const award = record.headline
    ? formatAward(
        record.headline.amount,
        record.headline.currency !== undefined ? record.headline.currency : record.currency,
        record.headline.basis,
      )
    : null
  const componentLabel = record.headline
    ? formatComponentLabel(record.headline.component, record.headline.basis)
    : null

  return (
    <article className="card">
      <div className="meta small muted">
        {record.provider} · {record.country}
      </div>

      <h3 className="title">
        <a href={href}>{record.title}</a>
      </h3>

      <div className="tags">
        {record.levels.map((level) => (
          <TagChip key={level}>{level}</TagChip>
        ))}
        {fundingType === 'Fully funded' ? (
          <span className="tag tag-fully-funded">Fully funded</span>
        ) : fundingType ? (
          <TagChip>{fundingType}</TagChip>
        ) : null}
        {record.tags.map((tag) => (
          <TagChip key={tag}>{tag}</TagChip>
        ))}
        {isDevelopment ? <UnknownBadge label="Development preview" /> : null}
      </div>

      <div className="headline-award">
        {award ? (
          <>
            {componentLabel ? <div className="amount-label">{componentLabel}</div> : null}
            <div
              className={`amt amount-value${award.currencyNote ? ' amount-value-unconfirmed' : ''}`}
            >
              {award.amountText}
            </div>
            {award.qualifierText ? (
              <div className="muted small amount-basis">{award.qualifierText}</div>
            ) : null}
            {award.currencyNote ? (
              <div className="muted small award-note">{award.currencyNote}</div>
            ) : null}
          </>
        ) : (
          <div className="ph">Amount not stated in the source</div>
        )}
      </div>

      <div className="foot">
        <div className="small muted checkedline">
          {record.sourceCheck
            ? `Source checked ${formatDate(record.sourceCheck.checkedAt)}`
            : 'Not source checked yet'}
        </div>
        <a className="btn btn-primary" href={href}>
          See scholarship details
        </a>
      </div>
    </article>
  )
}
