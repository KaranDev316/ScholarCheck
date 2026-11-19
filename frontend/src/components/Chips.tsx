import type { ReactNode } from 'react'

import type { FactState } from '../data/types'
import { UnknownBadge } from './UnknownBadge'

/**
 * Chips carry a word as well as a colour, so a fact's support is readable
 * without relying on colour alone.
 */
export function FactChip({ state }: { state: FactState }) {
  if (state === 'stated') return <span className="status-covered">Stated in source</span>
  if (state === 'conflicting') return <span className="chip conflict">Sources conflict</span>
  return <UnknownBadge label="Not specified" />
}

/** Coverage rows use the plain "Covered" / "Not stated" wording. */
export function CoverageChip({ state }: { state: FactState }) {
  if (state === 'stated') return <span className="status-covered">Covered</span>
  if (state === 'conflicting') return <span className="chip conflict">Sources conflict</span>
  return <UnknownBadge label="Not stated" />
}

export function TagChip({ children }: { children: ReactNode }) {
  return <span className="tag">{children}</span>
}

export function TextChip({ children }: { children: ReactNode }) {
  return <span className="tag">{children}</span>
}
