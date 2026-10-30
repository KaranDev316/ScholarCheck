import { developmentCatalogue } from './developmentCatalogue'
import type { Scholarship } from './types'

export interface Catalogue {
  records: readonly Scholarship[]
  /** True while screens show development previews instead of published records. */
  isDevelopment: boolean
}

/**
 * The catalogue the screens render.
 *
 * Roadmap Stage 1, step 2 builds the shell ahead of publication, so development
 * previews stand in for records. They are marked as unpublished on every screen
 * and never reach a production build: outside `vite dev` the public catalogue is
 * honestly empty until the published-only API exists.
 */
export function getCatalogue(): Catalogue {
  if (import.meta.env.DEV) {
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
