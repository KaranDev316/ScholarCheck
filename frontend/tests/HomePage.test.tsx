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
        name: /know whether a funded degree/i,
      }),
    ).toBeInTheDocument()
    expect(
      screen.getByText(/bachelor.s, master.s and PhD/i),
    ).toBeInTheDocument()
  })

  it('shows the public MVP scope without claiming publication', () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(() =>
        Promise.reject(new Error('not needed for this assertion')),
      ),
    )

    render(<HomePage />)

    expect(screen.getByText(/search by country, study level and funding/i)).toBeInTheDocument()
    expect(screen.getByText(/no opportunity is published/i)).toBeInTheDocument()
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
        name: /know whether a funded degree/i,
      }),
    ).toBeInTheDocument()
  })
})
