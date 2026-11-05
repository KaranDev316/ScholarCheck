import { useEffect, useState } from 'react'
export function SiteFooter() {
  const [contact, setContact] = useState<string | null>(null)
  useEffect(() => {
    fetch('/api/site').then(r => r.ok ? r.json() : null).then((body: { contactEmail?: string } | null) => {
      if (body?.contactEmail && /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(body.contactEmail)) setContact(body.contactEmail)
    }).catch(() => {})
  }, [])
  return (
    <footer>
      <div className="wrap">
        ScholarCheck shows what official sources say. It is not an eligibility decision and does not
        predict awards. Details can change, so confirm them with the provider before applying.
        {contact ? <p><a href={`mailto:${contact}`}>Contact ScholarCheck</a></p> : null}
      </div>
    </footer>
  )
}
