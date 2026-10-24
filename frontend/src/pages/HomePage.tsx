import { ConnectionStatus } from '../components/ConnectionStatus'

/**
 * Home page for the S01 scaffold while the public catalogue is being built.
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

      <ConnectionStatus />

      <section className="panel" aria-labelledby="next-heading">
        <h2 id="next-heading">What this build includes</h2>
        <p>
          The scaffold and four regression fixtures exist. Publication checks
          and the public catalogue are next; no opportunity is published yet.
          The launch set will use the best-evidenced records. After launch,
          monitoring will start with one scholarship.
        </p>
      </section>
    </main>
  )
}
