import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it } from 'vitest'

import App from '../src/App'

function goTo(hash: string) {
  window.history.replaceState(null, '', hash)
}

describe('App routing', () => {
  beforeEach(() => {
    goTo('#home')
  })

  afterEach(() => {
    goTo('#home')
  })

  it('renders the home view for the root hash', () => {
    render(<App />)

    expect(
      screen.getByRole('heading', {
        level: 1,
        name: /find funding. check the evidence. decide for yourself/i,
      }),
    ).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /skip to content/i })).toBeInTheDocument()
  })

  it('opens a record straight from its shareable link', () => {
    goTo('#cgsd-doctoral')
    render(<App />)

    expect(
      screen.getByRole('heading', {
        level: 1,
        name: /canada graduate research scholarship/i,
      }),
    ).toBeInTheDocument()
    expect(screen.getAllByText(/development preview/i).length).toBeGreaterThan(0)
  })

  it('says plainly when a record id is unknown, without inventing a record', () => {
    goTo('#withdrawn-award')
    render(<App />)

    expect(
      screen.getByRole('heading', { level: 1, name: /this scholarship isn’t available/i }),
    ).toBeInTheDocument()
    expect(screen.getByText(/no published record matches “withdrawn-award”/i)).toBeInTheDocument()
  })

  it('opens the explore view with the filters carried in the hash', () => {
    goTo('#explore?c=Canada')
    render(<App />)

    expect(screen.getByRole('heading', { level: 1, name: /find scholarships/i })).toBeInTheDocument()
    expect(screen.getByLabelText('Destination country')).toHaveValue('Canada')
  })

  it('follows a hash link without a full page reload', async () => {
    const user = userEvent.setup()
    render(<App />)

    await user.click(screen.getByRole('link', { name: 'Canada' }))

    await waitFor(() => {
      expect(screen.getByRole('heading', { level: 1, name: /find scholarships/i })).toBeInTheDocument()
    })
    expect(screen.getByLabelText('Destination country')).toHaveValue('Canada')
    expect(window.location.hash).toBe('#explore?c=Canada')
  })
})
