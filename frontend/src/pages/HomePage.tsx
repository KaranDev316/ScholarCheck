import { useState } from 'react'
import type { FormEvent } from 'react'

import { CoverageChip } from '../components/Chips'
import { ScholarshipCard } from '../components/ScholarshipCard'
import { availableCountries } from '../data/filters'
import { COVERAGE_KEYS, COVERAGE_LABELS, FUNDING_TYPES, STUDY_LEVELS } from '../data/types'
import type { Scholarship } from '../data/types'
import { exploreHref } from '../routing/routes'

interface HomePageProps {
  records: readonly Scholarship[]
  isDevelopment: boolean
}

export function HomePage({ records, isDevelopment }: HomePageProps) {
  const [query, setQuery] = useState('')
  const countries = availableCountries(records)
  const sample = records[0]

  function submitSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    window.location.hash = exploreHref({ q: query.trim() }).replace(/^#/, '')
  }

  return (
    <>
      <div className="herobg">
        <div className="wrap">
          <div className="hero">
            <div>
              <h1>Find funding. Check the evidence. Decide for yourself.</h1>
              <p className="lead">
                Find source-checked funding details, published deadlines and links to the official provider.
              </p>
              <form className="search" role="search" onSubmit={submitSearch}>
                <input
                  name="q"
                  aria-label="Search scholarships"
                  placeholder="Try “doctoral scholarships in Canada”"
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                />
                <button className="btn" type="submit">
                  Search
                </button>
              </form>
              <p className="small mute hero-note">
                No account needed to browse, filter or open official links.
              </p>
            </div>

            {sample ? (
              <div className="schcard" aria-label="Example record from the catalogue">
                {isDevelopment ? <div className="chip unspec">Development preview</div> : null}
                <div className="sm">
                  {sample.provider}, {sample.country}
                </div>
                <div className="st">{sample.title}</div>
                {sample.headline ? (
                  <div>
                    <div className="sa">{sample.headline.amount}</div>
                    <div className="sm">{sample.headline.basis}</div>
                  </div>
                ) : null}
                {sample.sourceCheck ? <p className="small">Source checked {new Date(sample.sourceCheck.checkedAt).toLocaleDateString('en-GB', { timeZone: 'UTC' })}</p> : null}
                <ul className="slist list-plain">
                  {COVERAGE_KEYS.map((key) => (
                    <li key={key}>
                      {COVERAGE_LABELS[key]}: <CoverageChip state={sample.coverage[key].state} />
                    </li>
                  ))}
                </ul>
              </div>
            ) : (
              <div className="schcard" aria-label="Catalogue status">
                <div className="st">No published scholarships yet</div>
                <div className="sm">
                  Records appear here once they pass the evidence checks and are published.
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      <section className="wrap starthere">
        <h2>Not sure where to start?</h2>
        <div className="startgrid">
          <div>
            <p className="small mute">Where do you want to study?</p>
            <div className="qrow">
              {countries.map((country) => (
                <a className="qchip" key={country} href={exploreHref({ country })}>
                  {country}
                </a>
              ))}
            </div>
          </div>
          <div>
            <p className="small mute">Which level?</p>
            <div className="qrow">
              {STUDY_LEVELS.map((level) => (
                <a className="qchip" key={level} href={exploreHref({ level })}>
                  {level}
                </a>
              ))}
            </div>
          </div>
          <div>
            <p className="small mute">What kind of funding?</p>
            <div className="qrow">
              {FUNDING_TYPES.map((funding) => (
                <a className="qchip" key={funding} href={exploreHref({ funding })}>
                  {funding}
                </a>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="wrap published">
        <div className="sectionhead">
          <h2>{isDevelopment ? 'Development preview scholarships' : 'Published scholarships'}</h2>
          <a href="#explore">Browse all {records.length}</a>
        </div>
        {records.length === 0 ? (
          <div className="state">
            <h3>No published scholarships yet</h3>
            <p className="mute">
              Only scholarships that passed our evidence checks are listed. Records appear here as
              they are published.
            </p>
          </div>
        ) : (
          <div className="grid2">
            {records.map((record) => (
              <ScholarshipCard key={record.id} record={record} isDevelopment={isDevelopment} />
            ))}
          </div>
        )}
      </section>
    </>
  )
}
