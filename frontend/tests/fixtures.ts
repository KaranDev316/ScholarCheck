import type { Scholarship } from '../src/data/types'

/** A minimal record; individual tests override only what they assert on. */
export const baseRecord: Scholarship = {
  id: 'example-doctoral',
  title: 'Example Doctoral Award',
  provider: 'Example University',
  country: 'Canada',
  levels: ['PhD'],
  summary: 'A doctoral award used by the tests.',
  tags: [],
  headline: { component: 'Living allowance', amount: 'CA$20,000', basis: 'per year' },
  coverage: {
    tuition: { state: 'unspecified' },
    livingCosts: { state: 'stated' },
    flights: { state: 'unspecified' },
  },
  components: [
    {
      id: 'example-stipend',
      label: 'Living allowance',
      state: 'stated',
      amount: 'CA$20,000',
      basis: 'per year',
      evidenceNumber: 1,
    },
    {
      id: 'example-tuition',
      label: 'Tuition coverage',
      state: 'unspecified',
      note: 'The source does not mention tuition.',
    },
  ],
  eligibility: [
    {
      id: 'example-doctoral-enrolment',
      statement: 'Be enrolled in a doctoral programme.',
      state: 'stated',
      evidenceNumber: 2,
    },
  ],
  rounds: [
    {
      id: 'example-round',
      round: 'Annual round',
      dateAsPublished: '18 December 2099',
      status: 'Deadline published',
      note: 'Example future deadline.',
    },
  ],
  application: { kind: 'provider', note: 'Apply through the provider.' },
  evidence: [
    {
      number: 1,
      claim: 'Published value',
      passage: 'A stipend of CA$20,000 per year.',
      url: 'https://example.edu/scholarship',
      savedAt: '2026-10-23T07:00:00Z',
    },
    {
      number: 2,
      claim: 'Stated eligibility',
      passage: 'You must be enrolled in a doctoral programme.',
      url: 'https://example.edu/requirements',
      savedAt: '2026-10-23T07:00:00Z',
    },
  ],
  links: {
    summary: 'https://example.edu/scholarship',
    requirements: 'https://example.edu/requirements',
    portal: 'https://example.edu/apply',
  },
  sourceCheck: null,
}

export function makeRecord(overrides: Partial<Scholarship> = {}): Scholarship {
  return { ...baseRecord, ...overrides }
}

/** A record whose three coverage facts are all stated. */
export const fullyFundedRecord = makeRecord({
  id: 'example-fully-funded',
  title: 'Example Fully Funded Award',
  coverage: {
    tuition: { state: 'stated' },
    livingCosts: { state: 'stated' },
    flights: { state: 'stated' },
  },
  sourceCheck: { checkedAt: '2026-10-27T09:30:00Z', result: 'matches' },
})
