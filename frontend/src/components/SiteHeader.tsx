export type HeaderSection = 'home' | 'explore'

export function SiteHeader({ current }: { current: HeaderSection }) {
  return (
    <header className="top">
      <div className="wrap">
        <a className="brand" href="#home">
          ScholarCheck
        </a>
        <nav aria-label="Main">
          <a href="#home" aria-current={current === 'home' ? 'page' : undefined}>
            Home
          </a>
          <a href="#explore" aria-current={current === 'explore' ? 'page' : undefined}>
            Find scholarships
          </a>
        </nav>
      </div>
    </header>
  )
}
