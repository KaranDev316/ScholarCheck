import { ConnectionStatus } from '../components/ConnectionStatus'

/**
 * Home page for the S01 scaffold while the public catalogue is being built.
 */
export function HomePage() {
  return (
    <main className="page">
      <header className="masthead">
        <p className="eyebrow">ScholarCheck</p>
        <h1>Know whether a funded degree really fits you</h1>
        <p className="lede">
          For bachelor&rsquo;s, master&rsquo;s and PhD study: browse scholarships
          checked against official sources. Search by country, study level and
          funding, then inspect stated eligibility, deadlines and evidence.
          Open official application links and share a scholarship page.
        </p>
      </header>

      <ConnectionStatus />

      <section className="panel" aria-labelledby="next-heading">
        <h2 id="next-heading">What this build includes</h2>
        <p>
          The scaffold and four regression fixtures exist. Publication checks
          and the public catalogue are next; no opportunity is published from
          those fixtures yet. After launch, monitoring will start with one
          scholarship.
        </p>
      </section>
    </main>
  )
}
