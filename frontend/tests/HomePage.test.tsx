import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it } from 'vitest'

import { HomePage } from '../src/pages/HomePage'
import { fullyFundedRecord, makeRecord } from './fixtures'

describe('HomePage', () => {
  beforeEach(() => {
    window.history.replaceState(null, '', '#home')
  })

  it('states the ScholarCheck promise and admits there is nothing published', () => {
    render(<HomePage records={[]} isDevelopment={false} />)

    expect(
      screen.getByRole('heading', {
        level: 1,
        name: /find funding. check the evidence. decide for yourself/i,
      }),
    ).toBeInTheDocument()
    expect(screen.getAllByText(/no published scholarships yet/i)).not.toHaveLength(0)
    expect(screen.queryByText(/development preview/i)).not.toBeInTheDocument()
  })

  it('marks preview records instead of presenting them as published', () => {
    render(<HomePage records={[makeRecord()]} isDevelopment />)

    expect(
      screen.getByRole('heading', { level: 2, name: /development preview scholarships/i }),
    ).toBeInTheDocument()
    expect(screen.getAllByText('Development preview').length).toBeGreaterThan(0)
    expect(screen.queryByText(/^published scholarships$/i)).not.toBeInTheDocument()
  })

  it('lists one card per record with its amount and source-check status', () => {
    render(<HomePage records={[makeRecord(), fullyFundedRecord]} isDevelopment />)

    expect(screen.getByRole('heading', { level: 3, name: /example doctoral award/i })).toBeVisible()
    expect(screen.getAllByRole('link', { name: /see scholarship details/i })).toHaveLength(2)
    expect(screen.getAllByText('CA$20,000').length).toBeGreaterThan(0)
    expect(screen.getAllByText(/not source checked yet/i)).toHaveLength(1)
    expect(screen.getByText(/source checked 27 October 2026/i)).toBeInTheDocument()
  })

  it('shows the catalogue record without internal quotations', () => {
    render(<HomePage records={[makeRecord()]} isDevelopment />)

    const hero = screen.getByLabelText('Example record from the catalogue')
    expect(within(hero).getByText(/example university, canada/i)).toBeInTheDocument()
    expect(within(hero).queryByText(/from the official page/i)).toBeNull()
    expect(within(hero).queryByText(/a stipend of ca\$20,000 per year\./i)).toBeNull()
  })

  it('offers quick filters that lead to a filtered search', () => {
    render(<HomePage records={[makeRecord()]} isDevelopment />)

    expect(screen.getByRole('link', { name: 'Canada' })).toHaveAttribute('href', '#explore?c=Canada')
    expect(screen.getByRole('link', { name: 'PhD' })).toHaveAttribute('href', '#explore?l=PhD')
    expect(screen.getByRole('link', { name: 'Fully funded' })).toHaveAttribute(
      'href',
      '#explore?f=Fully+funded',
    )
  })

  it('sends a typed search to the explore view', async () => {
    const user = userEvent.setup()
    render(<HomePage records={[makeRecord()]} isDevelopment />)

    await user.type(screen.getByLabelText('Search scholarships'), 'doctoral Canada')
    await user.click(screen.getByRole('button', { name: 'Search' }))

    expect(window.location.hash).toBe('#explore?q=doctoral+Canada')
  })
})
