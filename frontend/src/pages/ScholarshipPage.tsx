import { useState } from 'react'

import { CoverageChip, FactChip, TagChip } from '../components/Chips'
import { ReportDialog } from '../components/ReportDialog'
import { formatDate, formatDateTime, displayUrl } from '../data/format'
import { fundingTypeFor, passedRoundDates } from '../data/funding'
import { COVERAGE_KEYS, COVERAGE_LABELS } from '../data/types'
import type { Scholarship } from '../data/types'

interface ScholarshipPageProps {
  record: Scholarship
  isDevelopment: boolean
}

export function ScholarshipPage({ record, isDevelopment }: ScholarshipPageProps) {
  const [reportOpen, setReportOpen] = useState(false)
  const [toast, setToast] = useState('')

  const fundingType = fundingTypeFor(record.coverage)
  const passed = passedRoundDates(record)
  const canApply = record.application.kind === 'provider'
  const datesPassed = passed.length > 0

  const dateNote = datesPassed
    ? `The published dates (${passed.join('; ')}) have passed, and the next round isn’t published yet.`
    : record.application.note

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

  function showEvidence(number: number | undefined) {
    if (!number) return
    const target = document.getElementById(`${record.id}-ev${number}`)
    if (typeof target?.scrollIntoView === 'function') target.scrollIntoView({ block: 'center' })
  }

  function sendReport() {
    setReportOpen(false)
    announce('Reports are not being collected yet, so nothing was sent.')
  }

  return (
    <>
      <div className="crumbs wrap">
        <a href="#explore">All scholarships</a> / <span>{record.title}</span>
      </div>
      <div className="detail wrap">
        <div>
          <div className="titlerow">
            <h1>{record.title}</h1>
            <div className="share">
              <button className="sharebtn" type="button" onClick={copyLink}>
                Copy link
              </button>
              <button className="sharebtn" type="button" onClick={share}>
                Share
              </button>
            </div>
          </div>

          <p className="mute providerline">
            {record.provider}, {record.country}
          </p>

          <div className="tags">
            {record.levels.map((level) => (
              <TagChip key={level}>{level}</TagChip>
            ))}
            <TagChip>{fundingType ?? 'Funding type not established'}</TagChip>
            <TagChip>{record.country}</TagChip>
            {record.tags.map((tag) => (
              <TagChip key={tag}>{tag}</TagChip>
            ))}
            {isDevelopment ? <span className="chip unspec">Development preview</span> : null}
          </div>

          <div className="strip">
            <div>
              <span className="sl2">{record.headline?.component ?? 'Amount'}</span>
              {record.headline ? (
                <>
                  <strong className="amt">{record.headline.amount}</strong>
                  <span className="small mute">{record.headline.basis}</span>
                </>
              ) : (
                <span className="ph">Not stated in the source</span>
              )}
            </div>
            <div>
              <span className="sl2">Study level</span>
              <strong>{record.levels.join(', ')}</strong>
            </div>
            <div>
              <span className="sl2">Application round</span>
              <strong>{record.rounds[0]?.status ?? 'Not published'}</strong>
            </div>
          </div>

          <div className="actions">
            {isDevelopment ? (
              <p className="small note warn">
                Development preview. This record is not published and has not passed the automated
                source check.
              </p>
            ) : null}
            {dateNote ? <p className="small note warn">{dateNote}</p> : null}

            <div className="actionpair">
              <div className="act">
                <a
                  className={canApply && !datesPassed ? 'btn alt' : 'btn'}
                  href={record.links.requirements}
                  target="_blank"
                  rel="noreferrer"
                >
                  Read the requirements
                </a>
                <p className="small mute">
                  What the official page says about eligibility and funding.
                </p>
              </div>
              {canApply ? (
                <div className="act">
                  <a
                    className={datesPassed ? 'btn alt' : 'btn'}
                    href={record.links.portal}
                    target="_blank"
                    rel="noreferrer"
                  >
                    Apply on the provider’s site
                  </a>
                  <p className="small mute">Opens the provider’s own application page.</p>
                </div>
              ) : null}
            </div>
          </div>


          <div className="dsec">
            <h2>Funding components</h2>
            <p className="mute small">
              Each component is listed on its own. We never add them together or call one a total.
            </p>

            <div className="rule">
              <strong>
                {fundingType === 'Fully funded' ? (
                  <>
                    <span className="chip ff">Fully funded</span>{' '}
                  </>
                ) : null}
                What the official page says it covers
              </strong>
              <div className="small mute">
                “Fully funded” is shown only when tuition, living costs and flights are all stated
                as covered.
              </div>
              {COVERAGE_KEYS.map((key) => (
                <div className="covrow" key={key}>
                  <span>
                    {COVERAGE_LABELS[key]}
                    {record.coverage[key].detail ? (
                      <span className="small mute covdetail"> — {record.coverage[key].detail}</span>
                    ) : null}
                  </span>
                  <CoverageChip state={record.coverage[key].state} />
                </div>
              ))}
            </div>

            {record.components.map((component) => (
              <div className="rule" key={component.id}>
                <div className="comphead">
                  <strong>{component.label}</strong>
                  <FactChip state={component.state} />
                </div>
                {component.state === 'stated' ? (
                  <>
                    {component.amount ? (
                      <div className="amt compamount">{component.amount}</div>
                    ) : null}
                    <div className="small mute">
                      {component.basis ?? 'Covered, amount not stated'}
                    </div>
                    {component.note ? <p className="small mute">{component.note}</p> : null}
                  </>
                ) : (
                  <>
                    <div className="ph">{component.note ?? 'Not specified in the source'}</div>
                    {component.basis ? <div className="small mute">{component.basis}</div> : null}
                  </>
                )}
                {component.conditions?.length ? (
                  <ul className="small mute conditions">
                    {component.conditions.map((condition) => (
                      <li key={condition}>{condition}</li>
                    ))}
                  </ul>
                ) : null}
                {component.evidenceNumber ? (
                  <button
                    className="refbtn"
                    type="button"
                    onClick={() => showEvidence(component.evidenceNumber)}
                  >
                    Evidence {component.evidenceNumber}
                  </button>
                ) : null}
              </div>
            ))}
          </div>


          <div className="dsec">
            <h2>Stated eligibility</h2>
            <p className="mute small">
              What the official source says. This isn’t a decision about you or a chance of award.
            </p>
            {record.eligibility.map((item) => (
              <div className="rule" key={item.id}>
                <div className="comphead">
                  <span>{item.statement}</span>
                  <FactChip state={item.state} />
                </div>
                {item.evidenceNumber ? (
                  <button
                    className="refbtn"
                    type="button"
                    onClick={() => showEvidence(item.evidenceNumber)}
                  >
                    Evidence {item.evidenceNumber}
                  </button>
                ) : null}
              </div>
            ))}
          </div>

          <div className="dsec">
            <h2>Rounds and deadlines</h2>
            <div className="tblwrap">
              <table className="tbl">
                <thead>
                  <tr>
                    <th scope="col">Round</th>
                    <th scope="col">Date as published</th>
                    <th scope="col">Status</th>
                    <th scope="col">Note</th>
                  </tr>
                </thead>
                <tbody>
                  {record.rounds.map((round) => (
                    <tr key={round.id}>
                      <td>{round.round}</td>
                      <td>{round.dateAsPublished}</td>
                      <td>
                        <span className="chip neutral">{round.status}</span>
                      </td>
                      <td className="mute small">{round.note}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="small mute">
              A passed date marks that round only. Other rounds stay as they are until a source says
              otherwise.
            </p>
          </div>


          <div className="dsec">
            <h2>Evidence</h2>
            <p className="mute small">
              Each claim above links to the wording it rests on, kept from the official page.
            </p>
            {record.evidence.map((entry) => (
              <div className="ev" id={`${record.id}-ev${entry.number}`} key={entry.number}>
                <strong>
                  {entry.number}. {entry.claim}
                </strong>
                <p className="excerpt">“{entry.passage}”</p>
                <div className="small mute">
                  Source: {displayUrl(entry.url)} · Saved: {formatDateTime(entry.savedAt)}
                </div>
                <a className="btn alt sm" href={entry.url} target="_blank" rel="noreferrer">
                  Open the official page
                </a>
              </div>
            ))}
          </div>

          <div className="dsec">
            <h2>Was this record wrong?</h2>
            <p className="mute small">
              Feedback is not collected yet. Until it is, read the official pages linked above and
              treat them as the authority.
            </p>
            <button className="btn alt sm" type="button" onClick={() => setReportOpen(true)}>
              Report a problem
            </button>
          </div>
        </div>

        <aside className="side" aria-label="Assurance">
          <div className="panel">
            <h3>Checked against the official page</h3>
            {record.sourceCheck ? (
              <dl>
                <div>
                  <dt>Last checked</dt>
                  <dd>{formatDate(record.sourceCheck.checkedAt)}</dd>
                </div>
                <div>
                  <dt>Result</dt>
                  <dd>
                    <span className="chip stated">Matches the official page</span>
                  </dd>
                </div>
              </dl>
            ) : (
              <p className="small mute">
                <span className="chip unspec">Not source checked yet</span>
                <br />
                The record appears here as a development preview. A record is published only once an
                automated check confirms it matches the official page.
              </p>
            )}
            <p className="small mute">
              Details can change. Confirm with the provider before you apply.
            </p>
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
                <dd>{fundingType ?? 'Not established'}</dd>
              </div>
            </dl>
          </div>

          <div className="panel">
            <h3>See something wrong?</h3>
            <p className="small mute">Feedback is not collected yet.</p>
            <button className="btn alt sm" type="button" onClick={() => setReportOpen(true)}>
              Report a problem
            </button>
          </div>
        </aside>

        <div className="pinbar">
          {canApply && !datesPassed ? (
            <a className="btn" href={record.links.portal} target="_blank" rel="noreferrer">
              Apply on the provider’s site
            </a>
          ) : (
            <a className="btn" href={record.links.requirements} target="_blank" rel="noreferrer">
              Read the requirements
            </a>
          )}
        </div>
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

