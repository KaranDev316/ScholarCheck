import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { makeRecord } from './fixtures'

vi.mock('../src/data/catalogue', async (original) => {
  const actual = await original<typeof import('../src/data/catalogue')>()
  return { ...actual, getCatalogue: () => ({ records: [], isDevelopment: false }) }
})
import App from '../src/App'
import { ScholarshipPage } from '../src/pages/ScholarshipPage'

const record = makeRecord({ sourceCheck: { checkedAt: '2026-11-03T12:00:00Z', result: 'matches' } })
function reply(body: unknown, status = 200) { return Promise.resolve(new Response(JSON.stringify(body), { status })) }

describe('Public journeys', () => {
  beforeEach(() => { window.history.replaceState(null, '', '#explore') })
  afterEach(() => { vi.unstubAllGlobals() })

  it('loads the public catalogue, shows a real check date and hides evidence', async () => {
    vi.stubGlobal('fetch', vi.fn((url: string) => url === '/api/site' ? reply({ contactEmail: 'owner@scholarcheck.test' }) : reply({ records: [record], total: 1 })))
    render(<App />)
    expect(screen.getByText('Loading scholarships…')).toBeInTheDocument()
    expect(await screen.findByText(record.title)).toBeInTheDocument()
    expect(screen.queryByText(/development preview/i)).toBeNull()
    expect(await screen.findByRole('link', { name: 'Contact ScholarCheck' })).toHaveAttribute('href', 'mailto:owner@scholarcheck.test')
  })

  it('keeps an actionable retry when the API is unavailable', async () => {
    let failed = true
    vi.stubGlobal('fetch', vi.fn((url: string) => url === '/api/site' ? reply({}) : failed ? reply({}, 503) : reply({ records: [], total: 0 })))
    render(<App />)
    expect(await screen.findByRole('alert')).toHaveTextContent(/could not load scholarships/i)
    failed = false
    await userEvent.click(screen.getByRole('button', { name: 'Try again' }))
    await waitFor(() => expect(screen.queryByRole('alert')).toBeNull())
    expect(screen.queryByText('Loading scholarships…')).toBeNull()
  })

  it('retains report details on failure and confirms only after server acceptance', async () => {
    const user = userEvent.setup()
    const fetcher = vi.fn().mockImplementationOnce(() => reply({}, 503)).mockImplementationOnce(() => reply({ id: 'accepted' }, 202))
    vi.stubGlobal('fetch', fetcher)
    render(<ScholarshipPage record={record} isDevelopment={false} />)
    await user.click(screen.getByRole('button', { name: 'Report a problem' }))
    const dialog = screen.getByRole('dialog')
    await user.type(within(dialog).getByLabelText('Details (optional)'), 'Please check the year.')
    await user.click(within(dialog).getByRole('button', { name: 'Send report' }))
    expect(await within(dialog).findByRole('alert')).toHaveTextContent(/could not send/i)
    expect(within(dialog).getByLabelText('Details (optional)')).toHaveValue('Please check the year.')
    await user.click(within(dialog).getByRole('button', { name: 'Send report' }))
    await waitFor(() => expect(screen.queryByRole('dialog')).toBeNull())
    expect(screen.getByRole('status')).toHaveTextContent('Report received')
    expect(fetcher).toHaveBeenLastCalledWith(`/api/v1/opportunities/${record.id}/reports`, expect.objectContaining({ method: 'POST', body: expect.stringContaining('Please check the year.') }))
  })
})
