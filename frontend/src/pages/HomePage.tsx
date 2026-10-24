/**
 * Public landing page while source-backed listings are being prepared.
 */
export function HomePage() {
  return (
    <main className="page">
      <header className="masthead">
        <p className="eyebrow">ScholarCheck</p>
        <h1>Find funding. Check the evidence. Decide for yourself.</h1>
        <p className="lede">
          For bachelor&rsquo;s, master&rsquo;s and PhD study: every amount and
          deadline will sit beside the official wording it came from. Search
          by country, study level and funding type, then open the provider&rsquo;s
          own requirements and application pages. No account needed.
        </p>
      </header>

      <section className="panel" aria-labelledby="availability-heading">
        <h2 id="availability-heading">Scholarships are being checked</h2>
        <p>
          Listings will appear here when their details can be supported by
          official sources. No scholarships are published yet.
        </p>
      </section>
    </main>
  )
}
