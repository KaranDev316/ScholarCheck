import type { ReactNode } from 'react'

import type { FactState } from '../data/types'

/**
 * Chips carry a word as well as a colour, so a fact's support is readable
 * without relying on colour alone.
 */
export function FactChip({ state }: { state: FactState }) {
  if (state === 'stated') return <span className="chip stated">Stated in source</span>
  if (state === 'conflicting') return <span className="chip conflict">Sources conflict</span>
  return <span className="chip unspec">Not specified</span>
}

/** Coverage rows use the plain "Covered" / "Not stated" wording. */
export function CoverageChip({ state }: { state: FactState }) {
  if (state === 'stated') return <span className="chip stated">Covered</span>
  if (state === 'conflicting') return <span className="chip conflict">Sources conflict</span>
  return <span className="chip unspec">Not stated</span>
}

export function TagChip({ children }: { children: ReactNode }) {
  return <span className="chip neutral">{children}</span>
}

export function TextChip({ children }: { children: ReactNode }) {
  return <span className="chip">{children}</span>
}
