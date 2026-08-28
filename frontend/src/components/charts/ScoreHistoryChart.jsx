import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine
} from 'recharts'
import { format } from 'date-fns'

export default function ScoreHistoryChart({ scans = [] }) {
  const data = [...scans]
    .reverse()
    .slice(-10)
    .map(s => ({
      date: format(new Date(s.scan_date || s.created_at), 'MMM dd'),
      score: s.overall_score,
    }))

  if (!data.length) {
    return (
      <div className="flex items-center justify-center h-48 text-slate-500 text-sm">
        Run scans to see score history
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={220}>
      <LineChart data={data} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
        <XAxis dataKey="date" tick={{ fill: '#94a3b8', fontSize: 11 }} />
        <YAxis domain={[0, 100]} tick={{ fill: '#94a3b8', fontSize: 11 }} />
        <Tooltip
          contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8 }}
          labelStyle={{ color: '#f1f5f9' }}
          itemStyle={{ color: '#3b82f6' }}
        />
        <ReferenceLine y={90} stroke="#16a34a" strokeDasharray="4 4" label={{ value: 'Secure', fill: '#16a34a', fontSize: 10 }} />
        <ReferenceLine y={70} stroke="#d97706" strokeDasharray="4 4" label={{ value: 'Moderate', fill: '#d97706', fontSize: 10 }} />
        <ReferenceLine y={40} stroke="#ea580c" strokeDasharray="4 4" label={{ value: 'High Risk', fill: '#ea580c', fontSize: 10 }} />
        <Line
          type="monotone"
          dataKey="score"
          stroke="#3b82f6"
          strokeWidth={2.5}
          dot={{ fill: '#3b82f6', r: 4 }}
          activeDot={{ r: 6 }}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
