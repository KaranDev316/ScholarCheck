import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it } from 'vitest'

import { HomePage } from '../src/pages/HomePage'
import { fullyFundedRecord, makeRecord } from './fixtures'

describe('HomePage', () => {
  beforeEach(() => {
    window.history.replaceState(null, '', '#home')
  })

  it('states the ScholarCheck promise in three lines and admits there is nothing published', () => {
    render(<HomePage records={[]} isDevelopment={false} />)

    const heading = screen.getByRole('heading', {
      level: 1,
      name: /find funding\. check the evidence\. decide for yourself/i,
    })
    expect(heading).toBeInTheDocument()
    expect(heading.querySelectorAll('.line')).toHaveLength(3)
    expect(screen.getAllByText(/no published scholarships yet/i)).not.toHaveLength(0)
    expect(screen.queryByText(/development preview/i)).not.toBeInTheDocument()
    expect(screen.queryByText(/browse all/i)).not.toBeInTheDocument()
  })

  it('marks preview records instead of presenting them as published', () => {
    render(<HomePage records={[makeRecord()]} isDevelopment />)

    expect(
      screen.getByRole('heading', { level: 2, name: /development preview scholarships/i }),
    ).toBeInTheDocument()
    expect(screen.getAllByText('Development preview').length).toBeGreaterThan(0)
    expect(screen.queryByText(/^published scholarships$/i)).not.toBeInTheDocument()
  })

  it('lists one card per record with its amount and source-check status, without description or deadline rows', () => {
    render(<HomePage records={[makeRecord(), fullyFundedRecord]} isDevelopment />)

    expect(screen.getByRole('heading', { level: 3, name: /example doctoral award/i })).toBeVisible()
    expect(screen.getAllByRole('link', { name: /see scholarship details/i })).toHaveLength(2)
    expect(screen.getAllByText('CAD $20,000').length).toBeGreaterThan(0)
    expect(screen.getAllByText(/not source checked yet/i)).toHaveLength(1)
    expect(screen.getByText(/source checked 27 Oct 2026/i)).toBeInTheDocument()
    expect(screen.queryByText(/a doctoral award used by the tests/i)).toBeNull()
    expect(screen.queryByText('Deadline')).toBeNull()
  })

  it('shows a single compact row when only one record is published, and omits deadlines from the hero', () => {
    const unknownCurrencyRecord = makeRecord({
      id: 'cgsd-doctoral',
      title: 'Canada Graduate Research Scholarship – Doctoral (CGRS D)',
      currency: null,
      summary: 'A competitive doctoral scholarship. The source lists $40,000 per year for 36 months.',
      headline: {
        component: 'Award component',
        amount: '40,000',
        currency: null,
        basis: 'per year for 36 months',
      },
      deadline: {
        type: 'varies',
        note: "Set by your institution. Confirm with your university's graduate office.",
      },
      sourceCheck: { checkedAt: '2026-11-03T18:40:32Z', result: 'matches' },
    })
    render(<HomePage records={[unknownCurrencyRecord]} isDevelopment={false} />)

    const hero = screen.getByLabelText('Example record from the catalogue')
    expect(within(hero).getByText('Annual award')).toHaveClass('amount-label')
    expect(within(hero).getByText('$40,000')).toHaveClass('sa')
    expect(within(hero).getByText('per year for 36 months')).toHaveClass('sm')
    expect(within(hero).getByText('Currency not stated')).toHaveClass('award-note')
    expect(within(hero).queryByText('Deadline')).toBeNull()
    expect(within(hero).queryByText('Check with institution')).toBeNull()
    expect(within(hero).getByText('Source checked 3 Nov 2026')).toBeInTheDocument()
    expect(
      within(hero).getByText('Not stated by provider: tuition, flights'),
    ).toBeInTheDocument()
    expect(screen.queryByText(/03\/11\/2026/)).toBeNull()
    expect(screen.getByRole('link', { name: 'See details' })).toHaveAttribute(
      'href',
      '#cgsd-doctoral',
    )
    expect(screen.queryByRole('link', { name: /see scholarship details/i })).toBeNull()
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
