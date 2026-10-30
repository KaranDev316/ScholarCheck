import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { HomePage } from '../src/pages/HomePage'

describe('HomePage', () => {
  it('states the ScholarCheck promise and the current publication status', () => {
    render(<HomePage records={[]} isDevelopment={false} />)

    expect(
      screen.getByRole('heading', {
        level: 1,
        name: /find funding. check the evidence. decide for yourself/i,
      }),
    ).toBeInTheDocument()
    expect(screen.getAllByText(/no published scholarships yet/i)).not.toHaveLength(0)
    expect(screen.queryByText(/api connected|environment/i)).not.toBeInTheDocument()
  })
})
