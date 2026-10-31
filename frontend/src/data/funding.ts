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

/** A round can be marked passed by the source check or by its calendar date. */
export function isPassedStatus(status: string): boolean {
  return /passed/i.test(status)
}

function publishedDeadline(dateAsPublished: string): Date | null {
  if (!/^\d{1,2} [A-Za-z]+ \d{4}$/.test(dateAsPublished)) return null
  const date = new Date(`${dateAsPublished} 00:00:00 GMT`)
  return Number.isNaN(date.getTime()) ? null : date
}

export function isOpenRound(round: Scholarship['rounds'][number], now = new Date()): boolean {
  if (round.status !== 'Deadline published') return false
  const deadline = publishedDeadline(round.dateAsPublished)
  if (!deadline) return false
  const today = Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate())
  return deadline.getTime() >= today
}

export function isPassedRound(round: Scholarship['rounds'][number], now = new Date()): boolean {
  if (isPassedStatus(round.status)) return true
  if (round.status !== 'Deadline published') return false
  const deadline = publishedDeadline(round.dateAsPublished)
  if (!deadline) return false
  const today = Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate())
  return deadline.getTime() < today
}

export function passedRoundDates(record: Scholarship): string[] {
  return record.rounds
    .filter((round) => isPassedRound(round))
    .map((round) => round.dateAsPublished)
}

export function hasOpenRound(record: Scholarship): boolean {
  return record.rounds.some((round) => isOpenRound(round))
}
