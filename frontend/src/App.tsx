import { getCatalogue } from './data/catalogue'
import { HomePage } from './pages/HomePage'

function App() {
  const catalogue = getCatalogue()
  return <HomePage records={catalogue.records} isDevelopment={catalogue.isDevelopment} />
}

export default App
