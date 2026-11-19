export function NotFoundPage({ id }: { id: string }) {
  return (
    <section className="container wrap notfound">
      <h1 className="h-section">This scholarship isn’t available</h1>
      <p className="muted">
        No published record matches “{id}”. It may have been withdrawn, or the link may be out of
        date.
      </p>
      <a className="btn btn-primary" href="#explore">
        Browse published scholarships
      </a>
    </section>
  )
}
