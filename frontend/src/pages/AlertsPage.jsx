import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { Bell, BellOff, CheckCircle, XCircle, Send } from 'lucide-react'
import Layout from '../components/common/Layout'
import LoadingSpinner from '../components/common/LoadingSpinner'
import SeverityBadge from '../components/common/SeverityBadge'
import { alertService } from '../services/scanService'
import { formatDate, timeAgo } from '../utils/helpers'

export default function AlertsPage() {
  const [alerts, setAlerts]   = useState([])
  const [loading, setLoading] = useState(true)
  const [testing, setTesting] = useState(false)

  useEffect(() => { fetchAlerts() }, [])

  const fetchAlerts = async () => {
    setLoading(true)
    try {
      const res = await alertService.list()
      setAlerts(res.data.alerts || [])
    } catch {
      toast.error('Failed to load alerts')
    } finally {
      setLoading(false)
    }
  }

  const handleTestAlert = async () => {
    setTesting(true)
    try {
      const res = await alertService.test()
      if (res.data.success) {
        toast.success('Test alert sent successfully!')
      } else {
        toast.error('Test alert failed — check SES configuration')
      }
    } catch {
      toast.error('Failed to send test alert')
    } finally {
      setTesting(false)
    }
  }

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner size="lg" text="Loading alerts..." />
        </div>
      </Layout>
    )
  }

  const sentCount   = alerts.filter(a => a.sent_status === 'sent').length
  const failedCount = alerts.filter(a => a.sent_status === 'failed').length

  return (
    <Layout>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white">Security Alerts</h1>
          <p className="text-slate-400 text-sm mt-1">
            Email notifications for critical and high severity findings.
          </p>
        </div>
        <button onClick={handleTestAlert} disabled={testing} className="btn-secondary">
          {testing ? (
            <><span className="w-4 h-4 border-2 border-slate-400/30 border-t-slate-300 rounded-full animate-spin" /> Sending...</>
          ) : (
            <><Send size={16} /> Send Test Alert</>
          )}
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        {[
          { label: 'Total Alerts', value: alerts.length,  color: 'text-white',       bg: 'bg-slate-700/50' },
          { label: 'Sent',         value: sentCount,       color: 'text-green-400',   bg: 'bg-green-900/20' },
          { label: 'Failed',       value: failedCount,     color: 'text-red-400',     bg: 'bg-red-900/20' },
        ].map(({ label, value, color, bg }) => (
          <div key={label} className={`card ${bg}`}>
            <p className="text-sm text-slate-400">{label}</p>
            <p className={`text-3xl font-bold mt-1 ${color}`}>{value}</p>
          </div>
        ))}
      </div>

      {/* Alert list */}
      <div className="card">
        <h2 className="text-sm font-semibold text-slate-300 mb-4">Alert History</h2>
        {alerts.length === 0 ? (
          <div className="text-center py-16 text-slate-500">
            <BellOff size={40} className="mx-auto mb-3" />
            <p className="font-medium">No alerts yet</p>
            <p className="text-sm mt-1">Alerts are sent when Critical or High severity issues are detected.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {alerts.map((alert, i) => (
              <motion.div
                key={alert._id || i}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                className="flex items-start gap-4 p-4 bg-slate-700/40 rounded-lg border border-slate-700"
              >
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                  alert.sent_status === 'sent' ? 'bg-green-900/40' : 'bg-red-900/40'
                }`}>
                  {alert.sent_status === 'sent'
                    ? <CheckCircle size={16} className="text-green-400" />
                    : <XCircle size={16} className="text-red-400" />
                  }
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap mb-1">
                    <SeverityBadge severity={alert.severity} />
                    <span className="text-xs text-slate-500 uppercase font-medium">
                      {alert.affected_service}
                    </span>
                    <span className={`text-xs font-medium ${
                      alert.sent_status === 'sent' ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {alert.sent_status === 'sent' ? '✓ Sent' : '✗ Failed'}
                    </span>
                  </div>
                  <p className="text-sm text-slate-300">{alert.message}</p>
                  <p className="text-xs text-slate-500 mt-1">{timeAgo(alert.created_at)}</p>
                </div>
                <div className="text-right flex-shrink-0">
                  <p className="text-xs text-slate-500">{formatDate(alert.created_at)}</p>
                  <p className="text-xs text-slate-600 mt-0.5 capitalize">{alert.channel}</p>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>

      {/* Alert config info */}
      <div className="card mt-6">
        <h2 className="text-sm font-semibold text-slate-300 mb-3">⚙️ Alert Configuration</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-slate-400 mb-2">Alerts are triggered for:</p>
            <ul className="space-y-1 text-slate-300">
              <li className="flex items-center gap-2"><span className="badge-critical">Critical</span> All critical findings</li>
              <li className="flex items-center gap-2"><span className="badge-high">High</span> All high severity findings</li>
            </ul>
          </div>
          <div>
            <p className="text-slate-400 mb-2">Delivery channel:</p>
            <p className="text-slate-300">Email via AWS SES</p>
            <p className="text-xs text-slate-500 mt-1">
              Configure <code className="bg-slate-700 px-1 rounded">ALERT_EMAIL_FROM</code> and{' '}
              <code className="bg-slate-700 px-1 rounded">ALERT_EMAIL_TO</code> in your .env file.
            </p>
          </div>
        </div>
      </div>
    </Layout>
  )
}
