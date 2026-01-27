console.log('[SO101] App.tsx loading...')

import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import WizardPage from './pages/WizardPage'
import ComponentsPage from './pages/ComponentsPage'
import ComparisonPage from './pages/ComparisonPage'
import SetupPage from './pages/SetupPage'
import DocsPage from './pages/DocsPage'

console.log('[SO101] All App imports loaded')

function App() {
  console.log('[SO101] App component rendering')
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="wizard" element={<WizardPage />} />
          <Route path="components" element={<ComponentsPage />} />
          <Route path="comparison" element={<ComparisonPage />} />
          <Route path="setup/:setupId" element={<SetupPage />} />
          <Route path="docs" element={<DocsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
