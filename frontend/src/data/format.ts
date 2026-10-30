/**
 * Display formatting. Dates are rendered in UTC so a saved copy does not shift
 * a day depending on the visitor's time zone.
 */

const dateFormatter = new Intl.DateTimeFormat('en-GB', {
  day: 'numeric',
  month: 'long',
  year: 'numeric',
  timeZone: 'UTC',
})

const dateTimeFormatter = new Intl.DateTimeFormat('en-GB', {
  day: 'numeric',
  month: 'long',
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

/** Host and path of an official page, without the scheme. */
export function displayUrl(url: string): string {
  return url.replace(/^https?:\/\//, '')
}
