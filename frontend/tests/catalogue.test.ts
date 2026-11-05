import { describe, expect, it } from 'vitest'

import { fundingTypeFor, isFullyFunded } from '../src/data/funding'
import { developmentCatalogue } from '../src/data/developmentCatalogue'
import { getCatalogue } from '../src/data/catalogue'

/**
 * These are content invariants, not behaviour tests: S01 says a record may only
 * claim what its evidence supports, so the previews must stay internally honest.
 */
describe('development catalogue', () => {
  it('holds the four records with unique ids', () => {
    const ids = developmentCatalogue.map((record) => record.id)
    expect(ids).toHaveLength(4)
    expect(new Set(ids).size).toBe(4)
    expect(ids).toEqual([
      'cgsd-doctoral',
      'udem-exemption-doctoral',
      'rmit-research-stipend',
      'usyd-rtp-stipend',
    ])
  })

  it('ships no source-check result and links every reference to real evidence', () => {
    for (const record of developmentCatalogue) {
      expect(record.sourceCheck, record.id).toBeNull()

      const numbers = new Set((record.evidence ?? []).map((item) => item.number))
      const referenced = [
        ...record.components.map((component) => component.evidenceNumber),
        ...record.eligibility.map((statement) => statement.evidenceNumber),
      ].filter((value): value is number => typeof value === 'number')

      expect(referenced.length, record.id).toBeGreaterThan(0)
      for (const number of referenced) {
        expect(numbers.has(number), `${record.id} references evidence ${number}`).toBe(true)
      }
    }
  })

  it('keeps an evidence passage for every numbered source', () => {
    for (const record of developmentCatalogue) {
      for (const item of (record.evidence ?? [])) {
        expect(item.passage.trim(), `${record.id} evidence ${item.number}`).not.toBe('')
        expect(item.url, `${record.id} evidence ${item.number}`).toMatch(/^https:\/\//)
        expect(item.savedAt, `${record.id} evidence ${item.number}`).toMatch(/^\d{4}-\d{2}-\d{2}T/)
      }
    }
  })

  it('only calls a record fully funded when tuition, living costs and flights are all stated', () => {
    for (const record of developmentCatalogue) {
      expect(isFullyFunded(record.coverage), record.id).toBe(false)
      expect(fundingTypeFor(record.coverage), record.id).not.toBe('Fully funded')
    }
  })

  it('keeps the headline in the component that carries it', () => {
    for (const record of developmentCatalogue) {
      const headline = record.headline
      expect(headline, record.id).not.toBeNull()
      if (!headline) continue

      const headlineComponent = record.components.find((component) =>
        component.label.startsWith(headline.component),
      )
      expect(headlineComponent, record.id).toBeDefined()
      expect(headlineComponent?.amount, record.id).toBe(headline.amount)
    }
  })

  it('does not turn RMIT’s full-time stipend wording into a part-time claim', () => {
    const rmit = developmentCatalogue.find((record) => record.id === 'rmit-research-stipend')
    const stipend = rmit?.components.find((component) => component.id === 'rmit-stipend')

    expect(stipend?.basis).toBe('per year, published 2026 rate')
    expect(stipend?.basis).not.toMatch(/part-time/i)
  })

  it('renders the previews in development and an honest empty list in production', () => {
    expect(getCatalogue()).toEqual({ records: developmentCatalogue, isDevelopment: true })
  })
})
