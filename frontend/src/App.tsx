import { useEffect, useRef, useState } from 'react'

import { SiteFooter } from './components/SiteFooter'
import { SiteHeader } from './components/SiteHeader'
import { findScholarship, getCatalogue, loadCatalogue } from './data/catalogue'
import { ExplorePage } from './pages/ExplorePage'
import { HomePage } from './pages/HomePage'
import { NotFoundPage } from './pages/NotFoundPage'
import { ScholarshipPage } from './pages/ScholarshipPage'
import { exploreHref, routeKey } from './routing/routes'
import { useHashRoute } from './routing/useHashRoute'

const preview = getCatalogue()

function App() {
  const route = useHashRoute()
  const [catalogue, setCatalogue] = useState(preview)
  const [loading, setLoading] = useState(!preview.isDevelopment)
  const [error, setError] = useState('')
  const [attempt, setAttempt] = useState(0)
  useEffect(() => {
    if (preview.isDevelopment) return
    const controller = new AbortController()
    loadCatalogue(controller.signal).then(setCatalogue).catch((err: unknown) => {
      if (!controller.signal.aborted) setError(err instanceof Error ? err.message : 'Could not load scholarships.')
    }).finally(() => { if (!controller.signal.aborted) setLoading(false) })
    return () => controller.abort()
  }, [attempt])
  const mainRef = useRef<HTMLElement>(null)
  const firstRender = useRef(true)
  const current = routeKey(route)

  // Moving focus to the new view lets screen readers announce the change.
  useEffect(() => {
    if (firstRender.current) {
      firstRender.current = false
      return
    }
    mainRef.current?.focus()
  }, [current])

  let view
  let section: 'home' | 'explore' = 'explore'

  switch (route.name) {
    case 'home':
      section = 'home'
      view = <HomePage records={catalogue.records} isDevelopment={catalogue.isDevelopment} />
      break
    case 'explore':
      view = (
        <ExplorePage
          key={route.filters.q}
          records={catalogue.records}
          isDevelopment={catalogue.isDevelopment}
          filters={route.filters}
          onFiltersChange={(filters) => {
            window.location.hash = exploreHref(filters).replace(/^#/, '')
          }}
        />
      )
      break
    case 'scholarship': {
      const record = findScholarship(catalogue.records, route.id)
      view = record ? (
        <ScholarshipPage record={record} isDevelopment={catalogue.isDevelopment} />
      ) : (
        <NotFoundPage id={route.id} />
      )
      break
    }
  }

  return (
    <>
      <button className="skip" type="button" onClick={() => mainRef.current?.focus()}>
        Skip to content
      </button>
      <SiteHeader current={section} />
      <main id="main" ref={mainRef} tabIndex={-1}>
        {loading ? <div className="wrap" role="status">Loading scholarships…</div> : error ? (
          <div className="wrap" role="alert"><p>{error}</p><button className="btn" onClick={() => { setLoading(true); setError(''); setAttempt(attempt + 1) }}>Try again</button></div>
        ) : view}
      </main>
      <SiteFooter />
    </>
  )
}

export default App
