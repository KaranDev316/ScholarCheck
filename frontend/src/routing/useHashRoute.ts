import { useEffect, useState } from 'react'

import { parseHash, type Route } from './routes'

/**
 * Follows the URL hash. The browser fires `hashchange` on in-page link clicks,
 * so navigation works with plain anchors and links stay copyable.
 */
export function useHashRoute(): Route {
  const [route, setRoute] = useState<Route>(() => parseHash(window.location.hash))

  useEffect(() => {
    function handleHashChange() {
      setRoute(parseHash(window.location.hash))
      window.scrollTo(0, 0)
    }

    window.addEventListener('hashchange', handleHashChange)
    return () => window.removeEventListener('hashchange', handleHashChange)
  }, [])

  return route
}
