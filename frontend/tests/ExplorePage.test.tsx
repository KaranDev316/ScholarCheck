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
  it('counts the results against the whole catalogue', () => {
    render(<Harness />)

    expect(screen.getByText(/showing 2 of 2 published scholarships/i)).toBeInTheDocument()
    expect(screen.getAllByRole('article')).toHaveLength(2)
  })

  it('narrows the list when a country is chosen', async () => {
    const user = userEvent.setup()
    render(<Harness />)

    await user.selectOptions(screen.getByLabelText('Destination country'), 'Australia')

    expect(screen.getByText(/showing 1 of 2 published scholarships/i)).toBeInTheDocument()
    expect(screen.getByRole('heading', { level: 3, name: /australian research stipend/i })).toBeVisible()
    expect(screen.queryByRole('heading', { level: 3, name: /canada doctoral award/i })).toBeNull()
  })

  it('removes a filter through its active chip', async () => {
    const user = userEvent.setup()
    render(<Harness initial={{ ...EMPTY_FILTERS, country: 'Canada' }} />)

    const chip = screen.getByRole('button', { name: 'Remove filter Canada' })
    await user.click(chip)

    expect(screen.getByText(/showing 2 of 2 published scholarships/i)).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Remove filter Canada' })).toBeNull()
  })

  it('filters by the derived funding type', async () => {
    const user = userEvent.setup()
    render(<Harness />)

    await user.selectOptions(screen.getByLabelText('Funding type'), 'Tuition + stipend')

    expect(screen.getByText(/showing 1 of 2 published scholarships/i)).toBeInTheDocument()
    expect(screen.getByRole('heading', { level: 3, name: /canada doctoral award/i })).toBeVisible()
  })

  it('submits a search and shows it as an active filter', async () => {
    const user = userEvent.setup()
    render(<Harness />)

    await user.type(screen.getByLabelText('Search scholarships'), 'australia')
    await user.click(screen.getByRole('button', { name: 'Search' }))

    expect(screen.getByText(/showing 1 of 2 published scholarships/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Remove filter australia' })).toBeInTheDocument()
  })

  it('explains an empty result instead of showing a blank page', async () => {
    const user = userEvent.setup()
    render(<Harness initial={{ ...EMPTY_FILTERS, q: 'zzz' }} />)

    expect(
      screen.getByRole('heading', { level: 3, name: /no published scholarship matches these filters/i }),
    ).toBeInTheDocument()
    expect(screen.getByText(/only scholarships that passed our evidence checks are listed/i)).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Clear all filters' }))

    expect(screen.getAllByRole('article')).toHaveLength(2)
    expect(screen.getByLabelText('Search scholarships')).toHaveValue('')
  })
})
