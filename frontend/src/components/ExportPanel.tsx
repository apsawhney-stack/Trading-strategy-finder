import type { Source } from '../types';
import { useToast } from './Toast';
import './ExportPanel.css';

interface ExportPanelProps {
    sources: Source[];
    strategyName?: string;
}

export function ExportPanel({ sources, strategyName }: ExportPanelProps) {
    const { addToast } = useToast();

    const exportJSON = () => {
        const data = {
            exported_at: new Date().toISOString(),
            strategy_name: strategyName || 'Strategy Export',
            sources_count: sources.length,
            sources: sources.map(s => ({
                id: s.id,
                url: s.url,
                title: s.title,
                author: s.author,
                source_type: s.source_type,
                published_date: s.published_date,
                extracted_data: s.extracted_data,
                quality_metrics: s.quality_metrics,
            })),
        };

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        downloadBlob(blob, `${strategyName || 'strategy'}-export.json`);
        addToast({ type: 'success', message: 'JSON exported successfully' });
    };

    const exportMarkdown = () => {
        let md = `# ${strategyName || 'Strategy'} Research Export\n\n`;
        md += `**Exported**: ${new Date().toLocaleString()}\n`;
        md += `**Sources Analyzed**: ${sources.length}\n\n`;
        md += `---\n\n`;

        sources.forEach((source, i) => {
            const data = source.extracted_data;
            const quality = source.quality_metrics;

            md += `## ${i + 1}. ${data?.strategy_name?.value || source.title}\n\n`;
            md += `**Source**: [${source.title}](${source.url})\n`;
            md += `**Author**: ${source.author}\n`;
            md += `**Specificity Score**: ${quality.specificity_score.toFixed(1)}/10\n`;
            md += `**Trust Score**: ${quality.trust_score.toFixed(1)}/10\n\n`;

            // Setup Rules
            md += `### Setup\n`;
            if (data?.setup_rules?.underlying?.value) md += `- **Underlying**: ${data.setup_rules.underlying.value}\n`;
            if (data?.setup_rules?.dte?.value) md += `- **DTE**: ${data.setup_rules.dte.value}\n`;
            if (data?.setup_rules?.delta?.value) md += `- **Delta**: ${data.setup_rules.delta.value}\n`;
            if (data?.setup_rules?.strike_selection?.value) md += `- **Strike**: ${data.setup_rules.strike_selection.value}\n`;
            md += `\n`;

            // Management Rules
            md += `### Management\n`;
            if (data?.management_rules?.profit_target?.value) md += `- **Profit Target**: ${data.management_rules.profit_target.value}\n`;
            if (data?.management_rules?.stop_loss?.value) md += `- **Stop Loss**: ${data.management_rules.stop_loss.value}\n`;
            if (data?.management_rules?.adjustment_rules?.value) md += `- **Adjustments**: ${data.management_rules.adjustment_rules.value}\n`;
            md += `\n`;

            // Gaps
            if (quality.gaps.length > 0) {
                md += `### Missing Information\n`;
                quality.gaps.forEach(gap => {
                    md += `- ⚠️ ${gap}\n`;
                });
                md += `\n`;
            }

            // Insights
            if (data?.key_insights?.length > 0) {
                md += `### Key Insights\n`;
                data.key_insights.forEach(insight => {
                    md += `- 💡 ${insight}\n`;
                });
                md += `\n`;
            }

            md += `---\n\n`;
        });

        const blob = new Blob([md], { type: 'text/markdown' });
        downloadBlob(blob, `${strategyName || 'strategy'}-export.md`);
        addToast({ type: 'success', message: 'Markdown exported successfully' });
    };

    const copyBacktestParams = () => {
        // Find the source with highest specificity score
        const bestSource = sources.reduce((best, s) =>
            s.quality_metrics.specificity_score > best.quality_metrics.specificity_score ? s : best
            , sources[0]);

        const data = bestSource?.extracted_data;
        if (!data) {
            addToast({ type: 'error', message: 'No data to copy' });
            return;
        }

        const params = [
            `Strategy: ${data.strategy_name?.value || 'Unknown'}`,
            `Underlying: ${data.setup_rules?.underlying?.value || 'N/A'}`,
            `DTE: ${data.setup_rules?.dte?.value || 'N/A'}`,
            `Delta: ${data.setup_rules?.delta?.value || 'N/A'}`,
            `Width: ${data.setup_rules?.width?.value || 'N/A'}`,
            `Profit Target: ${data.management_rules?.profit_target?.value || 'N/A'}`,
            `Stop Loss: ${data.management_rules?.stop_loss?.value || 'N/A'}`,
        ].join('\n');

        navigator.clipboard.writeText(params);
        addToast({ type: 'success', message: 'Backtest parameters copied to clipboard' });
    };

    const downloadBlob = (blob: Blob, filename: string) => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    return (
        <div className="export-panel">
            <h4>Export</h4>
            <div className="export-buttons">
                <button className="btn btn-secondary" onClick={exportJSON}>
                    📄 JSON
                </button>
                <button className="btn btn-secondary" onClick={exportMarkdown}>
                    📝 Markdown
                </button>
                <button className="btn btn-secondary" onClick={copyBacktestParams}>
                    📋 Copy Backtest Params
                </button>
            </div>
        </div>
    );
}
