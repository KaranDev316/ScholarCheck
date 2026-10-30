export function NotFoundPage({ id }: { id: string }) {
  return (
    <section className="wrap notfound">
      <h1 className="h-section">This scholarship isn’t available</h1>
      <p className="mute">
        No published record matches “{id}”. It may have been withdrawn, or the link may be out of
        date.
      </p>
      <a className="btn" href="#explore">
        Browse published scholarships
      </a>
    </section>
  )
}
