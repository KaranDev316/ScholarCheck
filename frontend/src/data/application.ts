import { hasOpenRound } from './funding'
import type { Scholarship } from './types'

export interface ApplicationAction {
  href: string
  /** The label states what the link does, so admission is never sold as an application. */
  label: string
  note: string
  /** Admission is a standing next step, not a live application window. */
  emphasised: boolean
}

/**
 * The application call to action follows the recorded route and the published
 * rounds. It is never shown on styling alone:
 *
 * - an unconfirmed route gets no button at all;
 * - a record with no separate scholarship application says “Apply for
 *   admission” and points at the provider's admission page;
 * - a provider route needs an open round, so a record whose deadlines have all
 *   passed gets no button until a round is published again.
 */
export function applicationAction(record: Scholarship): ApplicationAction | null {
  if (record.application.kind === 'confirm') return null

  if (record.application.kind === 'none') {
    return {
      href: record.links.portal,
      label: 'Apply for admission',
      note: 'Opens the provider’s admission page.',
      emphasised: false,
    }
  }

  if (!hasOpenRound(record)) return null

  return {
    href: record.links.portal,
    label: 'Apply now',
    note: 'Opens the provider’s application page.',
    emphasised: true,
  }
}
