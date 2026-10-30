/**
 * View model for the public scholarship screens.
 *
 * These types describe what a screen needs to show, not the stored domain model
 * in `backend/app/domain/models.py`. Coverage states, round statuses and the
 * source-check result arrive from the publication pipeline; until the
 * published-only API exists, `developmentCatalogue.ts` supplies preview data.
 */

/** How well a material fact is supported by its official source. */
export type FactState = 'stated' | 'unspecified' | 'conflicting'

/** Labels used by the filter controls and the "Fully funded" rule. */
export const STUDY_LEVELS = ["Bachelor's", "Master's", 'PhD', 'Research degree'] as const
export type StudyLevel = (typeof STUDY_LEVELS)[number]

export const FUNDING_TYPES = ['Fully funded', 'Tuition + stipend', 'Tuition'] as const
export type FundingType = (typeof FUNDING_TYPES)[number]

/** The three coverage facts that decide the funding-type label. */
export const COVERAGE_KEYS = ['tuition', 'livingCosts', 'flights'] as const
export type CoverageKey = (typeof COVERAGE_KEYS)[number]

export const COVERAGE_LABELS: Record<CoverageKey, string> = {
  tuition: 'Tuition',
  livingCosts: 'Living costs',
  flights: 'Flights',
}

export interface CoverageFact {
  state: FactState
  /** Plain-language qualifier, e.g. which charges a tuition exemption covers. */
  detail?: string
}

export type FundingCoverage = Record<CoverageKey, CoverageFact>

export interface FundingComponentView {
  id: string
  label: string
  state: FactState
  /** Amount exactly as published, e.g. 'CA$40,000'. Omitted when not stated. */
  amount?: string
  /** The published basis for the amount, e.g. 'per year for 36 months'. */
  basis?: string
  note?: string
  conditions?: readonly string[]
  /** Number of the evidence entry that supports this component. */
  evidenceNumber?: number
}

export interface EligibilityStatement {
  id: string
  statement: string
  state: FactState
  evidenceNumber?: number
}

export interface RoundView {
  id: string
  round: string
  dateAsPublished: string
  /** Published round status, e.g. 'Date passed' or 'No separate application'. */
  status: string
  note: string
}

export type ApplicationRoute =
  | { kind: 'provider'; note: string }
  | { kind: 'confirm'; note: string }
  | { kind: 'none'; note: string }

export interface EvidenceEntry {
  number: number
  claim: string
  passage: string
  url: string
  /** When the retained copy was saved, as an ISO 8601 timestamp. */
  savedAt: string
}

export interface SourceCheck {
  /** When the record was last checked, as an ISO 8601 timestamp. */
  checkedAt: string
  result: 'matches'
}

export interface OfficialLinks {
  summary: string
  requirements: string
  portal: string
}

export interface Scholarship {
  id: string
  title: string
  provider: string
  country: string
  levels: readonly StudyLevel[]
  summary: string
  /** Extra descriptive tags; level, country and funding type are derived. */
  tags: readonly string[]
  /** Headline amount and the component it belongs to. Never a sum. */
  headline: { component: string; amount: string; basis: string } | null
  coverage: FundingCoverage
  components: readonly FundingComponentView[]
  eligibility: readonly EligibilityStatement[]
  rounds: readonly RoundView[]
  application: ApplicationRoute
  evidence: readonly EvidenceEntry[]
  links: OfficialLinks
  /** Null until a source check has passed; shown as "Not published". */
  sourceCheck: SourceCheck | null
}
