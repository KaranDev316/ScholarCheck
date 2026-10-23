/**
 * PROPOSED HTTP contracts, mirroring `backend/app/models/assessment.py` and
 * `backend/app/api/errors.py`. Not final until the T02/T07 gate is approved.
 */

import type { AssessmentResult, Profile } from './domain'

export interface HealthResponse {
  status: string
  service: string
  environment: string
}

export interface AssessmentRequest {
  profile: Profile
  /** Omitted when the opportunity has a single round. */
  roundId?: string | null
}

export interface AssessmentResponse {
  assessment: AssessmentResult
}

export interface FieldError {
  field: string
  message: string
}

/** Every non-2xx response body: `{code, message, details?}`. */
export interface ErrorBody {
  code: string
  message: string
  details: FieldError[] | null
}
