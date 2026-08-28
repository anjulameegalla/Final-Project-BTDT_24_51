import { format, formatDistanceToNow } from 'date-fns'

export const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A'
  try { return format(new Date(dateStr), 'MMM dd, yyyy HH:mm') }
  catch { return dateStr }
}

export const timeAgo = (dateStr) => {
  if (!dateStr) return ''
  try { return formatDistanceToNow(new Date(dateStr), { addSuffix: true }) }
  catch { return '' }
}

export const severityColor = (sev) => ({
  Critical: 'text-red-400',
  High:     'text-orange-400',
  Medium:   'text-yellow-400',
  Low:      'text-green-400',
}[sev] || 'text-slate-400')

export const severityBg = (sev) => ({
  Critical: 'bg-red-900/30 border-red-800',
  High:     'bg-orange-900/30 border-orange-800',
  Medium:   'bg-yellow-900/30 border-yellow-800',
  Low:      'bg-green-900/30 border-green-800',
}[sev] || 'bg-slate-700 border-slate-600')

export const severityBadgeClass = (sev) => ({
  Critical: 'badge-critical',
  High:     'badge-high',
  Medium:   'badge-medium',
  Low:      'badge-low',
}[sev] || 'badge-low')

export const scoreColor = (score) => {
  if (score >= 90) return 'text-green-400'
  if (score >= 70) return 'text-yellow-400'
  if (score >= 40) return 'text-orange-400'
  return 'text-red-400'
}

export const riskLevelColor = (level) => ({
  Secure:      'text-green-400',
  Moderate:    'text-yellow-400',
  'High Risk': 'text-orange-400',
  Critical:    'text-red-400',
}[level] || 'text-slate-400')

export const serviceIcon = (service) => ({
  iam:        '👤',
  s3:         '🪣',
  ec2:        '💻',
  cloudtrail: '📋',
}[service?.toLowerCase()] || '🔍')
