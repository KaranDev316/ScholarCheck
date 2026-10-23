import { afterEach, describe, expect, it, vi } from 'vitest'

import { ApiRequestError, getHealth } from '../src/api/client'

function jsonResponse(body: unknown, ok = true, status = 200) {
  return {
    ok,
    status,
    json: async () => body,
  }
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('api client (T01)', () => {
  it('t01_reads_the_health_payload', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () =>
        jsonResponse({
          status: 'ok',
          service: 'scholarcheck-api',
          environment: 'development',
        }),
      ),
    )

    await expect(getHealth()).resolves.toEqual({
      status: 'ok',
      service: 'scholarcheck-api',
      environment: 'development',
    })
  })

  it('t01_surfaces_the_agreed_error_body', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () =>
        jsonResponse(
          {
            code: 'opportunity_not_found',
            message: 'We could not find that opportunity.',
            details: null,
          },
          false,
          404,
        ),
      ),
    )

    const error = await getHealth().catch((caught: unknown) => caught)

    expect(error).toBeInstanceOf(ApiRequestError)
    const apiError = error as ApiRequestError
    expect(apiError.status).toBe(404)
    expect(apiError.code).toBe('opportunity_not_found')
    expect(apiError.message).toBe('We could not find that opportunity.')
  })

  it('t01_reports_a_network_failure_in_plain_language', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(() => Promise.reject(new Error('connection refused'))),
    )

    const error = await getHealth().catch((caught: unknown) => caught)

    expect(error).toBeInstanceOf(ApiRequestError)
    expect((error as ApiRequestError).code).toBe('network_error')
    expect((error as ApiRequestError).message).toMatch(/could not reach/i)
  })
})
