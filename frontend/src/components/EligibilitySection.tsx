import { useId, useState } from 'react'
import type { ReactNode } from 'react'

import { formatDate } from '../data/format'
import type { EligibilityStatement, SourceCheck } from '../data/types'
import { UnknownBadge } from './UnknownBadge'

interface EligibilitySectionProps {
  eligibility: readonly EligibilityStatement[]
  sourceCheck: SourceCheck | null
}

type CategoryId =
  | 'application-route'
  | 'citizenship'
  | 'admission-enrolment'
  | 'study-stage'
  | 'academic-merit'
  | 'language-tests'
  | 'age-limit'
  | 'non-duplication'

interface CategorySpec {
  id: CategoryId
  title: string
  subtitle: string
  pattern: RegExp
  idPattern: RegExp
  highlightWhenStated?: boolean
  icon: ReactNode
}

const WORD_NUMBERS: Record<string, string> = {
  one: '1',
  two: '2',
  three: '3',
  four: '4',
  five: '5',
}

function extractSummaryPill(categoryId: CategoryId, items: readonly EligibilityStatement[]): string | null {
  const combined = items.map((item) => item.statement).join(' ')
  if (categoryId === 'study-stage') {
    const months = combined.match(/(?:no more than|at most|up to)\s+(\d+)\s+months/i)
    if (months) return `≤ ${months[1]} months`
  }
  if (categoryId === 'non-duplication') {
    const cap = combined.match(/at most\s+(one|two|three|four|five|\d+)\s+(?:[\w-]+\s+){0,3}applications?/i)
    if (cap) {
      const num = WORD_NUMBERS[cap[1].toLowerCase()] ?? cap[1]
      return `Max ${num} ${num === '1' ? 'application' : 'applications'}`
    }
  }
  return null
}

function SvgIcon({ children }: { children: ReactNode }) {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {children}
    </svg>
  )
}

const CATEGORIES: readonly CategorySpec[] = [
  {
    id: 'application-route',
    title: 'Application route',
    subtitle: 'Which channel to apply through.',
    pattern: /\b(channel|route|quota|apply through|scholarship application form|separate scholarship application|supervisor)\b/i,
    idPattern: /(route|form|supervisor)/i,
    highlightWhenStated: true,
    icon: (
      <SvgIcon>
        <circle cx="6" cy="19" r="2.5" />
        <circle cx="18" cy="5" r="2.5" />
        <path d="M8.5 19H14a3 3 0 0 0 0-6h-4a3 3 0 0 1 0-6h5.5" />
      </SvgIcon>
    ),
  },
  {
    id: 'citizenship',
    title: 'Citizenship & residency',
    subtitle: 'Who can apply.',
    pattern: /\b(citizens?|citizenship|permanent residents?|protected persons?|international students?|international applicants?|domestic|nationality|francophone|residency|residents?)\b/i,
    idPattern: /(citizen|international|residen)/i,
    icon: (
      <SvgIcon>
        <circle cx="12" cy="12" r="9" />
        <path d="M3.6 9h16.8M3.6 15h16.8M12 3a14 14 0 0 0 0 18M12 3a14 14 0 0 1 0 18" />
      </SvgIcon>
    ),
  },
  {
    id: 'admission-enrolment',
    title: 'Admission & enrolment',
    subtitle: 'Registration and programme.',
    pattern: /\b(registered|enrol|enrolled|enrolment|admission|offer of admission|doctoral programme|doctoral program|higher degree|full-time|study permit|caq|eligible.*institution)\b/i,
    idPattern: /(enrol|admission|permit)/i,
    icon: (
      <SvgIcon>
        <path d="M7 3h7l5 5v13H7z" />
        <path d="M14 3v5h5M10 13h6M10 17h4" />
      </SvgIcon>
    ),
  },
  {
    id: 'study-stage',
    title: 'Study stage & time limit',
    subtitle: 'How far into the degree you can be.',
    pattern: /\b(\d+\s*months|full-time equivalent|study.*completed|prior.*doctorate|already hold a research doctorate|commencing|time limit|year of study)\b/i,
    idPattern: /(months|stage|doctorate)/i,
    icon: (
      <SvgIcon>
        <circle cx="12" cy="12" r="9" />
        <path d="M12 7v5l3 2" />
      </SvgIcon>
    ),
  },
  {
    id: 'academic-merit',
    title: 'Academic merit',
    subtitle: 'Grades, on the provider’s own scale.',
    pattern: /\b(grade|gpa|distinction|academic achievement|academic record|academic priority|80%|honours|first[- ]class|merit)\b/i,
    idPattern: /(academic|grade|merit)/i,
    icon: (
      <SvgIcon>
        <path d="M6 19v-6M12 19V5M18 19v-9" />
      </SvgIcon>
    ),
  },
  {
    id: 'language-tests',
    title: 'Language & tests',
    subtitle: 'English, host-country language, GRE/GMAT.',
    pattern: /\b(english|ielts|toefl|language|gre|gmat|french|german|test score)\b/i,
    idPattern: /(english|language)/i,
    icon: (
      <SvgIcon>
        <path d="M4 5h7M7.5 3v2M5 12c2.5-1.5 4.5-4 5.5-7M5.5 7c1 2.2 2.7 4 4.5 5M13 19l4-9 4 9M14.3 16h5.4" />
      </SvgIcon>
    ),
  },
  {
    id: 'age-limit',
    title: 'Age limit',
    subtitle: 'Maximum age.',
    pattern: /\b(maximum age|age limit|years old|under \d+\s*years|born after)\b/i,
    idPattern: /\bage\b/i,
    icon: (
      <SvgIcon>
        <circle cx="9" cy="8" r="3" />
        <path d="M3.5 19a5.5 5.5 0 0 1 11 0" />
        <circle cx="17" cy="9" r="2.5" />
        <path d="M16 14.5a4.5 4.5 0 0 1 4.5 4.5" />
      </SvgIcon>
    ),
  },
  {
    id: 'non-duplication',
    title: 'Non-duplication & limits',
    subtitle: 'Other awards and application caps.',
    pattern: /\b(previous recipients?|other.*exemptions?|external funding|third party|other.*awards?|applications?.*permitted|at most .* applications?|one .* application per|not hold another|non-duplication)\b/i,
    idPattern: /(other-award|restriction|limit|duplication)/i,
    icon: (
      <SvgIcon>
        <path d="m12 3 9 4.5-9 4.5-9-4.5L12 3Z" />
        <path d="m3 12 9 4.5 9-4.5M3 16.5 12 21l9-4.5" />
      </SvgIcon>
    ),
  },
]

function categoriseEligibility(eligibility: readonly EligibilityStatement[]) {
  const buckets = new Map<CategoryId, EligibilityStatement[]>()
  for (const cat of CATEGORIES) {
    buckets.set(cat.id, [])
  }

  for (const item of eligibility) {
    let matched = false
    for (const cat of CATEGORIES) {
      if (cat.pattern.test(item.statement) || cat.idPattern.test(item.id)) {
        buckets.get(cat.id)!.push(item)
        matched = true
      }
    }
    if (!matched) {
      buckets.get('admission-enrolment')!.push(item)
    }
  }

  return CATEGORIES.map((cat) => {
    const items = buckets.get(cat.id) ?? []
    const statedItems = items.filter((item) => item.state === 'stated')
    const isStated = statedItems.length > 0
    return {
      ...cat,
      items,
      isStated,
      summaryPill: isStated ? extractSummaryPill(cat.id, statedItems) : null,
    }
  })
}

export function EligibilitySection({ eligibility, sourceCheck }: EligibilitySectionProps) {
  const idPrefix = useId()
  const rows = categoriseEligibility(eligibility)
  const [expanded, setExpanded] = useState<Record<string, boolean>>({})

  const statedCount = rows.filter((row) => row.isStated).length
  const unspecifiedCount = rows.length - statedCount
  const allExpanded = rows.every((row) => Boolean(expanded[row.id]))

  function toggleAll() {
    if (allExpanded) {
      setExpanded({})
      return
    }
    const next: Record<string, boolean> = {}
    for (const row of rows) next[row.id] = true
    setExpanded(next)
  }

  function toggleRow(id: string) {
    setExpanded((prev) => ({ ...prev, [id]: !prev[id] }))
  }

  return (
    <div className="dsec elig-section">
      <h2>Eligibility</h2>
      <p className="muted">
        The provider’s stated requirements, taken from the official source. Not all conditions apply
        to every applicant.
      </p>

      <div className="elig-toolbar">
        <button className="btn btn-secondary sm" type="button" onClick={toggleAll}>
          {allExpanded ? 'Collapse all' : 'Expand all'}
        </button>
      </div>

      <div className="elig-summary">
        <span className="status-covered">{statedCount} stated</span>
        <UnknownBadge label={`${unspecifiedCount} not specified`} />
        {sourceCheck ? (
          <span className="small muted">Source checked {formatDate(sourceCheck.checkedAt)}</span>
        ) : null}
      </div>

      <div className="elig-cards">
        {rows.map((row) => {
          const isOpen = Boolean(expanded[row.id])
          const panelId = `${idPrefix}-${row.id}`
          const cardClass = [
            'elig-card',
            row.isStated ? 'elig-card--stated' : 'elig-card--unspecified',
            row.highlightWhenStated && row.isStated ? 'elig-card--highlight' : '',
          ]
            .filter(Boolean)
            .join(' ')

          return (
            <div className={cardClass} key={row.id}>
              <button
                type="button"
                className="elig-card-trigger"
                aria-expanded={isOpen}
                aria-controls={panelId}
                onClick={() => toggleRow(row.id)}
              >
                <span className="elig-icon">{row.icon}</span>
                <span className="elig-heading">
                  <span className="elig-title">{row.title}</span>
                  <span className="elig-subtitle small muted">{row.subtitle}</span>
                </span>
                <span className="elig-badges">
                  {row.highlightWhenStated && row.isStated ? (
                    <span className="elig-callout-pill">! Read first</span>
                  ) : null}
                  {row.summaryPill ? (
                    <span className="elig-metric-pill">{row.summaryPill}</span>
                  ) : null}
                  {row.isStated ? (
                    <span className="status-covered">Stated</span>
                  ) : (
                    <UnknownBadge label="Not specified" />
                  )}
                  <svg
                    className={`elig-chevron${isOpen ? ' elig-chevron--open' : ''}`}
                    width="18"
                    height="18"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    aria-hidden="true"
                  >
                    <path d="m6 9 6 6 6-6" />
                  </svg>
                </span>
              </button>

              {isOpen ? (
                <div className="elig-card-body" id={panelId}>
                  {row.isStated ? (
                    <ul className="elig-items">
                      {row.items.map((item) => (
                        <li key={item.id}>
                          {item.statement}
                          {item.state !== 'stated' ? (
                            <>
                              {' '}
                              <UnknownBadge label="Not specified" />
                            </>
                          ) : null}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="small muted">
                      The retained official wording does not specify a requirement for this
                      category. Confirm with the provider before applying.
                    </p>
                  )}
                </div>
              ) : null}
            </div>
          )
        })}
      </div>

      <div className="elig-disclaimer small muted">
        These are the provider’s stated requirements, not a decision about you. “Not specified”
        means the retained official wording does not say; it does not mean there is no requirement.
        Grades appear on the provider’s own scale and are never converted.
      </div>
    </div>
  )
}
