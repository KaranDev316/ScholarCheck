import { ConnectionStatus } from '../components/ConnectionStatus'
import { assessmentOutcomes, outcomeLabels } from '../types/domain'

/**
 * Home page for the S01 scaffold. It states the decision vocabulary the product
 * will use and proves the API is reachable; source checking and listings follow.
 */
export function HomePage() {
  return (
    <main className="page">
      <header className="masthead">
        <p className="eyebrow">ScholarCheck</p>
        <h1>Know whether a funded degree really fits you</h1>
        <p className="lede">
          For bachelor&rsquo;s, master&rsquo;s and PhD study: discover opportunities
          checked against official sources. See each stated requirement, what
          the funding covers, and the evidence behind every claim. No scores
          and no win probabilities.
        </p>
      </header>

      <section className="panel" aria-labelledby="outcomes-heading">
        <h2 id="outcomes-heading">How an outcome is described</h2>
        <ul className="outcome-list">
          {assessmentOutcomes.map((outcome) => (
            <li key={outcome}>{outcomeLabels[outcome]}</li>
          ))}
        </ul>
        <p className="fine-print">
          Every opportunity ends with exactly one of these four statements, each
          with the reason behind it.
        </p>
      </section>

      <ConnectionStatus />

      <section className="panel" aria-labelledby="next-heading">
        <h2 id="next-heading">What this build includes</h2>
        <p>
          The scaffold and four regression fixtures exist. Source monitoring
          and automatic publication checks are planned; no opportunity is
          published from those fixtures yet. Profile entry and listings follow
          later.
        </p>
      </section>
    </main>
  )
}
