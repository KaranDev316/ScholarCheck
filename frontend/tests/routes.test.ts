import { describe, expect, it } from 'vitest'

import { EMPTY_FILTERS } from '../src/data/filters'
import { exploreHref, parseHash, routeKey, scholarshipHref } from '../src/routing/routes'

describe('hash routes', () => {
  it('treats an empty hash as the home page', () => {
    expect(parseHash('')).toEqual({ name: 'home' })
    expect(parseHash('#home')).toEqual({ name: 'home' })
  })

  it('reads filters out of an explore link', () => {
    expect(parseHash('#explore?q=doctoral&c=Canada&l=PhD&f=Tuition')).toEqual({
      name: 'explore',
      filters: { q: 'doctoral', country: 'Canada', level: 'PhD', funding: 'Tuition' },
    })
  })

  it('replaces unknown filter values with "all" instead of failing', () => {
    expect(parseHash('#explore?l=Diploma&f=Gold')).toEqual({
      name: 'explore',
      filters: EMPTY_FILTERS,
    })
  })

  it('falls back to the home page filters for a bare explore link', () => {
    expect(parseHash('#explore')).toEqual({ name: 'explore', filters: EMPTY_FILTERS })
  })

  it('treats any other hash as a record id', () => {
    expect(parseHash('#cgsd-doctoral')).toEqual({ name: 'scholarship', id: 'cgsd-doctoral' })
    expect(parseHash('#usyd-rtp-stipend')).toEqual({ name: 'scholarship', id: 'usyd-rtp-stipend' })
  })
})

describe('link building', () => {
  it('round-trips filters through the URL', () => {
    const href = exploreHref({ ...EMPTY_FILTERS, q: 'doctoral', country: 'Canada' })
    expect(href).toBe('#explore?q=doctoral&c=Canada')
    expect(parseHash(href)).toEqual({
      name: 'explore',
      filters: { ...EMPTY_FILTERS, q: 'doctoral', country: 'Canada' },
    })
  })

  it('omits unused parameters', () => {
    expect(exploreHref()).toBe('#explore')
    expect(scholarshipHref('rmit-research-stipend')).toBe('#rmit-research-stipend')
  })

  it('changes the route key when the filters change', () => {
    expect(routeKey({ name: 'home' })).toBe('home')
    expect(routeKey(parseHash('#explore?c=Canada'))).not.toBe(routeKey(parseHash('#explore')))
    expect(routeKey(parseHash('#explore'))).toBe(routeKey(parseHash('#explore')))
  })
})
