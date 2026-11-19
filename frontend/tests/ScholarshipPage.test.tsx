import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'

import { ReportDialog } from '../src/components/ReportDialog'
import { developmentCatalogue } from '../src/data/developmentCatalogue'
import { ScholarshipPage } from '../src/pages/ScholarshipPage'
import { fullyFundedRecord, makeRecord } from './fixtures'

describe('ScholarshipPage', () => {
  it('leads with the breadcrumb, official title, provider and omits unestablished funding tags', () => {
    render(<ScholarshipPage record={makeRecord()} isDevelopment />)

    const breadcrumb = screen.getByRole('navigation', { name: /breadcrumb/i })
    expect(within(breadcrumb).getByRole('link', { name: 'Find scholarships' })).toHaveAttribute(
      'href',
      '#explore',
    )
    expect(screen.getByRole('heading', { level: 1, name: /example doctoral award/i })).toBeVisible()
    expect(screen.getByText(/example university, canada/i)).toBeInTheDocument()
    expect(screen.queryByText('Funding type not established')).toBeNull()
  })

  it('shows each coverage fact with the wording the source uses', () => {
    render(<ScholarshipPage record={makeRecord()} isDevelopment />)

    expect(screen.getByText('Living costs', { selector: 'span' })).toBeInTheDocument()
    expect(screen.getByText('Flights', { selector: 'span' })).toBeInTheDocument()
    expect(screen.getAllByText('Not stated')).toHaveLength(2)
    expect(screen.getAllByText('Covered')).toHaveLength(1)
  })

  it('never adds the components up into a total', () => {
    render(<ScholarshipPage record={makeRecord()} isDevelopment />)

    expect(screen.getByRole('heading', { level: 2, name: /funding components/i })).toBeVisible()
    expect(screen.getByText(/we never add them together or call one a total/i)).toBeInTheDocument()
  })

  it('uses the shared award format on the detail strip and component cards', () => {
    const unknown = makeRecord({
      currency: null,
      headline: {
        component: 'Living allowance',
        amount: '40,000',
        currency: null,
        basis: 'per year for 36 months',
      },
      components: [
        {
          id: 'cgsd-living-support',
          label: 'Living allowance',
          state: 'stated',
          amount: '40,000',
          currency: null,
          basis: 'per year for 36 months',
          evidenceNumber: 1,
        },
      ],
    })
    render(<ScholarshipPage record={unknown} isDevelopment={false} />)

    expect(screen.getAllByText('$40,000')).toHaveLength(2)
    expect(screen.getAllByText('per year for 36 months')).toHaveLength(2)
    expect(screen.getAllByText('Currency not stated')).toHaveLength(2)
  })

  it('formats the detail-page source-checked date unambiguously as 3 Nov 2026', () => {
    render(
      <ScholarshipPage
        record={makeRecord({
          sourceCheck: { checkedAt: '2026-11-03T18:40:32Z', result: 'matches' },
        })}
        isDevelopment={false}
      />,
    )

    expect(screen.getByText(/source checked 3 Nov 2026/i)).toBeInTheDocument()
    expect(screen.queryByText(/03\/11\/2026/)).toBeNull()
  })

  it('marks a record as unpublished and says the dates passed', () => {
    render(
      <ScholarshipPage
        record={makeRecord({
          rounds: [
            {
              id: 'passed',
              round: 'Annual round',
              dateAsPublished: '11 September 2026',
              status: 'Date passed',
              note: 'Next round not published.',
            },
          ],
        })}
        isDevelopment
      />,
    )

    expect(
      screen.getByText(/development preview\. this record is not published/i),
    ).toBeInTheDocument()
    expect(
      screen.getByText(/the published dates \(11 september 2026\) have passed/i),
    ).toBeInTheDocument()
  })

  it('shows the navy source-check panel with source, check date and result', () => {
    render(<ScholarshipPage record={fullyFundedRecord} isDevelopment={false} />)

    const aside = screen.getByLabelText('Scholarship details')
    expect(within(aside).getByRole('heading', { level: 3, name: 'Source check' })).toBeVisible()
    expect(within(aside).getByText('27 Oct 2026')).toBeInTheDocument()
    expect(within(aside).getByText('Matches the official page')).toBeInTheDocument()
    expect(
      within(aside).getByRole('link', { name: 'example.edu/scholarship' }),
    ).toHaveAttribute('href', 'https://example.edu/scholarship')
  })

  it('shows Read the requirements and Apply on the provider’s site when destinations differ', () => {
    render(<ScholarshipPage record={makeRecord()} isDevelopment />)

    const official = screen.getByRole('link', { name: 'Read the requirements' })
    expect(official).toHaveAttribute('href', 'https://example.edu/requirements')
    expect(
      screen.getByText(/what the official page says about eligibility and funding/i),
    ).toBeInTheDocument()

    expect(
      screen.getByRole('link', { name: "Apply on the provider's site" }),
    ).toHaveAttribute('href', 'https://example.edu/apply')
  })

  it('collapses to one action when requirements and application destinations are identical', () => {
    render(
      <ScholarshipPage
        record={makeRecord({
          links: {
            summary: 'https://example.edu/scholarship',
            requirements: 'https://example.edu/requirements',
            portal: 'https://example.edu/requirements',
          },
        })}
        isDevelopment={false}
      />,
    )

    expect(screen.getByRole('link', { name: 'Read the requirements' })).toHaveAttribute(
      'href',
      'https://example.edu/requirements',
    )
    expect(screen.queryByRole('link', { name: /apply/i })).toBeNull()
  })

  it('keeps the date note and both links when another round has a published deadline', () => {
    render(
      <ScholarshipPage
        record={makeRecord({
          rounds: [
            {
              id: 'old',
              round: 'First round',
              dateAsPublished: '11 September 2026',
              status: 'Date passed',
              note: '',
            },
            {
              id: 'next',
              round: 'Second round',
              dateAsPublished: '18 December 2026',
              status: 'Deadline published',
              note: '',
            },
          ],
        })}
        isDevelopment
      />,
    )

    expect(screen.getByText(/another round has a published deadline/i)).toBeInTheDocument()
    expect(screen.queryByText(/next round isn’t published yet/i)).toBeNull()
    expect(screen.getByRole('link', { name: 'Read the requirements' })).toHaveAttribute(
      'href',
      'https://example.edu/requirements',
    )
    expect(
      screen.getByRole('link', { name: "Apply on the provider's site" }),
    ).toHaveAttribute('href', 'https://example.edu/apply')
  })

  it('links the Sydney RTP record to its requirements page and its application', () => {
    const record = developmentCatalogue.find((item) => item.id === 'usyd-rtp-stipend')
    expect(record).toBeDefined()
    render(<ScholarshipPage record={record!} isDevelopment />)

    expect(screen.getByRole('link', { name: 'Read the requirements' })).toHaveAttribute(
      'href',
      'https://www.sydney.edu.au/scholarships/australian-government-research-training-program/rtp-international.html',
    )
    expect(
      screen.getByRole('link', { name: "Apply on the provider's site" }),
    ).toHaveAttribute('href', 'https://sydneyuniversity.formstack.com/forms/rtpapp')
  })

  it('withholds the application button while the route is unconfirmed', () => {
    render(
      <ScholarshipPage
        record={makeRecord({ application: { kind: 'confirm', note: 'No confirmed route yet.' } })}
        isDevelopment
      />,
    )

    expect(screen.getByRole('link', { name: 'Read the requirements' })).toBeInTheDocument()
    expect(screen.queryByRole('link', { name: /apply/i })).toBeNull()
  })

  it('says Apply for admission when there is no separate scholarship application', () => {
    render(
      <ScholarshipPage
        record={makeRecord({
          application: {
            kind: 'none',
            note: 'The source states no separate scholarship application. Apply for admission instead.',
          },
        })}
        isDevelopment
      />,
    )

    expect(screen.getByRole('link', { name: 'Apply for admission' })).toHaveAttribute(
      'href',
      'https://example.edu/apply',
    )
    expect(screen.queryByRole('link', { name: "Apply on the provider's site" })).toBeNull()
  })

  it('withholds the application button once every listed deadline has passed', () => {
    render(
      <ScholarshipPage
        record={makeRecord({
          rounds: [
            {
              id: 'passed',
              round: 'Annual round',
              dateAsPublished: '11 September 2026',
              status: 'Date passed',
              note: 'Next round not published.',
            },
          ],
        })}
        isDevelopment
      />,
    )

    expect(screen.getByRole('link', { name: 'Read the requirements' })).toBeInTheDocument()
    expect(screen.queryByRole('link', { name: /apply/i })).toBeNull()
  })

  it('treats a stale published deadline as passed on the detail page', () => {
    render(
      <ScholarshipPage
        record={makeRecord({
          rounds: [
            {
              id: 'stale',
              round: 'Old round',
              dateAsPublished: '18 December 2020',
              status: 'Deadline published',
              note: '',
            },
          ],
        })}
        isDevelopment
      />,
    )

    expect(
      screen.getByText(/the published dates \(18 december 2020\) have passed/i),
    ).toBeInTheDocument()
    expect(screen.getByText('Date passed')).toBeInTheDocument()
    expect(screen.queryByRole('link', { name: /apply/i })).toBeNull()
  })

  it('matches each catalogue record’s application button to its recorded route', () => {
    const expected: Record<string, string | null> = {
      'cgsd-doctoral': null,
      'udem-exemption-doctoral': 'Apply for admission',
      'rmit-research-stipend': null,
      'usyd-rtp-stipend': "Apply on the provider's site",
    }

    expect(developmentCatalogue.map((record) => record.id).sort()).toEqual(
      Object.keys(expected).sort(),
    )

    for (const record of developmentCatalogue) {
      const { unmount } = render(<ScholarshipPage record={record} isDevelopment />)
      const label = expected[record.id]

      if (label === null) {
        expect(screen.queryByRole('link', { name: /apply/i })).toBeNull()
      } else {
        expect(screen.getByRole('link', { name: label })).toHaveAttribute(
          'href',
          record.links.portal,
        )
      }

      unmount()
    }
  })

  it('lists stated eligibility with the required disclaimer', () => {
    render(<ScholarshipPage record={makeRecord()} isDevelopment />)

    expect(screen.getByRole('heading', { level: 2, name: 'Eligibility' })).toBeVisible()
    expect(
      screen.getByText(/these are the provider’s stated requirements, not a decision about you\./i),
    ).toBeInTheDocument()

    const items = screen.getAllByRole('listitem')
    expect(items).toHaveLength(1)
    expect(items[0]).toHaveTextContent('Be enrolled in a doctoral programme.')
  })

  it('shows exact retained evidence passages, source links, saved dates and match result', () => {
    render(<ScholarshipPage record={makeRecord()} isDevelopment={false} />)

    expect(screen.getByRole('heading', { level: 2, name: /official evidence/i })).toBeVisible()
    expect(screen.getByText(/a stipend of CA\$20,000 per year\./i)).toBeInTheDocument()
    expect(screen.getAllByText(/saved 23 Oct 2026/i)).toHaveLength(2)
    expect(screen.getAllByText('Matches the official page').length).toBeGreaterThan(0)
  })

  it('reports a problem without pretending the report was sent', async () => {
    const user = userEvent.setup()
    render(<ScholarshipPage record={makeRecord()} isDevelopment />)

    await user.click(screen.getAllByRole('button', { name: /report a problem/i })[0])
    const dialog = screen.getByRole('dialog', { name: /report a problem/i })
    await user.click(within(dialog).getByRole('button', { name: /send report/i }))

    expect(screen.getByRole('dialog')).toBeInTheDocument()
    expect(screen.getByRole('alert')).toHaveTextContent(
      /development previews cannot receive reports/i,
    )
  })
})

describe('ReportDialog', () => {
  it('names the record and offers the usual reasons', () => {
    render(
      <ReportDialog
        scholarshipTitle="Example Doctoral Award"
        open
        onClose={() => {}}
        onSend={() => {}}
      />,
    )

    const dialog = screen.getByRole('dialog', { name: /report a problem/i })
    expect(within(dialog).getByText(/about: example doctoral award/i)).toBeInTheDocument()
    expect(within(dialog).getByLabelText(/what looks wrong/i)).toBeInTheDocument()
    expect(within(dialog).getByText(/we don’t ask for your name or email/i)).toBeInTheDocument()
  })

  it('can be dismissed without sending anything', async () => {
    const user = userEvent.setup()
    let closed = false
    render(
      <ReportDialog
        scholarshipTitle="Example Doctoral Award"
        open
        onClose={() => {
          closed = true
        }}
        onSend={() => {}}
      />,
    )

    await user.click(screen.getByRole('button', { name: /cancel/i }))
    expect(closed).toBe(true)
  })

  it('traps focus inside the dialog, closes on Escape and returns focus to the trigger', async () => {
    const user = userEvent.setup()
    render(<ScholarshipPage record={makeRecord()} isDevelopment />)

    const trigger = screen.getByRole('button', { name: /report a problem/i })
    trigger.focus()
    await user.click(trigger)

    const dialog = screen.getByRole('dialog', { name: /report a problem/i })
    const select = within(dialog).getByLabelText(/what looks wrong/i)
    const cancel = within(dialog).getByRole('button', { name: /cancel/i })

    expect(select).toHaveFocus()
    cancel.focus()
    await user.keyboard('{Tab}')
    expect(select).toHaveFocus()

    await user.keyboard('{Shift>}{Tab}{/Shift}')
    expect(cancel).toHaveFocus()

    await user.keyboard('{Escape}')
    expect(screen.queryByRole('dialog')).toBeNull()
    expect(trigger).toHaveFocus()
  })
})
