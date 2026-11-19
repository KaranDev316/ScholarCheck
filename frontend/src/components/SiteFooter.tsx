import { useEffect, useState } from 'react'

export function SiteFooter() {
  const [contact, setContact] = useState<string | null>(null)
  useEffect(() => {
    fetch('/api/site')
      .then((r) => (r.ok ? r.json() : null))
      .then((body: { contactEmail?: string } | null) => {
        if (body?.contactEmail && /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(body.contactEmail)) {
          setContact(body.contactEmail)
        }
      })
      .catch(() => {})
  }, [])
  return (
    <footer className="band site-footer">
      <div className="container wrap">
        ScholarCheck shows what official sources say. It is not an eligibility decision and does not
        predict awards. Confirm details with the provider before applying.
        {contact ? (
          <p>
            <a href={`mailto:${contact}`}>Contact ScholarCheck</a>
          </p>
        ) : null}
      </div>
    </footer>
  )
}
