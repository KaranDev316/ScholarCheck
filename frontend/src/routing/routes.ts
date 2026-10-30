import { parseFundingType, parseStudyLevel, type ScholarshipFilters } from '../data/filters'

/**
 * The product is a single page with three views. Hash routes keep official
 * links (#cgsd-doctoral) and filtered searches (#explore?c=Canada) shareable
 * without adding a router dependency.
 */
export type Route =
  | { name: 'home' }
  | { name: 'explore'; filters: ScholarshipFilters }
  | { name: 'scholarship'; id: string }

export function parseHash(hash: string): Route {
  const raw = hash.replace(/^#/, '')
  if (raw === '' || raw === 'home') return { name: 'home' }

  const [path, queryString = ''] = raw.split('?')

  if (path === 'explore') {
    const params = new URLSearchParams(queryString)
    return {
      name: 'explore',
      filters: {
        q: params.get('q')?.trim() ?? '',
        country: params.get('c') ?? '',
        level: parseStudyLevel(params.get('l') ?? ''),
        funding: parseFundingType(params.get('f') ?? ''),
      },
    }
  }

  return { name: 'scholarship', id: safeDecode(path) }
}

export function exploreHref(filters: Partial<ScholarshipFilters> = {}): string {
  const params = new URLSearchParams()
  if (filters.q) params.set('q', filters.q)
  if (filters.country) params.set('c', filters.country)
  if (filters.level) params.set('l', filters.level)
  if (filters.funding) params.set('f', filters.funding)

  const query = params.toString()
  return query ? `#explore?${query}` : '#explore'
}

export function scholarshipHref(id: string): string {
  return `#${encodeURIComponent(id)}`
}

/** Changes whenever the visible page changes, so a view can remount cleanly. */
export function routeKey(route: Route): string {
  switch (route.name) {
    case 'home':
      return 'home'
    case 'explore':
      return [
        'explore',
        route.filters.q,
        route.filters.country,
        route.filters.level,
        route.filters.funding,
      ].join('|')
    case 'scholarship':
      return `scholarship|${route.id}`
  }
}

function safeDecode(value: string): string {
  try {
    return decodeURIComponent(value)
  } catch {
    return value
  }
}
