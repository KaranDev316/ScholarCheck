import { describe, expect, it } from 'vitest'

import {
  displayUrl,
  formatAward,
  formatCheckedAgo,
  formatDate,
  formatDateTime,
  formatScholarshipSummary,
} from '../src/data/format'
import { makeRecord } from './fixtures'

describe('date formatting', () => {
  it('formats dates in UTC so a saved copy never shifts a day', () => {
    expect(formatDate('2026-10-23T23:30:00Z')).toBe('23 October 2026')
    const timestamp = formatDateTime('2026-10-23T07:00:00Z')
    expect(timestamp).toContain('23 October 2026')
    expect(timestamp).toContain('07:00 UTC')
  })

  it('describes an unreadable date without inventing one', () => {
    expect(formatDate('not a date')).toBe('an unknown date')
    expect(formatDateTime('not a date')).toBe('an unknown time')
  })
})

describe('checked-ago wording', () => {
  const now = new Date('2026-10-30T12:00:00Z')

  it('counts whole days since the check', () => {
    expect(formatCheckedAgo('2026-10-30T09:00:00Z', now)).toBe('today')
    expect(formatCheckedAgo('2026-10-29T09:00:00Z', now)).toBe('1 day ago')
    expect(formatCheckedAgo('2026-10-27T09:00:00Z', now)).toBe('3 days ago')
  })

  it('does not report a negative age when the clock is skewed', () => {
    expect(formatCheckedAgo('2026-11-01T09:00:00Z', now)).toBe('today')
  })
})

describe('displayUrl', () => {
  it('drops the scheme so the source reads as an address', () => {
    expect(displayUrl('https://example.edu/awards/doctoral')).toBe('example.edu/awards/doctoral')
  })
})

describe('formatAward', () => {
  it('formats known currency with separate amount and period qualifiers', () => {
    const result = formatAward(40000, 'CAD', 'per year')
    expect(result).toEqual({
      amountText: 'CAD $40,000',
      inlineText: 'CAD $40,000 / year',
      qualifierText: 'per year',
      currencyNote: null,
    })
  })

  it('formats unknown currency without inline placeholder and adds a muted note', () => {
    const result = formatAward('40,000 (currency not stated)', null, 'per year for 36 months')
    expect(result).toEqual({
      amountText: '$40,000',
      inlineText: '$40,000 / year',
      qualifierText: 'per year for 36 months',
      currencyNote: 'Currency per source',
    })
  })

  it('preserves prefixes like Up to and decimal precision', () => {
    expect(formatAward('Up to 1,540', 'AUD', 'one-off payment')).toEqual({
      amountText: 'Up to AUD $1,540',
      inlineText: 'Up to AUD $1,540',
      qualifierText: 'one-off payment',
      currencyNote: null,
    })
    expect(formatAward('24,067.80', null, 'annual reduction')).toEqual({
      amountText: '$24,067.80',
      inlineText: '$24,067.80 / year',
      qualifierText: 'annual reduction',
      currencyNote: 'Currency per source',
    })
  })
})

describe('formatScholarshipSummary', () => {
  it('keeps card descriptions aligned with headline currency and amount', () => {
    const unknown = makeRecord({
      currency: null,
      summary: 'The source lists $40,000 per year for 36 months.',
      headline: { component: 'Award component', amount: '40,000', currency: null, basis: 'per year' },
    })
    expect(formatScholarshipSummary(unknown)).toBe('The source lists $40,000 / year for 36 months.')

    const known = makeRecord({
      currency: 'CAD',
      summary: 'The source lists $40,000 per year for 36 months.',
      headline: { component: 'Award component', amount: '40,000', currency: 'CAD', basis: 'per year' },
    })
    expect(formatScholarshipSummary(known)).toBe(
      'The source lists CAD $40,000 / year for 36 months.',
    )
  })
})
