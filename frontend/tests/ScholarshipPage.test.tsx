import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'

import { ActionBar } from '../src/components/ActionBar'
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

  it('marks a record as unpublished and marks passed rounds in the table', () => {
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

    expect(screen.getAllByText('Development preview').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Date passed').length).toBeGreaterThan(0)
  })

  it('shows the navy source-check panel with source, check date and result', () => {
    render(<ScholarshipPage record={fullyFundedRecord} isDevelopment={false} />)

    const aside = screen.getByLabelText('Scholarship details')
    expect(within(aside).getByRole('heading', { level: 3, name: 'Source check' })).toBeVisible()
    expect(within(aside).getByText('27 Oct 2026')).toBeInTheDocument()
    expect(within(aside).getByText('Matches the official page')).toBeInTheDocument()
    expect(
      within(aside).getByRole('link', { name: 'View official source' }),
    ).toHaveAttribute('href', 'https://example.edu/scholarship')
  })

  it('treats a stale published deadline as passed in the round table', () => {
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

    expect(screen.getByText('Date passed')).toBeInTheDocument()
    expect(screen.queryByRole('link', { name: /read the requirements/i })).toBeNull()
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

describe('ActionBar', () => {
  it('shows Read the requirements and Apply on the provider’s site when destinations differ', () => {
    render(<ActionBar record={makeRecord()} isDevelopment />)

    expect(screen.getByRole('link', { name: 'Read the requirements' })).toHaveAttribute(
      'href',
      'https://example.edu/requirements',
    )
    expect(screen.getByRole('link', { name: "Apply on the provider's site" })).toHaveAttribute(
      'href',
      'https://example.edu/apply',
    )
  })

  it('collapses to one action when requirements and application destinations are identical', () => {
    render(
      <ActionBar
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

  it('matches each catalogue record’s application button to its recorded route', () => {
    const expected: Record<string, string | null> = {
      'cgsd-doctoral': null,
      'udem-exemption-doctoral': 'Apply for admission',
      'rmit-research-stipend': null,
      'usyd-rtp-stipend': "Apply on the provider's site",
    }

    for (const record of developmentCatalogue) {
      const { unmount } = render(<ActionBar record={record} isDevelopment />)
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
})
