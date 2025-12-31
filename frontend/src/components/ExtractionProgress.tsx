import type { ExtractionStep } from '../types';
import './ExtractionProgress.css';

interface ExtractionProgressProps {
    currentStep: ExtractionStep;
}

const STEPS: { key: ExtractionStep; label: string }[] = [
    { key: 'fetching_content', label: 'Fetching transcript...' },
    { key: 'analyzing_structure', label: 'Analyzing content structure...' },
    { key: 'extracting_strategy', label: 'Extracting strategy parameters...' },
    { key: 'calculating_scores', label: 'Calculating Specificity & Trust scores...' },
    { key: 'complete', label: 'Complete!' },
];

export function ExtractionProgress({ currentStep }: ExtractionProgressProps) {
    const currentIndex = STEPS.findIndex(s => s.key === currentStep);

    return (
        <div className="extraction-progress">
            <div className="progress-steps">
                {STEPS.map((step, index) => {
                    const status = index < currentIndex ? 'done' : index === currentIndex ? 'active' : 'pending';

                    return (
                        <div key={step.key} className={`progress-step step-${status}`}>
                            <div className="step-indicator">
                                {status === 'done' ? '✓' : status === 'active' ? <span className="spinner"></span> : '○'}
                            </div>
                            <span className="step-label">{step.label}</span>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
