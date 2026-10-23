import { render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'

import { HomePage } from '../src/pages/HomePage'

function healthResponse(body: unknown, ok = true, status = 200) {
  return {
    ok,
    status,
    json: async () => body,
  }
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('HomePage (T01/T02)', () => {
  it('t01_renders_the_product_heading', () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(() =>
        Promise.reject(new Error('not needed for this assertion')),
      ),
    )

    render(<HomePage />)

    expect(
      screen.getByRole('heading', {
        level: 1,
        name: /know whether a funded master/i,
      }),
    ).toBeInTheDocument()
  })

  it('t02_lists_exactly_the_four_outcome_wordings', () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(() =>
        Promise.reject(new Error('not needed for this assertion')),
      ),
    )

    render(<HomePage />)

    const outcomes = screen.getAllByRole('listitem').map((item) => item.textContent)

    expect(outcomes).toEqual([
      'Meets checked requirements',
      'Potential fit: confirmation needed',
      'Does not meet a stated requirement',
      'Insufficient information',
    ])
    expect(screen.getByText(/no scores and no win probabilities/i)).toBeInTheDocument()
  })

  it('t01_reports_a_connected_api', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () =>
        healthResponse({
          status: 'ok',
          service: 'scholarcheck-api',
          environment: 'test',
        }),
      ),
    )

    render(<HomePage />)

    expect(screen.getByText(/checking the scholarcheck service/i)).toBeInTheDocument()
    expect(
      await screen.findByText(/api connected/i),
    ).toBeInTheDocument()
    expect(screen.getByText('test')).toBeInTheDocument()
  })

  it('t01_keeps_the_page_readable_when_the_api_is_down', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(() => Promise.reject(new Error('connection refused'))),
    )

    render(<HomePage />)

    expect(
      await screen.findByText(/api not reachable/i),
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', {
        level: 1,
        name: /know whether a funded master/i,
      }),
    ).toBeInTheDocument()
  })
})
