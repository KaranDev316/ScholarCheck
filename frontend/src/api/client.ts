/**
 * Thin fetch wrapper for the ScholarCheck API.
 *
 * Failures always surface as `ApiRequestError` carrying the agreed error body
 * `{code, message, details?}` (CONTEXT section 6), so screens can show plain
 * language instead of a raw HTTP status.
 */

import type { ErrorBody, FieldError, HealthResponse } from '../types/api'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api'

const UNREACHABLE_MESSAGE =
  'We could not reach the ScholarCheck service. Check your connection and try again.'
const UNEXPECTED_MESSAGE = 'Something went wrong. Please try again.'

export class ApiRequestError extends Error {
  readonly status: number
  readonly code: string
  readonly details: FieldError[]

  constructor(
    status: number,
    code: string,
    message: string,
    details: FieldError[] = [],
  ) {
    super(message)
    this.name = 'ApiRequestError'
    this.status = status
    this.code = code
    this.details = details
  }
}

function isErrorBody(value: unknown): value is ErrorBody {
  if (typeof value !== 'object' || value === null) {
    return false
  }
  const candidate = value as Record<string, unknown>
  return (
    typeof candidate.code === 'string' && typeof candidate.message === 'string'
  )
}

async function readJson(response: Response): Promise<unknown> {
  try {
    return (await response.json()) as unknown
  } catch {
    return null
  }
}

async function requestJson(path: string, init: RequestInit): Promise<unknown> {
  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: { Accept: 'application/json' },
      ...init,
    })
  } catch {
    throw new ApiRequestError(0, 'network_error', UNREACHABLE_MESSAGE)
  }

  const payload = await readJson(response)

  if (!response.ok) {
    if (isErrorBody(payload)) {
      throw new ApiRequestError(
        response.status,
        payload.code,
        payload.message,
        payload.details ?? [],
      )
    }
    throw new ApiRequestError(response.status, 'unexpected_error', UNEXPECTED_MESSAGE)
  }

  return payload
}

export async function getHealth(signal?: AbortSignal): Promise<HealthResponse> {
  const payload = await requestJson('/health', { method: 'GET', signal })

  if (
    typeof payload !== 'object' ||
    payload === null ||
    typeof (payload as Record<string, unknown>).status !== 'string'
  ) {
    throw new ApiRequestError(200, 'unexpected_error', UNEXPECTED_MESSAGE)
  }

  return payload as HealthResponse
}
