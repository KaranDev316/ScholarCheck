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
    expect(screen.getByText(/not source checked yet/i)).toBeInTheDocument()
  })

  it('offers only the requirements link whatever the application route', () => {
    const { unmount } = render(
      <ScholarshipPage
        record={makeRecord({ application: { kind: 'confirm', note: 'No confirmed route yet.' } })}
        isDevelopment
      />,
    )

    expect(screen.getAllByRole('link', { name: /read the requirements/i }).length).toBeGreaterThan(0)
    expect(screen.queryByRole('link', { name: /go to application/i })).toBeNull()

    unmount()

    render(<ScholarshipPage record={fullyFundedRecord} isDevelopment={false} />)
    expect(screen.getAllByRole('link', { name: /read the requirements/i }).length).toBeGreaterThan(0)
    expect(screen.queryByRole('link', { name: /go to application/i })).toBeNull()
  })

  it('keeps the requirements link when another round has a published deadline', () => {
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

    const requirements = screen.getAllByRole('link', { name: 'Read the requirements' })
    expect(requirements.length).toBeGreaterThan(0)
    expect(requirements[0]).toHaveAttribute('href', 'https://example.edu/requirements')
    expect(screen.queryByRole('link', { name: /application/i })).toBeNull()
    expect(screen.getByText(/another round has a published deadline/i)).toBeInTheDocument()
    expect(screen.queryByText(/next round isn’t published yet/i)).toBeNull()
  })

  it('keeps the Sydney RTP record on the requirements link', () => {
    const record = developmentCatalogue.find((item) => item.id === 'usyd-rtp-stipend')
    expect(record).toBeDefined()
    render(<ScholarshipPage record={record!} isDevelopment />)

    expect(screen.getAllByRole('link', { name: 'Read the requirements' })[0]).toHaveAttribute(
      'href',
      'https://www.sydney.edu.au/scholarships/australian-government-research-training-program/rtp-international.html',
    )
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
      'https://example.edu/requirements',
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
