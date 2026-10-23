/**
 * TypeScript mirror of `backend/app/domain/enums.py` and `models.py`.
 *
 * The API emits camelCase JSON (Pydantic aliases), so these interfaces are the
 * wire shape. Changing a member here is a contract change: update the Python
 * enum in the same step.
 */

export const assessmentOutcomes = [
  'meets_checked_requirements',
  'potential_fit_confirmation_needed',
  'does_not_meet_stated_requirement',
  'insufficient_information',
] as const

export type AssessmentOutcome = (typeof assessmentOutcomes)[number]

/** The only four wordings allowed on screen (CONTEXT rule 1). */
export const outcomeLabels: Record<AssessmentOutcome, string> = {
  meets_checked_requirements: 'Meets checked requirements',
  potential_fit_confirmation_needed: 'Potential fit: confirmation needed',
  does_not_meet_stated_requirement: 'Does not meet a stated requirement',
  insufficient_information: 'Insufficient information',
}

export const ruleResults = [
  'met',
  'not_met',
  'unresolved',
  'insufficient_information',
] as const

export type RuleResult = (typeof ruleResults)[number]

export const eligibilityRuleKinds = [
  'nationality',
  'residence',
  'degree_level',
  'degree_type',
  'degree_duration',
  'degree_status',
  'grade',
  'institution_recognition',
  'enrolment_status',
  'other',
] as const

export type EligibilityRuleKind = (typeof eligibilityRuleKinds)[number]

export const degreeLevels = [
  'research_master',
  'taught_master',
  'doctoral',
] as const

export type DegreeLevel = (typeof degreeLevels)[number]

export const degreeStatuses = ['ongoing', 'completed'] as const

export type DegreeStatus = (typeof degreeStatuses)[number]

export const fundingComponentKinds = [
  'tuition',
  'living_support',
  'accommodation',
  'insurance',
  'travel',
  'upfront_cost',
  'other',
] as const

export type FundingComponentKind = (typeof fundingComponentKinds)[number]

/** `unspecified` is shown as "Unspecified", never as zero or full (rule 3). */
export const fundingStatuses = ['specified', 'partial', 'unspecified'] as const

export type FundingStatus = (typeof fundingStatuses)[number]

export const fundingRelationships = [
  'tuition_reduction',
  'grant',
  'loan',
  'employment',
  'not_stated',
] as const

export type FundingRelationship = (typeof fundingRelationships)[number]

export interface Evidence {
  id: string
  url: string
  passage: string
  /** ISO 8601 timestamp: when the page was fetched. */
  retrievedAt: string
  /** ISO 8601 timestamp: when a human confirmed the passage. Null = unverified. */
  verifiedAt: string | null
  verifiedBy: string | null
}

export interface Programme {
  id: string
  name: string
  degreeLevel: DegreeLevel
  institution: string
  country: string
  durationYears: number | null
  researchComponent: boolean | null
}

export interface Round {
  id: string
  label: string
  intake: string | null
  route: string | null
}

export interface EligibilityRule {
  id: string
  requirement: string
  kind: EligibilityRuleKind
  blocking: boolean
  evidenceRefs: string[]
}

export interface FundingComponent {
  id: string
  kind: FundingComponentKind
  status: FundingStatus
  relationship: FundingRelationship
  description: string | null
  /** Decimal value as a string; never summed with other components. */
  amount: string | null
  currency: string | null
  period: string | null
  conditions: string[]
  evidenceRefs: string[]
}

export interface OfficialLinks {
  summaryUrl: string
  requirementsUrl: string
  portalUrl: string
}

export interface Opportunity {
  id: string
  schemeName: string
  funder: string
  destinations: string[]
  summary: string
  links: OfficialLinks
  programmes: Programme[]
  rounds: Round[]
  eligibilityRules: EligibilityRule[]
  fundingComponents: FundingComponent[]
  evidence: Evidence[]
  lastRetrievedAt: string | null
  lastVerifiedAt: string | null
}

/** A grade exactly as the applicant stated it: no conversion (rule 6). */
export interface Grade {
  value: string
  scale: string
}

export interface Profile {
  nationality: string
  residenceCountry: string
  degreeType: string
  degreeDurationYears: number
  degreeStatus: DegreeStatus
  intendedLevel: DegreeLevel
  grade: Grade | null
}

export interface RuleAssessment {
  ruleId: string
  result: RuleResult
  reason: string
  evidenceRefs: string[]
}

export interface AssessmentResult {
  opportunityId: string
  roundId: string | null
  outcome: AssessmentOutcome
  outcomeReason: string
  rules: RuleAssessment[]
}
