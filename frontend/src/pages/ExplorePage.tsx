import { useId, useState } from 'react'
import type { FormEvent } from 'react'

import { ScholarshipCard } from '../components/ScholarshipCard'
import {
  EMPTY_FILTERS,
  availableCountries,
  filterScholarships,
  hasActiveFilters,
  type ScholarshipFilters,
} from '../data/filters'
import { FUNDING_TYPES, STUDY_LEVELS } from '../data/types'
import type { Scholarship } from '../data/types'

interface ExplorePageProps {
  records: readonly Scholarship[]
  isDevelopment: boolean
  filters: ScholarshipFilters
  onFiltersChange: (filters: ScholarshipFilters) => void
}

export function ExplorePage({
  records,
  isDevelopment,
  filters,
  onFiltersChange,
}: ExplorePageProps) {
  const [query, setQuery] = useState(filters.q)
  const [syncedQuery, setSyncedQuery] = useState(filters.q)
  const idPrefix = useId()
  const countries = availableCountries(records)
  const results = filterScholarships(records, filters)
  const filtering = hasActiveFilters(filters)

  // The URL is the source of truth. When it changes — a chip removed, "Clear
  // all", a shared link — the search box follows before the next paint.
  if (syncedQuery !== filters.q) {
    setSyncedQuery(filters.q)
    setQuery(filters.q)
  }

  function submitSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const trimmed = query.trim()
    if (trimmed === filters.q) return
    onFiltersChange({ ...filters, q: trimmed })
  }

  function clearFilter(label: string) {
    onFiltersChange({
      ...filters,
      country: filters.country === label ? '' : filters.country,
      level: filters.level === label ? '' : filters.level,
      funding: filters.funding === label ? '' : filters.funding,
    })
  }

  return (
    <section className="wrap explorepage">
      <h1 className="h-section">Find scholarships</h1>
      <p className="mute intro">
        Filter by destination, study level and funding. Open any record for funding details, stated requirements and official links.
      </p>

      <div className="explore">
        <details className="filters" open>
          <summary>Filters</summary>
          <div className="filterfields">
            <label htmlFor={`${idPrefix}-country`}>
              Destination country
              <select
                id={`${idPrefix}-country`}
                value={filters.country}
                onChange={(event) => onFiltersChange({ ...filters, country: event.target.value })}
              >
                <option value="">All countries</option>
                {countries.map((country) => (
                  <option key={country} value={country}>
                    {country}
                  </option>
                ))}
              </select>
            </label>

            <label htmlFor={`${idPrefix}-level`}>
              Study level
              <select
                id={`${idPrefix}-level`}
                value={filters.level}
                onChange={(event) =>
                  onFiltersChange({
                    ...filters,
                    level: event.target.value as ScholarshipFilters['level'],
                  })
                }
              >
                <option value="">All levels</option>
                {STUDY_LEVELS.map((level) => (
                  <option key={level} value={level}>
                    {level}
                  </option>
                ))}
              </select>
            </label>

            <label htmlFor={`${idPrefix}-funding`}>
              Funding type
              <select
                id={`${idPrefix}-funding`}
                value={filters.funding}
                onChange={(event) =>
                  onFiltersChange({
                    ...filters,
                    funding: event.target.value as ScholarshipFilters['funding'],
                  })
                }
              >
                <option value="">All funding types</option>
                {FUNDING_TYPES.map((funding) => (
                  <option key={funding} value={funding}>
                    {funding}
                  </option>
                ))}
              </select>
            </label>

            <button
              className="btn alt sm"
              type="button"
              onClick={() => onFiltersChange(EMPTY_FILTERS)}
              disabled={!filtering}
            >
              Clear all
            </button>
          </div>
        </details>

        <div>
          <form className="bar" role="search" onSubmit={submitSearch}>
            <input
              name="q"
              aria-label="Search scholarships"
              placeholder="Scholarship, university or country"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
            />
            <button className="btn" type="submit">
              Search
            </button>
          </form>

          <div className="active">
            {filters.q ? (
              <button
                type="button"
                aria-label={`Remove filter ${filters.q}`}
                onClick={() => onFiltersChange({ ...filters, q: '' })}
              >
                Search: “{filters.q}” ×
              </button>
            ) : null}
            {[filters.country, filters.level, filters.funding]
              .filter(Boolean)
              .map((label) => (
                <button
                  key={label}
                  type="button"
                  aria-label={`Remove filter ${label}`}
                  onClick={() => clearFilter(label)}
                >
                  {label} ×
                </button>
              ))}
          </div>

          <p className="mute small count">
            Showing {results.length} of {records.length}{' '}
            {isDevelopment ? 'development preview' : 'published'} scholarships
          </p>

          {results.length === 0 ? (
            <div className="state">
              <h3>
                No {isDevelopment ? 'development preview' : 'published'} scholarship matches these
                filters
              </h3>
              <p className="mute">
                {isDevelopment
                  ? 'These preview records have not passed source checks.'
                  : 'Only scholarships that passed our evidence checks are listed.'}{' '}
                Remove a filter to widen the search.
              </p>
              <button className="btn" type="button" onClick={() => onFiltersChange(EMPTY_FILTERS)}>
                Clear all filters
              </button>
            </div>
          ) : (
            <div className="cards">
              {results.map((record) => (
                <ScholarshipCard key={record.id} record={record} isDevelopment={isDevelopment} />
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  )
}
