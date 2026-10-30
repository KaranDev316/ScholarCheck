import { TagChip } from './Chips'
import { fundingTypeFor } from '../data/funding'
import { formatCheckedAgo } from '../data/format'
import type { Scholarship } from '../data/types'
import { scholarshipHref } from '../routing/routes'

interface ScholarshipCardProps {
  record: Scholarship
  isDevelopment: boolean
}

export function ScholarshipCard({ record, isDevelopment }: ScholarshipCardProps) {
  const fundingType = fundingTypeFor(record.coverage)
  const href = scholarshipHref(record.id)

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
      <p className="mute">{record.summary}</p>

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
          {record.headline ? (
            <>
              <div className="amt">{record.headline.amount}</div>
              <div className="mute small">
                {record.headline.component} · {record.headline.basis}
              </div>
            </>
          ) : (
            <div className="ph">Amount not stated in the source</div>
          )}
          <div className="small mute checkedline">
            {record.sourceCheck
              ? `Checked ${formatCheckedAgo(record.sourceCheck.checkedAt)} against the official page`
              : 'Not source checked yet'}
          </div>
        </div>
        <a className="btn alt sm" href={href}>
          See evidence and details
        </a>
      </div>
    </article>
  )
}
