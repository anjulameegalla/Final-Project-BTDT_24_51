import { useState } from 'react'
import { ChevronDown, ChevronRight, Terminal } from 'lucide-react'
import SeverityBadge from '../common/SeverityBadge'
import { serviceIcon } from '../../utils/helpers'

export default function FindingRow({ finding }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="border border-slate-700 rounded-lg overflow-hidden">
      {/* Header row */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-3 p-4 hover:bg-slate-700/50 transition-colors text-left"
      >
        <span className="text-lg">{serviceIcon(finding.service)}</span>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-slate-200 truncate">{finding.issue_title}</p>
          <p className="text-xs text-slate-500 truncate">{finding.resource_id}</p>
        </div>
        <SeverityBadge severity={finding.severity} />
        <span className="text-xs text-slate-500 uppercase font-medium w-16 text-right">
          {finding.service}
        </span>
        {expanded ? (
          <ChevronDown size={16} className="text-slate-400 flex-shrink-0" />
        ) : (
          <ChevronRight size={16} className="text-slate-400 flex-shrink-0" />
        )}
      </button>

      {/* Expanded details */}
      {expanded && (
        <div className="border-t border-slate-700 bg-slate-800/50 p-4 space-y-4">
          {/* Description */}
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Description</p>
            <p className="text-sm text-slate-300">{finding.description}</p>
          </div>

          {/* AI Explanation */}
          {finding.ai_explanation && (
            <div className="bg-blue-900/20 border border-blue-800/40 rounded-lg p-3">
              <p className="text-xs font-semibold text-blue-400 uppercase tracking-wider mb-1">
                🤖 AI Explanation
              </p>
              <p className="text-sm text-slate-300">{finding.ai_explanation}</p>
            </div>
          )}

          {/* Why Dangerous */}
          {finding.why_dangerous && (
            <div className="bg-red-900/20 border border-red-800/40 rounded-lg p-3">
              <p className="text-xs font-semibold text-red-400 uppercase tracking-wider mb-1">
                ⚠️ Why It's Dangerous
              </p>
              <p className="text-sm text-slate-300">{finding.why_dangerous}</p>
            </div>
          )}

          {/* Business Impact */}
          {finding.business_impact && (
            <div className="bg-orange-900/20 border border-orange-800/40 rounded-lg p-3">
              <p className="text-xs font-semibold text-orange-400 uppercase tracking-wider mb-1">
                💼 Business Impact
              </p>
              <p className="text-sm text-slate-300">{finding.business_impact}</p>
            </div>
          )}

          {/* Fix Steps */}
          {finding.fix_steps?.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-green-400 uppercase tracking-wider mb-2">
                ✅ Remediation Steps
              </p>
              <ol className="space-y-1">
                {finding.fix_steps.map((step, i) => (
                  <li key={i} className="flex gap-2 text-sm text-slate-300">
                    <span className="text-green-400 font-bold flex-shrink-0">{i + 1}.</span>
                    <span>{step}</span>
                  </li>
                ))}
              </ol>
            </div>
          )}

          {/* CLI Command */}
          {finding.cli_command && (
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1 flex items-center gap-1">
                <Terminal size={12} /> CLI Command
              </p>
              <pre className="bg-slate-900 border border-slate-700 rounded-lg p-3 text-xs text-green-400 overflow-x-auto whitespace-pre-wrap">
                {finding.cli_command}
              </pre>
            </div>
          )}

          {/* Recommendation */}
          {finding.recommendation && (
            <div className="bg-slate-700/50 rounded-lg p-3">
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">
                💡 Best Practice
              </p>
              <p className="text-sm text-slate-300">{finding.recommendation}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
