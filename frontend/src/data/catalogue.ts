import { developmentCatalogue } from './developmentCatalogue'
import type { Scholarship } from './types'

export interface Catalogue {
  records: readonly Scholarship[]
  /** True while screens show development previews instead of published records. */
  isDevelopment: boolean
}

/** Development previews require explicit opt-in; ordinary runs use the API. */
export function getCatalogue(): Catalogue {
  if (import.meta.env.DEV && import.meta.env.VITE_PREVIEW_DATA === 'true') {
    return { records: developmentCatalogue, isDevelopment: true }
  }

  return { records: [], isDevelopment: false }
}

export function findScholarship(
  records: readonly Scholarship[],
  id: string,
): Scholarship | undefined {
  return records.find((record) => record.id === id)
}

export async function loadCatalogue(signal?: AbortSignal): Promise<Catalogue> {
  const records: Scholarship[] = []
  let total = 1
  while (records.length < total) {
    const response = await fetch(`/api/v1/opportunities?limit=100&offset=${records.length}`, { signal })
    if (!response.ok) throw new Error('Could not load scholarships. Please try again.')
    const body = await response.json() as { records: Scholarship[]; total: number }
    if (!Array.isArray(body.records) || typeof body.total !== 'number') throw new Error('The catalogue response was invalid.')
    total = body.total
    if (!body.records.length) break
    records.push(...body.records)
  }
  return { records, isDevelopment: false }
}
