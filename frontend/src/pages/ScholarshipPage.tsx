import { useState } from 'react'

import { FactChip, TagChip } from '../components/Chips'
import { CoverageChecklist } from '../components/CoverageChecklist'
import { DateRoundTable } from '../components/DateRoundTable'
import { EvidenceBlock } from '../components/EvidenceBlock'
import { ReportDialog } from '../components/ReportDialog'
import { UnknownBadge } from '../components/UnknownBadge'
import {
  formatAward,
  formatComponentLabel,
  formatDate,
  formatScholarshipSummary,
} from '../data/format'
import { fundingTypeFor, isOpenRound } from '../data/funding'
import type { Scholarship } from '../data/types'

interface ScholarshipPageProps {
  record: Scholarship
  isDevelopment: boolean
}

export function ScholarshipPage({ record, isDevelopment }: ScholarshipPageProps) {
  const [reportOpen, setReportOpen] = useState(false)
  const [toast, setToast] = useState('')

  const fundingType = fundingTypeFor(record.coverage)
  const upcomingRound = record.rounds.find((round) => isOpenRound(round))
  const headlineAward = record.headline
    ? formatAward(
        record.headline.amount,
        record.headline.currency !== undefined ? record.headline.currency : record.currency,
        record.headline.basis,
      )
    : null

  function announce(message: string) {
    setToast(message)
    window.setTimeout(() => setToast(''), 3200)
  }

  async function copyLink() {
    try {
      await navigator.clipboard.writeText(window.location.href)
      announce('Link copied')
    } catch {
      announce('Could not copy the link. Copy it from the address bar instead.')
    }
  }

  async function share() {
    if (typeof navigator.share === 'function') {
      try {
        await navigator.share({ title: record.title, url: window.location.href })
      } catch {
        return
      }
      return
    }

    await copyLink()
  }

  async function sendReport(reason: string, details: string) {
    if (isDevelopment) throw new Error('Development previews cannot receive reports.')
    const response = await fetch(`/api/v1/opportunities/${encodeURIComponent(record.id)}/reports`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reason, details }),
    })
    if (!response.ok) {
      throw new Error(
        response.status === 429
          ? 'Too many reports. Please try again later.'
          : 'Could not send your report. Please try again.',
      )
    }
    setReportOpen(false)
    announce('Report received. Thank you.')
  }

  return (
    <>
      <nav className="crumbs container wrap" aria-label="Breadcrumb">
        <a href="#explore">Find scholarships</a> <span aria-hidden="true">›</span>{' '}
        <span>{record.title}</span>
      </nav>

      <div className="detail container wrap">
        <div>
          <div className="titlerow">
            <h1>{record.title}</h1>
            <div className="share">
              <button className="btn btn-secondary sharebtn" type="button" onClick={copyLink}>
                Copy link
              </button>
              <button className="btn btn-secondary sharebtn" type="button" onClick={share}>
                Share
              </button>
            </div>
          </div>

          <p className="muted providerline">
            {record.provider}, {record.country}
          </p>

          {record.summary ? (
            <p className="muted reading summary-lead">{formatScholarshipSummary(record)}</p>
          ) : null}

          <div className="tags">
            {record.levels.map((level) => (
              <TagChip key={level}>{level}</TagChip>
            ))}
            {fundingType === 'Fully funded' ? (
              <span className="tag tag-fully-funded">Fully funded</span>
            ) : fundingType ? (
              <TagChip>{fundingType}</TagChip>
            ) : null}
            {record.tags.map((tag) => (
              <TagChip key={tag}>{tag}</TagChip>
            ))}
            {isDevelopment ? <UnknownBadge label="Development preview" /> : null}
          </div>

          <div className="strip">
            <div>
              <span className="sl2 amount-label">
                {record.headline
                  ? formatComponentLabel(record.headline.component, record.headline.basis)
                  : 'Amount'}
              </span>
              {headlineAward ? (
                <>
                  <strong
                    className={`amt amount-value${headlineAward.currencyNote ? ' amount-value-unconfirmed' : ''}`}
                  >
                    {headlineAward.amountText}
                  </strong>
                  {headlineAward.qualifierText ? (
                    <span className="small muted amount-basis">{headlineAward.qualifierText}</span>
                  ) : null}
                  {headlineAward.currencyNote ? (
                    <span className="small muted award-note">{headlineAward.currencyNote}</span>
                  ) : null}
                </>
              ) : (
                <UnknownBadge label="Not specified" />
              )}
            </div>
            <div>
              <span className="sl2">Source check</span>
              <strong>
                {record.sourceCheck
                  ? `Source checked ${formatDate(record.sourceCheck.checkedAt)}`
                  : 'Not source checked yet'}
              </strong>
              <span className="small muted">{record.levels.join(', ')}</span>
            </div>
            <div>
              <span className="sl2">Funding & round</span>
              <div>
                {fundingType === 'Fully funded' ? (
                  <span className="tag tag-fully-funded">Fully funded</span>
                ) : fundingType ? (
                  <TagChip>{fundingType}</TagChip>
                ) : (
                  <UnknownBadge label="Not specified" />
                )}
              </div>
              <span className="small muted">
                {upcomingRound?.status ?? record.rounds[0]?.status ?? 'Not published'}
              </span>
            </div>
          </div>

          <div className="dsec">
            <h2>Funding components</h2>
            <p className="muted small">
              Each component is listed on its own. We never add them together or call one a total.
            </p>

            <CoverageChecklist coverage={record.coverage} />

            {record.components.map((component) => {
              const componentAward = component.amount
                ? formatAward(
                    component.amount,
                    component.currency !== undefined ? component.currency : record.currency,
                    component.basis,
                  )
                : null
              return (
                <div className="rule" key={component.id}>
                  <div className="comphead">
                    <strong>{formatComponentLabel(component.label, component.basis)}</strong>
                    <FactChip state={component.state} />
                  </div>
                  {component.state === 'stated' ? (
                    <>
                      {componentAward ? (
                        <div
                          className={`amt compamount amount-value${componentAward.currencyNote ? ' amount-value-unconfirmed' : ''}`}
                        >
                          {componentAward.amountText}
                        </div>
                      ) : null}
                      <div className="small muted amount-basis">
                        {componentAward?.qualifierText ??
                          component.basis ??
                          'Covered, amount not stated'}
                      </div>
                      {componentAward?.currencyNote ? (
                        <div className="small muted award-note">{componentAward.currencyNote}</div>
                      ) : null}
                      {component.note ? <p className="small muted">{component.note}</p> : null}
                    </>
                  ) : (
                    <>
                      <div className="ph">{component.note ?? 'Not specified in the source'}</div>
                      {component.basis ? <div className="small muted">{component.basis}</div> : null}
                    </>
                  )}
                  {component.conditions?.length ? (
                    <ul className="small muted conditions">
                      {component.conditions.map((condition) => (
                        <li key={condition}>{condition}</li>
                      ))}
                    </ul>
                  ) : null}
                </div>
              )
            })}
          </div>

          <div className="dsec">
            <h2>Eligibility</h2>
            <p className="muted small">
              These are the provider’s stated requirements, not a decision about you.
            </p>
            <ol className="elig">
              {record.eligibility.map((item) => (
                <li key={item.id}>
                  {item.statement}
                  {item.state === 'stated' ? null : (
                    <>
                      {' '}
                      <UnknownBadge label="Not specified" />
                    </>
                  )}
                </li>
              ))}
            </ol>
          </div>

          <div className="dsec">
            <h2>Rounds and deadlines</h2>
            <DateRoundTable rounds={record.rounds} />
          </div>

          <div className="dsec">
            <h2>Official evidence</h2>
            <p className="muted small">
              Exact wording retained from the official provider page.
            </p>
            <EvidenceBlock
              recordId={record.id}
              evidence={record.evidence}
              sourceCheck={record.sourceCheck}
              fallbackUrl={record.links.requirements}
            />
          </div>
        </div>

        <aside className="side" aria-label="Scholarship details">
          <div className="panel band source-check-panel">
            <h3>Source check</h3>
            <dl>
              <div>
                <dt>Official source</dt>
                <dd>
                  <a
                    className="btn btn-secondary sm"
                    href={record.links.summary}
                    target="_blank"
                    rel="noreferrer"
                  >
                    View official source
                  </a>
                </dd>
              </div>
              <div>
                <dt>Checked date</dt>
                <dd>
                  {record.sourceCheck
                    ? formatDate(record.sourceCheck.checkedAt)
                    : 'Not source checked yet'}
                </dd>
              </div>
              <div>
                <dt>Result</dt>
                <dd>
                  {record.sourceCheck ? (
                    'Matches the official page'
                  ) : (
                    <UnknownBadge label="Development preview" />
                  )}
                </dd>
              </div>
            </dl>
          </div>

          <div className="panel">
            <h3>At a glance</h3>
            <dl>
              <div>
                <dt>Provider</dt>
                <dd>{record.provider}</dd>
              </div>
              <div>
                <dt>Country</dt>
                <dd>{record.country}</dd>
              </div>
              <div>
                <dt>Study level</dt>
                <dd>{record.levels.join(', ')}</dd>
              </div>
              <div>
                <dt>Funding type</dt>
                <dd>{fundingType ?? <UnknownBadge label="Not specified" />}</dd>
              </div>
            </dl>
          </div>

          <div className="panel">
            <h3>See something wrong?</h3>
            <p className="small muted">
              Tell us about an incorrect amount, deadline, requirement or link.
            </p>
            <button
              className="btn btn-secondary sm"
              type="button"
              onClick={() => setReportOpen(true)}
            >
              Report a problem
            </button>
          </div>
        </aside>
      </div>

      <ReportDialog
        scholarshipTitle={record.title}
        open={reportOpen}
        onClose={() => setReportOpen(false)}
        onSend={sendReport}
      />

      <div className={toast ? 'toast on' : 'toast'} role="status">
        {toast}
      </div>
    </>
  )
}
