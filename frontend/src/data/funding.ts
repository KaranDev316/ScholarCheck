import {
  COVERAGE_KEYS,
  type FundingCoverage,
  type FundingType,
  type FactState,
  type Scholarship,
} from './types'

/**
 * Only a stated fact counts as covered. Conflicting or missing facts are never
 * rounded up to "funded".
 */
export function isCovered(state: FactState): boolean {
  return state === 'stated'
}

/** "Fully funded" needs all three coverage facts stated, not just two. */
export function isFullyFunded(coverage: FundingCoverage): boolean {
  return COVERAGE_KEYS.every((key) => isCovered(coverage[key].state))
}

/**
 * Funding type is derived from coverage rather than entered by hand, so a card
 * can never claim a label the record does not support.
 */
export function fundingTypeFor(coverage: FundingCoverage): FundingType | null {
  if (isFullyFunded(coverage)) return 'Fully funded'
  if (isCovered(coverage.tuition.state) && isCovered(coverage.livingCosts.state)) {
    return 'Tuition + stipend'
  }
  if (isCovered(coverage.tuition.state)) return 'Tuition'
  return null
}

export function fundingTypeLabel(record: Scholarship): string {
  return fundingTypeFor(record.coverage) ?? 'Funding type not established'
}

/** A round is passed only when its published status says so. */
export function isPassedStatus(status: string): boolean {
  return /passed/i.test(status)
}

export function passedRoundDates(record: Scholarship): string[] {
  return record.rounds
    .filter((round) => isPassedStatus(round.status))
    .map((round) => round.dateAsPublished)
}

export function hasOpenRound(record: Scholarship): boolean {
  return record.rounds.some((round) => !isPassedStatus(round.status))
}
