import { motion } from 'framer-motion'
import { scoreColor, riskLevelColor } from '../../utils/helpers'

export default function ScoreGauge({ score = 0, riskLevel = 'Unknown' }) {
  const radius = 70
  const stroke = 10
  const normalizedRadius = radius - stroke / 2
  const circumference = 2 * Math.PI * normalizedRadius
  const progress = Math.max(0, Math.min(100, score))
  const strokeDashoffset = circumference - (progress / 100) * circumference

  const colorMap = {
    Secure:      '#16a34a',
    Moderate:    '#d97706',
    'High Risk': '#ea580c',
    Critical:    '#dc2626',
    Unknown:     '#64748b',
  }
  const color = colorMap[riskLevel] || '#64748b'

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative">
        <svg height={radius * 2} width={radius * 2}>
          {/* Background circle */}
          <circle
            stroke="#334155"
            fill="transparent"
            strokeWidth={stroke}
            r={normalizedRadius}
            cx={radius}
            cy={radius}
          />
          {/* Progress circle */}
          <motion.circle
            stroke={color}
            fill="transparent"
            strokeWidth={stroke}
            strokeDasharray={`${circumference} ${circumference}`}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1.2, ease: 'easeOut' }}
            strokeLinecap="round"
            r={normalizedRadius}
            cx={radius}
            cy={radius}
            style={{ transform: 'rotate(-90deg)', transformOrigin: '50% 50%' }}
          />
        </svg>
        {/* Score text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.span
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
            className={`text-3xl font-bold ${scoreColor(score)}`}
          >
            {score}
          </motion.span>
          <span className="text-xs text-slate-400">/ 100</span>
        </div>
      </div>
      <div className={`text-sm font-semibold ${riskLevelColor(riskLevel)}`}>
        {riskLevel}
      </div>
    </div>
  )
}
