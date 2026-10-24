import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { HomePage } from '../src/pages/HomePage'

describe('HomePage', () => {
  it('states the ScholarCheck promise and the current publication status', () => {
    render(<HomePage />)

    expect(
      screen.getByRole('heading', {
        level: 1,
        name: /find funding. check the evidence. decide for yourself/i,
      }),
    ).toBeInTheDocument()
    expect(screen.getByText(/no scholarships are published yet/i)).toBeInTheDocument()
    expect(screen.queryByText(/api connected|environment/i)).not.toBeInTheDocument()
  })
})
