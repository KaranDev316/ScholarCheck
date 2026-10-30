import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

// jsdom has no layout, and its window.scrollTo only logs "not implemented".
// Route changes call it, so replace it with a no-op rather than noise.
window.scrollTo = () => {}

// Without `test.globals`, Testing Library cannot register its own cleanup.
afterEach(() => {
  cleanup()
})
