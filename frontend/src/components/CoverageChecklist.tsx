import { fundingTypeFor } from '../data/funding'
import { COVERAGE_KEYS, COVERAGE_LABELS, type FundingCoverage } from '../data/types'
import { CoverageChip } from './Chips'
import { UnknownBadge } from './UnknownBadge'

interface CoverageChecklistProps {
  coverage: FundingCoverage
  compact?: boolean
}

export function CoverageChecklist({ coverage, compact = false }: CoverageChecklistProps) {
  if (compact) {
    const coveredKeys = COVERAGE_KEYS.filter((key) => coverage[key].state === 'stated')
    const unknownKeys = COVERAGE_KEYS.filter((key) => coverage[key].state !== 'stated')

    if (unknownKeys.length > 1) {
      return (
        <ul className="slist list-plain">
          {coveredKeys.map((key) => (
            <li className="coverage-row" key={key}>
              <span>{COVERAGE_LABELS[key]}</span>
              <CoverageChip state="stated" />
            </li>
          ))}
          <li className="coverage-row">
            <UnknownBadge
              label={`Not stated by provider: ${unknownKeys.map((k) => COVERAGE_LABELS[k].toLowerCase()).join(', ')}`}
            />
          </li>
        </ul>
      )
    }

    return (
      <ul className="slist list-plain">
        {COVERAGE_KEYS.map((key) => (
          <li className="coverage-row" key={key}>
            <span>{COVERAGE_LABELS[key]}</span>
            <CoverageChip state={coverage[key].state} />
          </li>
        ))}
      </ul>
    )
  }

  const fundingType = fundingTypeFor(coverage)

  return (
    <div className="rule">
      <strong>
        {fundingType === 'Fully funded' ? (
          <>
            <span className="tag tag-fully-funded">Fully funded</span>{' '}
          </>
        ) : null}
        What the official page says it covers
      </strong>
      <div className="small muted">
        “Fully funded” is shown only when tuition, living costs and flights are all stated as
        covered.
      </div>
      {COVERAGE_KEYS.map((key) => (
        <div className="coverage-row covrow" key={key}>
          <span>
            {COVERAGE_LABELS[key]}
            {coverage[key].detail ? (
              <span className="small muted covdetail"> — {coverage[key].detail}</span>
            ) : null}
          </span>
          <CoverageChip state={coverage[key].state} />
        </div>
      ))}
    </div>
  )
}
