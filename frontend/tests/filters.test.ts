import { describe, expect, it } from 'vitest'

import { filterScholarships, matchesQuery, EMPTY_FILTERS } from '../src/data/filters'
import { makeRecord } from './fixtures'

const canadian = makeRecord({
  id: 'canada-doctoral',
  title: 'Canada Graduate Research Scholarship',
  country: 'Canada',
  levels: ['PhD'],
  tags: ['Federal'],
  coverage: {
    tuition: { state: 'stated' },
    livingCosts: { state: 'stated' },
    flights: { state: 'unspecified' },
  },
})

const australian = makeRecord({
  id: 'australia-research',
  title: 'Research Training Program Stipend',
  provider: 'Example University',
  country: 'Australia',
  levels: ['Research degree'],
  tags: [],
  coverage: {
    tuition: { state: 'stated' },
    livingCosts: { state: 'stated' },
    flights: { state: 'stated' },
  },
})

const montreal = makeRecord({
  id: 'montreal-tuition',
  title: 'Bourse d’exemption pour personnes étudiantes de l’international',
  provider: 'Université de Montréal',
  country: 'Canada',
  levels: ['PhD'],
  tags: ['Awarded on admission'],
  coverage: {
    tuition: { state: 'stated' },
    livingCosts: { state: 'unspecified' },
    flights: { state: 'unspecified' },
  },
})

const records = [canadian, australian, montreal]

function ids(results: readonly { id: string }[]): string[] {
  return results.map((record) => record.id)
}

describe('scholarship search', () => {
  it('needs every word of the query to appear in the record', () => {
    expect(matchesQuery(canadian, 'doctoral scholarships in Canada')).toBe(true)
    expect(matchesQuery(canadian, 'doctoral scholarships in Australia')).toBe(false)
  })

  it('finds doctoral awards when the visitor types PhD, and the reverse', () => {
    expect(matchesQuery(canadian, 'PhD')).toBe(true)
    expect(matchesQuery(canadian, 'doctorate')).toBe(true)
    expect(matchesQuery(montreal, 'PhD Canada')).toBe(true)
  })

  it('ignores case, accents and apostrophes', () => {
    expect(matchesQuery(montreal, 'universite de montreal')).toBe(true)
    expect(matchesQuery(montreal, 'personnes etudiantes')).toBe(true)
    expect(matchesQuery(montreal, 'bourse dexemption')).toBe(true)
  })
})

describe('scholarship filters', () => {
  it('returns everything when no filter is set', () => {
    expect(ids(filterScholarships(records, EMPTY_FILTERS))).toEqual([
      'canada-doctoral',
      'australia-research',
      'montreal-tuition',
    ])
  })

  it('combines country, level, funding type and query', () => {
    expect(
      ids(
        filterScholarships(records, {
          q: '',
          country: 'Canada',
          level: 'PhD',
          funding: 'Tuition',
        }),
      ),
    ).toEqual(['montreal-tuition'])
  })

  it('matches the derived funding type, not a stored label', () => {
    expect(ids(filterScholarships(records, { ...EMPTY_FILTERS, funding: 'Tuition + stipend' }))).toEqual(
      ['canada-doctoral'],
    )
    expect(ids(filterScholarships(records, { ...EMPTY_FILTERS, funding: 'Fully funded' }))).toEqual([
      'australia-research',
    ])
  })

  it('returns an empty list when nothing matches', () => {
    expect(filterScholarships(records, { ...EMPTY_FILTERS, country: 'Germany' })).toEqual([])
  })
})
