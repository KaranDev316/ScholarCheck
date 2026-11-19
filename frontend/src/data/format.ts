/**
 * Display formatting. Dates are rendered in UTC so a saved copy does not shift
 * a day depending on the visitor's time zone.
 */

import type { Scholarship, ScholarshipDeadline } from './types'

const dateFormatter = new Intl.DateTimeFormat('en-GB', {
  day: 'numeric',
  month: 'short',
  year: 'numeric',
  timeZone: 'UTC',
})

const dateTimeFormatter = new Intl.DateTimeFormat('en-GB', {
  day: 'numeric',
  month: 'short',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
  timeZone: 'UTC',
  timeZoneName: 'short',
})

export function formatDate(iso: string): string {
  const date = new Date(iso)
  return Number.isNaN(date.getTime()) ? 'an unknown date' : dateFormatter.format(date)
}

export function formatDateTime(iso: string): string {
  const date = new Date(iso)
  return Number.isNaN(date.getTime()) ? 'an unknown time' : dateTimeFormatter.format(date)
}

/** "Checked 3 days ago" wording for the card footer. */
export function formatCheckedAgo(iso: string, now: Date = new Date()): string {
  const checked = new Date(iso)
  if (Number.isNaN(checked.getTime())) return 'on an unknown date'

  const days = Math.floor((now.getTime() - checked.getTime()) / 86_400_000)
  if (days <= 0) return 'today'
  if (days === 1) return '1 day ago'
  return `${days} days ago`
}

const CURRENCY_SYMBOLS: Record<string, string> = {
  AUD: '$',
  CAD: '$',
  EUR: '€',
  GBP: '£',
  HKD: '$',
  NZD: '$',
  SGD: '$',
  USD: '$',
}

export interface FormattedAward {
  /** Large display text: amount only (e.g. "CAD $40,000" or "$40,000"). */
  amountText: string
  /** Single-line representation for descriptions and inline copy (e.g. "CAD $40,000 / year" or "$40,000 / year"). */
  inlineText: string
  /** Smaller qualifier line rendered below the large amount (e.g. "per year", "per year for 36 months"). */
  qualifierText: string | null
  /** Muted fallback note shown only when the source does not state a currency. */
  currencyNote: string | null
}

function normaliseAmountValue(amount: number | string): { prefix: string; numeric: string } {
  if (typeof amount === 'number') {
    return {
      prefix: '',
      numeric: new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(amount),
    }
  }

  let cleaned = amount.replace(/\s*\(currency not stated\)/gi, '').trim()
  let prefix = ''

  const upToMatch = cleaned.match(/^(up to)\s+/i)
  if (upToMatch) {
    prefix = `${upToMatch[1]} `
    cleaned = cleaned.slice(upToMatch[0].length).trim()
  }

  // Strip any leading currency code/symbol so formatAward is the single authority.
  cleaned = cleaned.replace(/^(?:(?:CA|AU|US|NZ|HK|SG)\$|[A-Z]{3}\s*[$€£]?|[$€£])\s*/, '').trim()

  // Format plain ungrouped numbers like "40000" -> "40,000", preserving decimals.
  if (/^\d+(?:\.\d+)?$/.test(cleaned)) {
    const [whole, fraction] = cleaned.split('.')
    const grouped = Number(whole).toLocaleString('en-US')
    cleaned = fraction !== undefined ? `${grouped}.${fraction}` : grouped
  }

  return { prefix, numeric: cleaned }
}

function formatPeriodSuffix(period?: string | null): string | null {
  if (!period) return null
  if (/\bper\s+year\b|\/\s*year\b|\bannual(?:ly)?\b/i.test(period)) return '/ year'
  if (/\bper\s+month\b|\/\s*month\b|\bmonthly\b/i.test(period)) return '/ month'
  if (/\bper\s+term\b|\/\s*term\b/i.test(period)) return '/ term'
  if (/\bper\s+week\b|\/\s*week\b|\bweekly\b/i.test(period)) return '/ week'
  return null
}

/**
 * Shared award formatter used across hero cards, list cards, detail pages and
 * generated descriptions so amount and currency wording can never disagree.
 */
export function formatAward(
  amount: number | string,
  currency?: string | null,
  period?: string | null,
): FormattedAward {
  const { prefix, numeric } = normaliseAmountValue(amount)
  const code = currency?.trim().toUpperCase() || null

  let amountText: string
  let currencyNote: string | null

  if (code) {
    const symbol = CURRENCY_SYMBOLS[code] ?? ''
    amountText = `${prefix}${code} ${symbol}${numeric}`
    currencyNote = null
  } else {
    amountText = `${prefix}$${numeric}`
    currencyNote = 'Currency per source'
  }

  const qualifierText = period?.trim() ? period.trim() : null
  const periodSuffix = formatPeriodSuffix(qualifierText)
  const inlineText = periodSuffix ? `${amountText} ${periodSuffix}` : amountText

  return {
    amountText,
    inlineText,
    qualifierText,
    currencyNote,
  }
}

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

/**
 * Ensures any headline amount mentioned in a scholarship's summary uses the
 * exact same formatAward output as the headline display.
 */
export function formatScholarshipSummary(record: Scholarship): string {
  if (!record.headline) return record.summary

  const currency =
    record.headline.currency !== undefined ? record.headline.currency : record.currency
  const award = formatAward(record.headline.amount, currency, record.headline.basis)
  const { numeric } = normaliseAmountValue(record.headline.amount)
  if (!numeric) return record.summary

  const ungrouped = numeric.replace(/,/g, '')
  const numberPattern =
    ungrouped !== numeric
      ? `(?:${escapeRegExp(numeric)}|${escapeRegExp(ungrouped)})`
      : escapeRegExp(numeric)

  const mentionPattern = new RegExp(
    `(?<![\\dA-Za-z])(?:(?:(?:CA|AU|US|NZ|HK|SG)\\$|[A-Z]{3}\\s*[$€£]?|[$€£])\\s*)?${numberPattern}(?!\\d)(?:\\s*\\(currency not stated\\))?(?:\\s*(?:per\\s+(?:year|month|term|week)|\\/\\s*(?:year|month|term|week)))?`,
    'gi',
  )

  return record.summary.replace(mentionPattern, (match) => {
    const hasPeriod = /(?:per\s+(?:year|month|term|week)|\/\s*(?:year|month|term|week))/i.test(match)
    return hasPeriod ? award.inlineText : award.amountText
  })
}

export type DeadlineBadgeTone = 'neutral' | 'closing-soon' | 'closed'

export interface FormattedDeadline {
  /** Primary date/value shown inline with the Deadline label (e.g. "18 Dec 2026", "Rolling"), or null when the note carries the copy. */
  text: string | null
  /** Supporting plain-language note displayed below the row. */
  note: string | null
  /** Accessible badge label (never empty; never colour-only). */
  badgeLabel: string
  badgeTone: DeadlineBadgeTone
  sourceUrl: string | null
}

function parseIsoUtcDay(iso: string): number | null {
  const dateOnly = iso.match(/^(\d{4})-(\d{2})-(\d{2})/)
  if (dateOnly) {
    const year = Number(dateOnly[1])
    const month = Number(dateOnly[2]) - 1
    const day = Number(dateOnly[3])
    const parsed = new Date(Date.UTC(year, month, day))
    if (
      parsed.getUTCFullYear() === year &&
      parsed.getUTCMonth() === month &&
      parsed.getUTCDate() === day
    ) {
      return parsed.getTime()
    }
    return null
  }
  const parsed = new Date(iso)
  if (Number.isNaN(parsed.getTime())) return null
  return Date.UTC(parsed.getUTCFullYear(), parsed.getUTCMonth(), parsed.getUTCDate())
}

/**
 * Formats a scholarship deadline and derives its accessible status badge
 * relative to today's UTC calendar date.
 */
export function formatDeadline(
  deadline?: ScholarshipDeadline | null,
  now: Date = new Date(),
): FormattedDeadline {
  const note = deadline?.note?.trim() || null
  const sourceUrl = deadline?.sourceUrl?.trim() || null

  if (!deadline || deadline.type === 'unknown') {
    return {
      text: note ? null : 'Not stated',
      note,
      badgeLabel: 'Check with institution',
      badgeTone: 'neutral',
      sourceUrl,
    }
  }

  if (deadline.type === 'varies') {
    return {
      text: note ? null : 'Varies by institution',
      note,
      badgeLabel: 'Check with institution',
      badgeTone: 'neutral',
      sourceUrl,
    }
  }

  if (deadline.type === 'rolling') {
    return {
      text: 'Rolling',
      note,
      badgeLabel: 'Rolling',
      badgeTone: 'neutral',
      sourceUrl,
    }
  }

  const deadlineDay = deadline.date ? parseIsoUtcDay(deadline.date) : null
  if (deadlineDay === null || !deadline.date) {
    return {
      text: note ? null : 'Not stated',
      note,
      badgeLabel: 'Check with institution',
      badgeTone: 'neutral',
      sourceUrl,
    }
  }

  const todayUtc = Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate())
  const diffDays = Math.round((deadlineDay - todayUtc) / 86_400_000)

  if (diffDays < 0) {
    return {
      text: formatDate(deadline.date),
      note,
      badgeLabel: 'Closed',
      badgeTone: 'closed',
      sourceUrl,
    }
  }

  if (diffDays <= 30) {
    return {
      text: formatDate(deadline.date),
      note,
      badgeLabel: 'Closing soon',
      badgeTone: 'closing-soon',
      sourceUrl,
    }
  }

  return {
    text: formatDate(deadline.date),
    note,
    badgeLabel: 'Open',
    badgeTone: 'neutral',
    sourceUrl,
  }
}

/** Host and path of an official page, without the scheme. */
export function displayUrl(url: string): string {
  return url.replace(/^https?:\/\//, '')
}
