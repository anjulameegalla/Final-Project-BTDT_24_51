import { motion } from 'framer-motion'
import { scoreColor, riskLevelColor } from '../../utils/helpers'

const serviceInfo = {
  iam:        { label: 'IAM',         emoji: '👤', desc: 'Identity & Access Management' },
  s3:         { label: 'S3',          emoji: '🪣', desc: 'Simple Storage Service' },
  ec2:        { label: 'EC2',         emoji: '💻', desc: 'Elastic Compute Cloud' },
  cloudtrail: { label: 'CloudTrail',  emoji: '📋', desc: 'API Activity Logging' },
}

function getRiskLevel(score) {
  if (score >= 90) return 'Secure'
  if (score >= 70) return 'Moderate'
  if (score >= 40) return 'High Risk'
  return 'Critical'
}

export default function ServiceCard({ service, score = 100, issueCount = 0 }) {
  const info = serviceInfo[service] || { label: service, emoji: '🔍', desc: '' }
  const riskLevel = getRiskLevel(score)

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="card hover:border-slate-600 transition-all"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-2xl">{info.emoji}</span>
          <div>
            <p className="font-semibold text-white text-sm">{info.label}</p>
            <p className="text-xs text-slate-500">{info.desc}</p>
          </div>
        </div>
        <span className={`text-xs font-semibold ${riskLevelColor(riskLevel)}`}>
          {riskLevel}
        </span>
      </div>

      {/* Score bar */}
      <div className="mt-3">
        <div className="flex justify-between text-xs mb-1">
          <span className="text-slate-400">Security Score</span>
          <span className={`font-bold ${scoreColor(score)}`}>{score}/100</span>
        </div>
        <div className="w-full bg-slate-700 rounded-full h-2">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${score}%` }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
            className="h-2 rounded-full"
            style={{
              background: score >= 90 ? '#16a34a' : score >= 70 ? '#d97706' : score >= 40 ? '#ea580c' : '#dc2626'
            }}
          />
        </div>
      </div>

      <p className="text-xs text-slate-500 mt-2">
        {issueCount === 0 ? '✅ No issues found' : `⚠️ ${issueCount} issue${issueCount > 1 ? 's' : ''} detected`}
      </p>
    </motion.div>
  )
}
