import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useState } from 'react'
import { describe, expect, it } from 'vitest'

import { EMPTY_FILTERS, type ScholarshipFilters } from '../src/data/filters'
import { ExplorePage } from '../src/pages/ExplorePage'
import { makeRecord } from './fixtures'

const canadian = makeRecord({
  id: 'canada-doctoral',
  title: 'Canada Doctoral Award',
  country: 'Canada',
  coverage: {
    tuition: { state: 'stated' },
    livingCosts: { state: 'stated' },
    flights: { state: 'unspecified' },
  },
})

const australian = makeRecord({
  id: 'australia-research',
  title: 'Australian Research Stipend',
  country: 'Australia',
  levels: ['Research degree'],
})

const records = [canadian, australian]

/**
 * Route state normally lives in the hash; the harness keeps it in React state
 * so a filter change is observable without a real navigation.
 */
function Harness({ initial = EMPTY_FILTERS }: { initial?: ScholarshipFilters }) {
  const [filters, setFilters] = useState(initial)
  return (
    <ExplorePage
      records={records}
      isDevelopment={false}
      filters={filters}
      onFiltersChange={setFilters}
    />
  )
}

describe('ExplorePage', () => {
  it('counts the results with singular and plural headings', () => {
    render(<Harness />)

    expect(screen.getByRole('heading', { level: 2, name: '2 scholarships' })).toBeInTheDocument()
    expect(screen.getAllByRole('article')).toHaveLength(2)
  })

  it('narrows the list when a country filter chip is toggled', async () => {
    const user = userEvent.setup()
    render(<Harness />)

    const australiaChip = screen.getByRole('button', { name: 'Australia' })
    expect(australiaChip).toHaveAttribute('aria-pressed', 'false')
    await user.click(australiaChip)

    expect(australiaChip).toHaveAttribute('aria-pressed', 'true')
    expect(screen.getByRole('heading', { level: 2, name: '1 scholarship' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { level: 3, name: /australian research stipend/i })).toBeVisible()
    expect(screen.queryByRole('heading', { level: 3, name: /canada doctoral award/i })).toBeNull()
  })

  it('removes a filter through its active chip', async () => {
    const user = userEvent.setup()
    render(<Harness initial={{ ...EMPTY_FILTERS, country: 'Canada' }} />)

    const chip = screen.getByRole('button', { name: 'Remove filter Canada' })
    await user.click(chip)

    expect(screen.getByRole('heading', { level: 2, name: '2 scholarships' })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Remove filter Canada' })).toBeNull()
  })

  it('filters by the derived funding type', async () => {
    const user = userEvent.setup()
    render(<Harness />)

    const fundingChip = screen.getByRole('button', { name: 'Tuition + stipend' })
    await user.click(fundingChip)

    expect(fundingChip).toHaveAttribute('aria-pressed', 'true')
    expect(screen.getByRole('heading', { level: 2, name: '1 scholarship' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { level: 3, name: /canada doctoral award/i })).toBeVisible()
  })

  it('submits a search and shows it as an active filter', async () => {
    const user = userEvent.setup()
    render(<Harness />)

    await user.type(screen.getByLabelText('Search scholarships'), 'australia')
    await user.click(screen.getByRole('button', { name: 'Search' }))

    expect(screen.getByRole('heading', { level: 2, name: '1 scholarship' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Remove filter australia' })).toBeInTheDocument()
  })

  it('explains an empty result instead of showing a blank page', async () => {
    const user = userEvent.setup()
    render(<Harness initial={{ ...EMPTY_FILTERS, q: 'zzz' }} />)

    expect(
      screen.getByRole('heading', {
        level: 3,
        name: /no published scholarships match these filters\./i,
      }),
    ).toBeInTheDocument()

    const clearButtons = screen.getAllByRole('button', { name: 'Clear filters' })
    await user.click(clearButtons[clearButtons.length - 1])

    expect(screen.getAllByRole('article')).toHaveLength(2)
    expect(screen.getByLabelText('Search scholarships')).toHaveValue('')
  })
})
