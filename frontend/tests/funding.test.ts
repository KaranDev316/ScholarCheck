import { describe, expect, it } from 'vitest'

import { isCovered, isFullyFunded, fundingTypeFor, passedRoundDates } from '../src/data/funding'
import { makeRecord } from './fixtures'

describe('funding rules', () => {
  it('treats only stated facts as covered', () => {
    expect(isCovered('stated')).toBe(true)
    expect(isCovered('unspecified')).toBe(false)
    expect(isCovered('conflicting')).toBe(false)
  })

  it('needs all three coverage facts before calling a record fully funded', () => {
    expect(
      isFullyFunded({
        tuition: { state: 'stated' },
        livingCosts: { state: 'stated' },
        flights: { state: 'unspecified' },
      }),
    ).toBe(false)

    expect(
      isFullyFunded({
        tuition: { state: 'stated' },
        livingCosts: { state: 'stated' },
        flights: { state: 'stated' },
      }),
    ).toBe(true)
  })

  it('derives the funding type from coverage instead of trusting a label', () => {
    expect(
      fundingTypeFor({
        tuition: { state: 'stated' },
        livingCosts: { state: 'stated' },
        flights: { state: 'stated' },
      }),
    ).toBe('Fully funded')

    expect(
      fundingTypeFor({
        tuition: { state: 'stated' },
        livingCosts: { state: 'stated' },
        flights: { state: 'conflicting' },
      }),
    ).toBe('Tuition + stipend')

    expect(
      fundingTypeFor({
        tuition: { state: 'stated' },
        livingCosts: { state: 'unspecified' },
        flights: { state: 'unspecified' },
      }),
    ).toBe('Tuition')

    expect(
      fundingTypeFor({
        tuition: { state: 'unspecified' },
        livingCosts: { state: 'stated' },
        flights: { state: 'unspecified' },
      }),
    ).toBeNull()
  })

  it('reports only the rounds whose published status says they passed', () => {
    const record = makeRecord({
      rounds: [
        { id: 'a', round: 'Round A', dateAsPublished: '11 September 2026', status: 'Date passed', note: '' },
        {
          id: 'b',
          round: 'Round B',
          dateAsPublished: '18 December 2026',
          status: 'Deadline published',
          note: '',
        },
      ],
    })

    expect(passedRoundDates(record)).toEqual(['11 September 2026'])
  })
})
