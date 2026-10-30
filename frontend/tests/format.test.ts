import { describe, expect, it } from 'vitest'

import { displayUrl, formatCheckedAgo, formatDate, formatDateTime } from '../src/data/format'

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
