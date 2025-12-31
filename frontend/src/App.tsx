import { useState } from 'react'
import { Header } from './components/Header'
import { URLInput } from './components/URLInput'
import { SourceCard } from './components/SourceCard'
import { SourceDetail } from './components/SourceDetail'
import { ExtractionProgress } from './components/ExtractionProgress'
import { DiscoveryModal } from './components/DiscoveryModal'
import { extractSource } from './services/api'
import type { Source, ExtractionStep } from './types'
import './App.css'

function App() {
  const [sources, setSources] = useState<Source[]>([])
  const [isExtracting, setIsExtracting] = useState(false)
  const [currentStep, setCurrentStep] = useState<ExtractionStep>('fetching_content')
  const [error, setError] = useState<string | null>(null)
  const [selectedSource, setSelectedSource] = useState<Source | null>(null)
  const [showDiscovery, setShowDiscovery] = useState(false)

  const handleExtract = async (url: string) => {
    setIsExtracting(true)
    setError(null)
    setCurrentStep('fetching_content')

    try {
      const steps: ExtractionStep[] = [
        'fetching_content',
        'analyzing_structure',
        'extracting_strategy',
        'calculating_scores',
        'complete'
      ]

      let stepIndex = 0
      const stepInterval = setInterval(() => {
        stepIndex++
        if (stepIndex < steps.length - 1) {
          setCurrentStep(steps[stepIndex])
        }
      }, 2000)

      const result = await extractSource(url)
      clearInterval(stepInterval)

      if (result.success && result.source) {
        setCurrentStep('complete')
        setSources(prev => [result.source!, ...prev])
      } else {
        setError(result.error || 'Extraction failed')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Extraction failed')
    } finally {
      setIsExtracting(false)
    }
  }

  const handleBatchExtract = async (urls: string[]) => {
    for (const url of urls) {
      await handleExtract(url)
    }
  }

  return (
    <div className="app">
      <Header onDiscoverClick={() => setShowDiscovery(true)} />

      <main className="main-content">
        <div className="container">
          <section className="search-section">
            <h2>Research a Strategy</h2>
            <URLInput onSubmit={handleExtract} disabled={isExtracting} />

            {isExtracting && (
              <ExtractionProgress currentStep={currentStep} />
            )}

            {error && (
              <div className="error-message">
                <span>⚠️</span> {error}
              </div>
            )}
          </section>

          <section className="sources-section">
            <div className="section-header">
              <h3>Extracted Sources</h3>
              <span className="text-muted">{sources.length} sources</span>
            </div>

            {sources.length === 0 ? (
              <div className="empty-state">
                <p>No sources yet. Paste a YouTube, Reddit, or article URL above to extract strategy data.</p>
                <button
                  className="btn btn-secondary"
                  onClick={() => setShowDiscovery(true)}
                >
                  🔍 Discover Sources
                </button>
              </div>
            ) : (
              <div className="sources-list">
                {sources.map(source => (
                  <SourceCard
                    key={source.id}
                    source={source}
                    onClick={() => setSelectedSource(source)}
                  />
                ))}
              </div>
            )}
          </section>
        </div>
      </main>

      {selectedSource && (
        <SourceDetail
          source={selectedSource}
          onClose={() => setSelectedSource(null)}
        />
      )}

      {showDiscovery && (
        <DiscoveryModal
          onClose={() => setShowDiscovery(false)}
          onExtract={handleBatchExtract}
        />
      )}
    </div>
  )
}

export default App

