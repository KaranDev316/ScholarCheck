import { useState } from 'react'
import type { FormEvent } from 'react'

import { Card } from '../components/Card'
import { FilterChip } from '../components/FilterChip'
import {
  EMPTY_FILTERS,
  availableCountries,
  filterScholarships,
  hasActiveFilters,
  type ScholarshipFilters,
} from '../data/filters'
import { FUNDING_TYPES, type Scholarship, type StudyLevel } from '../data/types'

interface ExplorePageProps {
  records: readonly Scholarship[]
  isDevelopment: boolean
  filters: ScholarshipFilters
  onFiltersChange: (filters: ScholarshipFilters) => void
}

const PRIMARY_LEVELS: readonly StudyLevel[] = ["Bachelor's", "Master's", 'PhD']

export function ExplorePage({
  records,
  isDevelopment,
  filters,
  onFiltersChange,
}: ExplorePageProps) {
  const [query, setQuery] = useState(filters.q)
  const [syncedQuery, setSyncedQuery] = useState(filters.q)
  const countries = availableCountries(records)
  const hasResearchFallback =
    records.some((record) => record.levels.includes('Research degree')) ||
    filters.level === 'Research degree'
  const levels: readonly StudyLevel[] = hasResearchFallback
    ? [...PRIMARY_LEVELS, 'Research degree']
    : PRIMARY_LEVELS

  const results = filterScholarships(records, filters)
  const filtering = hasActiveFilters(filters)

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
    <section className="container wrap explorepage">
      <h1 className="h-section">Find scholarships</h1>
      <p className="muted intro">
        Filter by destination, study level and funding. Open any record for funding details, stated
        requirements and official links.
      </p>

      <form className="bar search" role="search" onSubmit={submitSearch}>
        <input
          name="q"
          aria-label="Search scholarships"
          placeholder="Try 'doctoral scholarships in Canada'"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />
        <button className="btn btn-primary" type="submit">
          Search
        </button>
      </form>

      <div className="filter-bar" aria-label="Filters">
        {countries.length > 0 ? (
          <div className="filter-group" role="group" aria-label="Destination country">
            <span className="filter-group-label small muted">Country</span>
            <div className="filter-chips">
              {countries.map((country) => (
                <FilterChip
                  key={country}
                  label={country}
                  selected={filters.country === country}
                  onToggle={() =>
                    onFiltersChange({
                      ...filters,
                      country: filters.country === country ? '' : country,
                    })
                  }
                />
              ))}
            </div>
          </div>
        ) : null}

        <div className="filter-group" role="group" aria-label="Study level">
          <span className="filter-group-label small muted">Level</span>
          <div className="filter-chips">
            {levels.map((level) => (
              <FilterChip
                key={level}
                label={level}
                selected={filters.level === level}
                onToggle={() =>
                  onFiltersChange({
                    ...filters,
                    level: filters.level === level ? '' : level,
                  })
                }
              />
            ))}
          </div>
        </div>

        <div className="filter-group" role="group" aria-label="Funding type">
          <span className="filter-group-label small muted">Funding type</span>
          <div className="filter-chips">
            {FUNDING_TYPES.map((funding) => (
              <FilterChip
                key={funding}
                label={funding}
                selected={filters.funding === funding}
                onToggle={() =>
                  onFiltersChange({
                    ...filters,
                    funding: filters.funding === funding ? '' : funding,
                  })
                }
              />
            ))}
          </div>
        </div>
      </div>

      {filtering ? (
        <div className="active" aria-label="Active filters">
          {filters.q ? (
            <FilterChip
              label={`Search: “${filters.q}”`}
              removeLabel={filters.q}
              onRemove={() => onFiltersChange({ ...filters, q: '' })}
            />
          ) : null}
          {[filters.country, filters.level, filters.funding]
            .filter(Boolean)
            .map((label) => (
              <FilterChip
                key={label}
                label={label}
                onRemove={() => clearFilter(label)}
              />
            ))}
          <button
            className="btn btn-secondary sm"
            type="button"
            onClick={() => onFiltersChange(EMPTY_FILTERS)}
          >
            Clear filters
          </button>
        </div>
      ) : null}

      <h2 className="count">
        {results.length} {results.length === 1 ? 'scholarship' : 'scholarships'}
      </h2>

      {results.length === 0 ? (
        <div className="state state-empty">
          <h3>No published scholarships match these filters.</h3>
          <button
            className="btn btn-primary"
            type="button"
            onClick={() => onFiltersChange(EMPTY_FILTERS)}
          >
            Clear filters
          </button>
        </div>
      ) : (
        <div
          className={
            results.length === 1
              ? 'card-grid card-grid--single cards'
              : results.length === 2
                ? 'card-grid card-grid--two cards'
                : 'card-grid cards'
          }
        >
          {results.map((record) => (
            <Card key={record.id} record={record} isDevelopment={isDevelopment} />
          ))}
        </div>
      )}
    </section>
  )
}
