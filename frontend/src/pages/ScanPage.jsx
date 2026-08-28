import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { ScanLine, Play, Trash2, Clock, CheckCircle, XCircle, Loader } from 'lucide-react'
import Layout from '../components/common/Layout'
import LoadingSpinner from '../components/common/LoadingSpinner'
import SeverityBadge from '../components/common/SeverityBadge'
import FindingRow from '../components/dashboard/FindingRow'
import { scanService, awsService } from '../services/scanService'
import { formatDate, timeAgo, scoreColor, riskLevelColor } from '../utils/helpers'

const StatusIcon = ({ status }) => {
  if (status === 'completed') return <CheckCircle size={16} className="text-green-400" />
  if (status === 'failed')    return <XCircle size={16} className="text-red-400" />
  return <Loader size={16} className="text-blue-400 animate-spin" />
}

export default function ScanPage() {
  const navigate = useNavigate()

  const [history, setHistory]       = useState([])
  const [selected, setSelected]     = useState(null)
  const [loading, setLoading]       = useState(true)
  const [scanning, setScanning]     = useState(false)
  const [detailLoading, setDetailLoading] = useState(false)
  const [filter, setFilter]         = useState('All')
  const [awsAccountId, setAwsAccountId] = useState(null)

  useEffect(() => { fetchHistory() }, [])

  const fetchHistory = async () => {
    setLoading(true)
    try {
      const [histRes, awsRes] = await Promise.allSettled([
        scanService.getHistory(20),
        awsService.getStatus(),
      ])
      if (histRes.status === 'fulfilled') {
        const scans = histRes.value.data.scans || []
        setHistory(scans)
        if (scans.length > 0) loadScanDetail(scans[0].id)
      }
      if (awsRes.status === 'fulfilled') {
        setAwsAccountId(awsRes.value.data.account_id)
      }
    } finally {
      setLoading(false)
    }
  }

  const loadScanDetail = async (scanId) => {
    setDetailLoading(true)
    try {
      const res = await scanService.getScan(scanId)
      setSelected(res.data)
    } catch (err) {
      toast.error('Failed to load scan details')
    } finally {
      setDetailLoading(false)
    }
  }

  const handleStartScan = async () => {
    if (!awsAccountId) {
      toast.error('Connect an AWS account first')
      navigate('/connect')
      return
    }
    setScanning(true)
    try {
      const res = await scanService.startScan(awsAccountId, ['iam', 's3', 'ec2', 'cloudtrail'])
      const scanId = res.data.scan_id
      toast.success('Scan started!')

      // Poll for completion
      let attempts = 0
      const poll = setInterval(async () => {
        attempts++
        try {
          const r = await scanService.getScan(scanId)
          if (r.data.status === 'completed' || r.data.status === 'failed') {
            clearInterval(poll)
            setScanning(false)
            if (r.data.status === 'completed') {
              fetchHistory()
              toast.success('Scan completed!')
            } else {
              toast.error(r.data.error || 'Scan failed')
            }
          }
        } catch {}
        if (attempts > 40) { clearInterval(poll); setScanning(false) }
      }, 3000)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to start scan')
      setScanning(false)
    }
  }

  const handleDelete = async (scanId, e) => {
    e.stopPropagation()
    if (!confirm('Delete this scan?')) return
    try {
      await scanService.deleteScan(scanId)
      toast.success('Scan deleted')
      if (selected?.id === scanId) setSelected(null)
      fetchHistory()
    } catch {
      toast.error('Failed to delete scan')
    }
  }

  const filteredFindings = (selected?.findings || []).filter(f =>
    filter === 'All' || f.severity === filter
  )

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner size="lg" text="Loading scan history..." />
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white">Scan Results</h1>
          <p className="text-slate-400 text-sm mt-1">{history.length} scan{history.length !== 1 ? 's' : ''} in history</p>
        </div>
        <button onClick={handleStartScan} disabled={scanning} className="btn-primary">
          {scanning ? (
            <><span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Scanning...</>
          ) : (
            <><Play size={16} /> New Scan</>
          )}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Scan history list */}
        <div className="lg:col-span-1">
          <div className="card p-0 overflow-hidden">
            <div className="p-4 border-b border-slate-700">
              <h2 className="text-sm font-semibold text-slate-300">Scan History</h2>
            </div>
            {history.length === 0 ? (
              <div className="p-8 text-center text-slate-500">
                <ScanLine size={32} className="mx-auto mb-2" />
                <p className="text-sm">No scans yet</p>
              </div>
            ) : (
              <div className="divide-y divide-slate-700 max-h-[600px] overflow-y-auto">
                {history.map(scan => (
                  <button
                    key={scan.id}
                    onClick={() => loadScanDetail(scan.id)}
                    className={`w-full p-4 text-left hover:bg-slate-700/50 transition-colors ${
                      selected?.id === scan.id ? 'bg-blue-900/20 border-l-2 border-blue-500' : ''
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <StatusIcon status={scan.status} />
                        <span className={`text-sm font-semibold ${scoreColor(scan.overall_score)}`}>
                          {scan.overall_score}/100
                        </span>
                      </div>
                      <div className="flex items-center gap-1">
                        <span className={`text-xs font-medium ${riskLevelColor(scan.risk_level)}`}>
                          {scan.risk_level}
                        </span>
                        <button
                          onClick={(e) => handleDelete(scan.id, e)}
                          className="p-1 text-slate-500 hover:text-red-400 transition-colors ml-1"
                        >
                          <Trash2 size={13} />
                        </button>
                      </div>
                    </div>
                    <p className="text-xs text-slate-400 flex items-center gap-1">
                      <Clock size={11} /> {timeAgo(scan.scan_date || scan.created_at)}
                    </p>
                    <p className="text-xs text-slate-500 mt-1">
                      {scan.total_issues} issues · {scan.critical_count} critical
                    </p>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Scan detail */}
        <div className="lg:col-span-2">
          {detailLoading ? (
            <div className="card flex items-center justify-center h-64">
              <LoadingSpinner text="Loading findings..." />
            </div>
          ) : selected ? (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
              {/* Summary */}
              <div className="card">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h2 className="text-lg font-bold text-white">
                      Score: <span className={scoreColor(selected.overall_score)}>{selected.overall_score}/100</span>
                    </h2>
                    <p className="text-sm text-slate-400">{formatDate(selected.scan_date)}</p>
                  </div>
                  <span className={`text-sm font-bold px-3 py-1 rounded-full border ${
                    selected.risk_level === 'Secure'      ? 'text-green-400 border-green-800 bg-green-900/20' :
                    selected.risk_level === 'Moderate'    ? 'text-yellow-400 border-yellow-800 bg-yellow-900/20' :
                    selected.risk_level === 'High Risk'   ? 'text-orange-400 border-orange-800 bg-orange-900/20' :
                    'text-red-400 border-red-800 bg-red-900/20'
                  }`}>
                    {selected.risk_level}
                  </span>
                </div>
                <div className="grid grid-cols-4 gap-3">
                  {[
                    { label: 'Total',    value: selected.total_issues,    color: 'text-white' },
                    { label: 'Critical', value: selected.critical_count,  color: 'text-red-400' },
                    { label: 'High',     value: selected.high_count,      color: 'text-orange-400' },
                    { label: 'Med/Low',  value: `${selected.medium_count}/${selected.low_count}`, color: 'text-yellow-400' },
                  ].map(({ label, value, color }) => (
                    <div key={label} className="bg-slate-700/50 rounded-lg p-3 text-center">
                      <p className={`text-xl font-bold ${color}`}>{value}</p>
                      <p className="text-xs text-slate-400 mt-0.5">{label}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Findings */}
              <div className="card">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-semibold text-slate-300">
                    Findings ({filteredFindings.length})
                  </h3>
                  <div className="flex gap-1">
                    {['All', 'Critical', 'High', 'Medium', 'Low'].map(s => (
                      <button
                        key={s}
                        onClick={() => setFilter(s)}
                        className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                          filter === s ? 'bg-blue-600 text-white' : 'bg-slate-700 text-slate-400 hover:bg-slate-600'
                        }`}
                      >
                        {s}
                      </button>
                    ))}
                  </div>
                </div>
                <div className="space-y-2 max-h-[500px] overflow-y-auto pr-1">
                  {filteredFindings.length === 0 ? (
                    <p className="text-center text-slate-500 py-8">No findings for this filter</p>
                  ) : (
                    filteredFindings.map((f, i) => <FindingRow key={f.id || i} finding={f} />)
                  )}
                </div>
              </div>
            </motion.div>
          ) : (
            <div className="card flex flex-col items-center justify-center h-64 text-slate-500">
              <ScanLine size={40} className="mb-3" />
              <p>Select a scan from the history to view details</p>
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}
