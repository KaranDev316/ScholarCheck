import { displayUrl, formatDate } from '../data/format'
import type { EvidenceEntry, SourceCheck } from '../data/types'

interface EvidenceBlockProps {
  recordId?: string
  evidence?: readonly EvidenceEntry[]
  sourceCheck: SourceCheck | null
  fallbackUrl: string
}

export function EvidenceBlock({
  recordId,
  evidence,
  sourceCheck,
  fallbackUrl,
}: EvidenceBlockProps) {
  if (!evidence || evidence.length === 0) {
    return (
      <div className="evidence reading">
        <div className="small muted">
          Source:{' '}
          <a href={fallbackUrl} target="_blank" rel="noreferrer">
            {displayUrl(fallbackUrl)}
          </a>
          {sourceCheck ? (
            <>
              {' '}
              · Saved {formatDate(sourceCheck.checkedAt)} ·{' '}
              <span className="result">Matches the official page</span>
            </>
          ) : null}
        </div>
      </div>
    )
  }

  return (
    <div className="evidence-list">
      {evidence.map((entry) => (
        <div
          className="evidence reading"
          id={recordId ? `${recordId}-ev${entry.number}` : undefined}
          key={entry.number}
        >
          <div className="small muted">
            <strong>{entry.claim}</strong>
          </div>
          <blockquote>“{entry.passage}”</blockquote>
          <div className="small muted">
            Source:{' '}
            <a href={entry.url} target="_blank" rel="noreferrer">
              {displayUrl(entry.url)}
            </a>{' '}
            · Saved {formatDate(entry.savedAt)} ·{' '}
            <span className="result">Matches the official page</span>
          </div>
        </div>
      ))}
    </div>
  )
}
