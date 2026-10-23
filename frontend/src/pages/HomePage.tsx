import { ConnectionStatus } from '../components/ConnectionStatus'
import { assessmentOutcomes, outcomeLabels } from '../types/domain'

/**
 * Home page for the S01 scaffold. It states the decision vocabulary the product
 * will use and proves the API is reachable; listings arrive in later steps.
 */
export function HomePage() {
  return (
    <main className="page">
      <header className="masthead">
        <p className="eyebrow">ScholarCheck</p>
        <h1>Know whether a funded master&rsquo;s really fits you</h1>
        <p className="lede">
          Check each stated requirement, see what the funding actually covers,
          and open the official source behind every claim. No scores and no win
          probabilities.
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
          Scaffold complete: shared domain types, a health endpoint and this page.
          Profile entry, listings, evidence panels and saving come next in slice
          S01.
        </p>
      </section>
    </main>
  )
}
