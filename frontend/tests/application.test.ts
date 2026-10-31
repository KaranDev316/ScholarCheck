import { describe, expect, it } from 'vitest'

import { applicationAction } from '../src/data/application'
import { makeRecord } from './fixtures'

const passedRound = {
  id: 'passed',
  round: 'Annual round',
  dateAsPublished: '11 September 2026',
  status: 'Date passed',
  note: '',
}

const openRound = {
  id: 'open',
  round: 'Next round',
  dateAsPublished: '18 December 2026',
  status: 'Deadline published',
  note: '',
}

describe('application action', () => {
  it('offers Apply now only for a provider route with a round still open', () => {
    const action = applicationAction(
      makeRecord({
        application: { kind: 'provider', note: 'Apply through the provider.' },
        rounds: [passedRound, openRound],
      }),
    )

    expect(action).toEqual({
      href: 'https://example.edu/apply',
      label: 'Apply now',
      note: 'Opens the provider’s application page.',
      emphasised: true,
    })
  })

  it('withholds the button while the application route is unconfirmed', () => {
    expect(
      applicationAction(
        makeRecord({
          application: { kind: 'confirm', note: 'No confirmed application route yet.' },
          rounds: [openRound],
        }),
      ),
    ).toBeNull()
  })

  it('withholds the button when every listed deadline has passed', () => {
    expect(
      applicationAction(
        makeRecord({
          application: { kind: 'provider', note: 'Apply through the provider.' },
          rounds: [passedRound],
        }),
      ),
    ).toBeNull()

    expect(
      applicationAction(
        makeRecord({ application: { kind: 'provider', note: '' }, rounds: [] }),
      ),
    ).toBeNull()
  })

  it('says Apply for admission when there is no separate scholarship application', () => {
    const action = applicationAction(
      makeRecord({
        application: {
          kind: 'none',
          note: 'The source states no separate scholarship application. Apply for admission instead.',
        },
        rounds: [openRound],
      }),
    )

    expect(action).toEqual({
      href: 'https://example.edu/apply',
      label: 'Apply for admission',
      note: 'Opens the provider’s admission page.',
      emphasised: false,
    })
  })

  it('keeps the admission step on a passed round, because admission is always the route', () => {
    expect(
      applicationAction(
        makeRecord({
          application: { kind: 'none', note: 'Apply for admission instead.' },
          rounds: [passedRound],
        }),
      )?.label,
    ).toBe('Apply for admission')
  })
})
