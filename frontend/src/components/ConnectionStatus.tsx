import { useEffect, useState } from 'react'

import { ApiRequestError, getHealth } from '../api/client'
import type { HealthResponse } from '../types/api'

type ConnectionState =
  | { status: 'checking' }
  | { status: 'connected'; health: HealthResponse }
  | { status: 'unavailable'; message: string }

/**
 * Shows whether the API is reachable. Status is conveyed as text, not by colour
 * alone (CONTEXT section 6 accessibility).
 */
export function ConnectionStatus() {
  const [state, setState] = useState<ConnectionState>({ status: 'checking' })

  useEffect(() => {
    const controller = new AbortController()

    getHealth(controller.signal)
      .then((health) => {
        if (!controller.signal.aborted) {
          setState({ status: 'connected', health })
        }
      })
      .catch((error: unknown) => {
        if (controller.signal.aborted) {
          return
        }
        const message =
          error instanceof ApiRequestError
            ? error.message
            : 'The ScholarCheck service is not reachable right now.'
        setState({ status: 'unavailable', message })
      })

    return () => {
      controller.abort()
    }
  }, [])

  return (
    <section className="panel" aria-labelledby="connection-heading">
      <h2 id="connection-heading">Service status</h2>
      <div role="status" aria-live="polite">
        {state.status === 'checking' && <p>Checking the ScholarCheck service…</p>}
        {state.status === 'connected' && (
          <p>
            API connected. Environment: <strong>{state.health.environment}</strong>.
          </p>
        )}
        {state.status === 'unavailable' && (
          <p>
            API not reachable. {state.message} You can still read this page; data
            will load once the service is back.
          </p>
        )}
      </div>
    </section>
  )
}
