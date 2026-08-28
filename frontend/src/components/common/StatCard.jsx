import { motion } from 'framer-motion'

export default function StatCard({ title, value, icon: Icon, color = 'blue', subtitle }) {
  const colorMap = {
    blue:   'text-blue-400 bg-blue-900/30',
    red:    'text-red-400 bg-red-900/30',
    orange: 'text-orange-400 bg-orange-900/30',
    yellow: 'text-yellow-400 bg-yellow-900/30',
    green:  'text-green-400 bg-green-900/30',
    purple: 'text-purple-400 bg-purple-900/30',
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card hover:border-slate-600 transition-colors"
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-slate-400 font-medium">{title}</p>
          <p className="text-3xl font-bold text-white mt-1">{value}</p>
          {subtitle && <p className="text-xs text-slate-500 mt-1">{subtitle}</p>}
        </div>
        {Icon && (
          <div className={`p-3 rounded-xl ${colorMap[color] || colorMap.blue}`}>
            <Icon size={22} className={colorMap[color]?.split(' ')[0]} />
          </div>
        )}
      </div>
    </motion.div>
  )
}
