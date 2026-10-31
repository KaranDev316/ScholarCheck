import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'

import { ReportDialog } from '../src/components/ReportDialog'
import { developmentCatalogue } from '../src/data/developmentCatalogue'
import { ScholarshipPage } from '../src/pages/ScholarshipPage'
import { fullyFundedRecord, makeRecord } from './fixtures'

describe('ScholarshipPage', () => {
  it('leads with the official title, provider and derived funding type', () => {
    render(<ScholarshipPage record={makeRecord()} isDevelopment />)

    expect(screen.getByRole('heading', { level: 1, name: /example doctoral award/i })).toBeVisible()
    expect(screen.getByText(/example university, canada/i)).toBeInTheDocument()
    expect(screen.getByText('Funding type not established')).toBeInTheDocument()
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

    expect(screen.getByText(/development preview\. this record is not published/i)).toBeInTheDocument()
    expect(screen.getByText(/the published dates \(11 september 2026\) have passed/i)).toBeInTheDocument()
    expect(screen.queryByText(/checked against the official page/i)).toBeNull()
    expect(screen.queryByText(/not source checked yet/i)).toBeNull()
  })

  it('leaves the source-check status off the detail page', () => {
    const { unmount } = render(<ScholarshipPage record={makeRecord()} isDevelopment />)

    expect(screen.queryByText(/checked against the official page/i)).toBeNull()
    expect(screen.queryByText(/not source checked yet/i)).toBeNull()
    expect(screen.queryByText(/confirm with the provider before you apply/i)).toBeNull()

    unmount()

    render(<ScholarshipPage record={fullyFundedRecord} isDevelopment={false} />)
    expect(screen.queryByText(/checked against the official page/i)).toBeNull()
    expect(screen.queryByText(/last checked/i)).toBeNull()
    expect(screen.queryByText(/matches the official page/i)).toBeNull()
  })

  it('puts the official page and Apply now under Rounds and deadlines', () => {
    render(<ScholarshipPage record={makeRecord()} isDevelopment />)

    const heading = screen.getByRole('heading', { level: 2, name: 'Rounds and deadlines' })
    const section = heading.closest('.dsec') as HTMLElement
    expect(section).not.toBeNull()

    const official = within(section).getByRole('link', { name: 'Official page' })
    expect(official).toHaveAttribute('href', 'https://example.edu/requirements')
    expect(
      within(section).getByText(/what the official page says about eligibility and funding/i),
    ).toBeInTheDocument()

    expect(within(section).getByRole('link', { name: 'Apply now' })).toHaveAttribute(
      'href',
      'https://example.edu/apply',
    )

    expect(screen.queryByRole('link', { name: /read the requirements/i })).toBeNull()
  })

  it('keeps the date note and both links when another round has a published deadline', () => {
    render(
      <ScholarshipPage
        record={makeRecord({
          rounds: [
            { id: 'old', round: 'First round', dateAsPublished: '11 September 2026', status: 'Date passed', note: '' },
            { id: 'next', round: 'Second round', dateAsPublished: '18 December 2026', status: 'Deadline published', note: '' },
          ],
        })}
        isDevelopment
      />,
    )

    expect(screen.getByText(/another round has a published deadline/i)).toBeInTheDocument()
    expect(screen.queryByText(/next round isn’t published yet/i)).toBeNull()
    expect(screen.getByRole('link', { name: 'Official page' })).toHaveAttribute(
      'href',
      'https://example.edu/requirements',
    )
    expect(screen.getByRole('link', { name: 'Apply now' })).toHaveAttribute(
      'href',
      'https://example.edu/apply',
    )
  })

  it('links the Sydney RTP record to its official page and its application', () => {
    const record = developmentCatalogue.find((item) => item.id === 'usyd-rtp-stipend')
    expect(record).toBeDefined()
    render(<ScholarshipPage record={record!} isDevelopment />)

    expect(screen.getByRole('link', { name: 'Official page' })).toHaveAttribute(
      'href',
      'https://www.sydney.edu.au/scholarships/australian-government-research-training-program/rtp-international.html',
    )
    expect(screen.getByRole('link', { name: 'Apply now' })).toHaveAttribute(
      'href',
      'https://sydneyuniversity.formstack.com/forms/rtpapp',
    )
  })

  it('withholds the application button while the route is unconfirmed', () => {
    render(
      <ScholarshipPage
        record={makeRecord({ application: { kind: 'confirm', note: 'No confirmed route yet.' } })}
        isDevelopment
      />,
    )

    expect(screen.getByRole('link', { name: 'Official page' })).toBeInTheDocument()
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
    expect(screen.queryByRole('link', { name: 'Apply now' })).toBeNull()
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

    expect(screen.getByRole('link', { name: 'Official page' })).toBeInTheDocument()
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

    expect(screen.getByText(/the published dates \(18 december 2020\) have passed/i)).toBeInTheDocument()
    expect(screen.getByText('Date passed')).toBeInTheDocument()
    expect(screen.queryByRole('link', { name: /apply/i })).toBeNull()
  })

  it('matches each catalogue record’s application button to its recorded route', () => {
    const expected: Record<string, string | null> = {
      // Route unconfirmed: the note is shown, but no button.
      'cgsd-doctoral': null,
      // No separate scholarship application: admission is the next step.
      'udem-exemption-doctoral': 'Apply for admission',
      // Every listed deadline has passed: no button until a round is published.
      'rmit-research-stipend': null,
      'usyd-rtp-stipend': 'Apply now',
    }

    expect(developmentCatalogue.map((record) => record.id).sort()).toEqual(Object.keys(expected).sort())

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

  it('lists eligibility as a numbered list with no evidence links', () => {
    render(<ScholarshipPage record={makeRecord()} isDevelopment />)

    expect(screen.getByRole('heading', { level: 2, name: 'Eligibility' })).toBeVisible()
    expect(screen.getByText(/this isn’t a decision about you or a chance of award/i)).toBeInTheDocument()

    const items = screen.getAllByRole('listitem')
    expect(items).toHaveLength(1)
    expect(items[0]).toHaveTextContent('Be enrolled in a doctoral programme.')
    expect(within(items[0]).queryByRole('link')).toBeNull()
  })

  it('keeps the quoted passages, source addresses and saved dates off the page', () => {
    render(<ScholarshipPage record={makeRecord()} isDevelopment />)

    expect(screen.getAllByRole('link').map((link) => link.getAttribute('href'))).toEqual([
      '#explore',
      'https://example.edu/requirements',
      'https://example.edu/apply',
    ])
    expect(screen.queryByText(/open the official page/i)).toBeNull()
    expect(screen.queryByText(/^source:/i)).toBeNull()
    expect(screen.queryByText(/^saved:/i)).toBeNull()
    expect(screen.queryByText(/a stipend of CA\$20,000 per year/i)).toBeNull()
    expect(screen.queryByRole('button', { name: /evidence/i })).toBeNull()
  })

  it('reports a problem without pretending the report was sent', async () => {
    const user = userEvent.setup()
    render(<ScholarshipPage record={makeRecord()} isDevelopment />)

    await user.click(screen.getAllByRole('button', { name: /report a problem/i })[0])
    const dialog = screen.getByRole('dialog', { name: /report a problem/i })
    await user.click(within(dialog).getByRole('button', { name: /send report/i }))

    expect(screen.queryByRole('dialog')).toBeNull()
    expect(screen.getByRole('status')).toHaveTextContent(
      /reports are not being collected yet, so nothing was sent/i,
    )
  })
})

describe('ReportDialog', () => {
  it('names the record and offers the usual reasons', () => {
    render(
      <ReportDialog scholarshipTitle="Example Doctoral Award" open onClose={() => {}} onSend={() => {}} />,
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
})
