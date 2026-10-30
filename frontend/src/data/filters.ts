import { fundingTypeFor } from './funding'
import {
  FUNDING_TYPES,
  STUDY_LEVELS,
  type FundingType,
  type Scholarship,
  type StudyLevel,
} from './types'

export interface ScholarshipFilters {
  q: string
  country: string
  level: StudyLevel | ''
  funding: FundingType | ''
}

export const EMPTY_FILTERS: ScholarshipFilters = {
  q: '',
  country: '',
  level: '',
  funding: '',
}

/** Select values arrive as plain strings; anything unrecognised means "all". */
export function parseStudyLevel(value: string): StudyLevel | '' {
  return (STUDY_LEVELS as readonly string[]).includes(value) ? (value as StudyLevel) : ''
}

export function parseFundingType(value: string): FundingType | '' {
  return (FUNDING_TYPES as readonly string[]).includes(value) ? (value as FundingType) : ''
}

export function availableCountries(records: readonly Scholarship[]): string[] {
  return [...new Set(records.map((record) => record.country))].sort((a, b) => a.localeCompare(b))
}

/** Case-, accent- and apostrophe-insensitive form used by search. */
function normalise(value: string): string {
  return value
    .normalize('NFD')
    .replace(/\p{Diacritic}/gu, '')
    .replace(/['\u2019]/g, '')
    .toLowerCase()
}

function searchText(record: Scholarship): string {
  // "PhD" should also be found by the words visitors actually type.
  const levelWords = record.levels.includes('PhD')
    ? `${record.levels.join(' ')} doctoral doctorate`
    : record.levels.join(' ')

  return normalise(
    [
      record.title,
      record.provider,
      record.country,
      record.summary,
      record.levels.join(' '),
      record.tags.join(' '),
      'scholarship scholarships',
      levelWords,
    ].join(' '),
  )
}

/**
 * Every meaningful word of the query must appear somewhere in the record, so
 * "doctoral scholarships in Canada" finds a Canadian doctoral award. Short
 * linking words are dropped, because no record is expected to contain them.
 */
const STOP_WORDS = new Set([
  'a',
  'an',
  'and',
  'at',
  'for',
  'in',
  'of',
  'on',
  'the',
  'to',
  'with',
])

export function matchesQuery(record: Scholarship, query: string): boolean {
  const tokens = normalise(query)
    .split(/\s+/)
    .map((token) => token.replace(/[^\p{L}\p{N}]+/gu, ''))
    .filter(Boolean)

  if (tokens.length === 0) return true

  const meaningful = tokens.filter((token) => !STOP_WORDS.has(token))
  const required = meaningful.length > 0 ? meaningful : tokens

  const haystack = searchText(record)
  return required.every((token) => haystack.includes(token))
}

export function filterScholarships(
  records: readonly Scholarship[],
  filters: ScholarshipFilters,
): Scholarship[] {
  return records.filter((record) => {
    if (filters.country && record.country !== filters.country) return false
    if (filters.level && !record.levels.includes(filters.level)) return false
    if (filters.funding && fundingTypeFor(record.coverage) !== filters.funding) return false
    return matchesQuery(record, filters.q)
  })
}

export function hasActiveFilters(filters: ScholarshipFilters): boolean {
  return Boolean(filters.q || filters.country || filters.level || filters.funding)
}
