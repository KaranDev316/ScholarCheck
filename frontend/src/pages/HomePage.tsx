import { useState } from 'react'
import type { FormEvent } from 'react'

import { Card } from '../components/Card'
import { CoverageChecklist } from '../components/CoverageChecklist'
import { UnknownBadge } from '../components/UnknownBadge'
import { availableCountries } from '../data/filters'
import { formatAward, formatComponentLabel, formatDate } from '../data/format'
import { FUNDING_TYPES, type Scholarship, type StudyLevel } from '../data/types'
import { exploreHref, scholarshipHref } from '../routing/routes'

interface HomePageProps {
  records: readonly Scholarship[]
  isDevelopment: boolean
}

const PRIMARY_LEVELS: readonly StudyLevel[] = ["Bachelor's", "Master's", 'PhD']

export function HomePage({ records, isDevelopment }: HomePageProps) {
  const [query, setQuery] = useState('')
  const countries = availableCountries(records)
  const hasResearchFallback = records.some((record) => record.levels.includes('Research degree'))
  const levels: readonly StudyLevel[] = hasResearchFallback
    ? [...PRIMARY_LEVELS, 'Research degree']
    : PRIMARY_LEVELS

  const sample = records[0]
  const sampleAward = sample?.headline
    ? formatAward(
        sample.headline.amount,
        sample.headline.currency !== undefined ? sample.headline.currency : sample.currency,
        sample.headline.basis,
      )
    : null
  const sampleComponentLabel = sample?.headline
    ? formatComponentLabel(sample.headline.component, sample.headline.basis)
    : null

  function submitSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    window.location.hash = exploreHref({ q: query.trim() }).replace(/^#/, '')
  }

  const gridClass =
    records.length === 2 ? 'card-grid card-grid--two' : 'card-grid'

  return (
    <>
      <div className="herobg band">
        <div className="container wrap">
          <div className="hero">
            <div>
              <h1>
                <span className="line">Find funding.</span>{' '}
                <span className="line">Check the evidence.</span>{' '}
                <span className="line">Decide for yourself.</span>
              </h1>
              <p className="lead">
                Every scholarship shows exact official wording, source-checked funding details and
                visible unknowns.
              </p>
              <form className="search" role="search" onSubmit={submitSearch}>
                <input
                  name="q"
                  aria-label="Search scholarships"
                  placeholder="Try 'doctoral scholarships in Canada'"
                  value={query}
                  onChange={(event) => setQuery(event.target.value)}
                />
                <button className="btn btn-primary" type="submit">
                  Search
                </button>
              </form>
              <p className="small muted hero-note">No account needed.</p>
            </div>

            {sample ? (
              <div className="schcard card" aria-label="Example record from the catalogue">
                {isDevelopment ? (
                  <div>
                    <UnknownBadge label="Development preview" />
                  </div>
                ) : null}
                <div className="sm">
                  {sample.provider}, {sample.country}
                </div>
                <div className="st">{sample.title}</div>
                {sampleAward ? (
                  <div>
                    {sampleComponentLabel ? (
                      <div className="amount-label sm">{sampleComponentLabel}</div>
                    ) : null}
                    <div
                      className={`sa amount-value${sampleAward.currencyNote ? ' amount-value-unconfirmed' : ''}`}
                    >
                      {sampleAward.amountText}
                    </div>
                    {sampleAward.qualifierText ? (
                      <div className="sm amount-basis">{sampleAward.qualifierText}</div>
                    ) : null}
                    {sampleAward.currencyNote ? (
                      <div className="sm award-note">{sampleAward.currencyNote}</div>
                    ) : null}
                  </div>
                ) : null}
                {sample.sourceCheck ? (
                  <p className="small sm">
                    Source checked {formatDate(sample.sourceCheck.checkedAt)}
                  </p>
                ) : null}
                <CoverageChecklist coverage={sample.coverage} compact />
              </div>
            ) : (
              <div className="schcard card" aria-label="Catalogue status">
                <div className="st">No published scholarships yet</div>
                <div className="sm">
                  Records appear here once they pass the evidence checks and are published.
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      <section className="container wrap starthere" aria-label="Quick filters">
        <h2>Quick filters</h2>
        <div className="startgrid">
          {countries.length > 0 ? (
            <div className="startgroup">
              <p className="small muted startlabel">Country</p>
              <div className="qrow">
                {countries.map((country) => (
                  <a className="chip qchip" key={country} href={exploreHref({ country })}>
                    {country}
                  </a>
                ))}
              </div>
            </div>
          ) : null}
          <div className="startgroup">
            <p className="small muted startlabel">Level</p>
            <div className="qrow">
              {levels.map((level) => (
                <a className="chip qchip" key={level} href={exploreHref({ level })}>
                  {level}
                </a>
              ))}
            </div>
          </div>
          <div className="startgroup">
            <p className="small muted startlabel">Funding type</p>
            <div className="qrow">
              {FUNDING_TYPES.map((funding) => (
                <a className="chip qchip" key={funding} href={exploreHref({ funding })}>
                  {funding}
                </a>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="container wrap published">
        <div className="sectionhead">
          <h2>{isDevelopment ? 'Development preview scholarships' : 'Published scholarships'}</h2>
        </div>
        {records.length === 0 ? (
          <div className="state state-empty">
            <h3>No published scholarships yet</h3>
            <p className="muted">
              Only scholarships that passed our evidence checks are listed. Records appear here as
              they are published.
            </p>
          </div>
        ) : records.length === 1 && sample ? (
          <div className="published-compact-row card">
            <div className="compact-row-main">
              <h3>
                <a href={scholarshipHref(sample.id)}>{sample.title}</a>
              </h3>
              {isDevelopment ? <UnknownBadge label="Development preview" /> : null}
            </div>
            {sampleAward ? (
              <div className="compact-row-amount">
                <span className="amount-value">{sampleAward.inlineText}</span>
                {sampleAward.currencyNote ? (
                  <span className="small muted award-note">{sampleAward.currencyNote}</span>
                ) : null}
              </div>
            ) : null}
            <a className="btn btn-primary" href={scholarshipHref(sample.id)}>
              See details
            </a>
          </div>
        ) : (
          <div className={gridClass}>
            {records.map((record) => (
              <Card key={record.id} record={record} isDevelopment={isDevelopment} />
            ))}
          </div>
        )}
      </section>
    </>
  )
}
