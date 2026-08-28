import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import {
  AlertTriangle, ShieldCheck, ScanLine, TrendingUp,
  RefreshCw, Download, Play
} from 'lucide-react'

import Layout from '../components/common/Layout'
import LoadingSpinner from '../components/common/LoadingSpinner'
import StatCard from '../components/common/StatCard'
import ScoreGauge from '../components/dashboard/ScoreGauge'
import ServiceCard from '../components/dashboard/ServiceCard'
import SeverityPieChart from '../components/charts/SeverityPieChart'
import ScoreHistoryChart from '../components/charts/ScoreHistoryChart'
import ServiceScoreChart from '../components/charts/ServiceScoreChart'
import FindingRow from '../components/dashboard/FindingRow'
import { scanService, awsService, reportService } from '../services/scanService'
import { formatDate, timeAgo } from '../utils/helpers'

export default function DashboardPage() {
  const navigate = useNavigate()

  const [latestScan, setLatestScan]   = useState(null)
  const [history, setHistory]         = useState([])
  const [awsAccount, setAwsAccount]   = useState(null)
  const [loading, setLoading]         = useState(true)
  const [scanning, setScanning]       = useState(false)
  const [generating, setGenerating]   = useState(false)
  const [filter, setFilter]           = useState('All')
  const [serviceFilter, setServiceFilter] = useState('All')

  useEffect(() => { fetchData() }, [])

  const fetchData = async () => {
    setLoading(true)
    try {
      const [scanRes, histRes, awsRes] = await Promise.allSettled([
        scanService.getLatest(),
        scanService.getHistory(10),
        awsService.getStatus(),
      ])
      if (scanRes.status === 'fulfilled') setLatestScan(scanRes.value.data)
      if (histRes.status === 'fulfilled') setHistory(histRes.value.data.scans || [])
      if (awsRes.status === 'fulfilled') setAwsAccount(awsRes.value.data)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleStartScan = async () => {
    if (!awsAccount) {
      toast.error('Connect an AWS account first')
      navigate('/connect')
      return
    }
    setScanning(true)
    try {
      const accountId = awsAccount.account_id
      if (!accountId) {
        throw new Error('AWS account ID is missing. Please reconnect your account.')
      }
      const scanRes = await scanService.startScan(accountId, ['iam', 's3', 'ec2', 'cloudtrail'])
      toast.success('Scan started! Results will appear shortly.')

      // Poll for completion
      const scanId = scanRes.data.scan_id
      let attempts = 0
      const poll = setInterval(async () => {
        attempts++
        try {
          const res = await scanService.getScan(scanId)
          if (res.data.status === 'completed' || res.data.status === 'failed') {
            clearInterval(poll)
            setScanning(false)
            if (res.data.status === 'completed') {
              setLatestScan(res.data)
              toast.success('Scan completed!')
              fetchData()
            } else {
              toast.error(res.data.error || 'Scan failed')
            }
          }
        } catch {}
        if (attempts > 30) { clearInterval(poll); setScanning(false) }
      }, 3000)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to start scan')
      setScanning(false)
    }
  }

  const handleGenerateReport = async () => {
    if (!latestScan) return
    setGenerating(true)
    try {
      const res = await reportService.generate(latestScan.id)
      toast.success('Report generated!')
      const report = await reportService.download(res.data.report_id)
      const url = URL.createObjectURL(report.data)
      const link = document.createElement('a')
      link.href = url
      link.download = res.data.file_name || 'cloudguard_report.pdf'
      link.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to generate report')
    } finally {
      setGenerating(false)
    }
  }

  // Filter findings
  const allFindings = latestScan?.findings || []
  const filteredFindings = allFindings.filter(f => {
    const sevMatch = filter === 'All' || f.severity === filter
    const svcMatch = serviceFilter === 'All' || f.service?.toLowerCase() === serviceFilter.toLowerCase()
    return sevMatch && svcMatch
  })

  const severityData = {
    Critical: latestScan?.critical_count || 0,
    High:     latestScan?.high_count     || 0,
    Medium:   latestScan?.medium_count   || 0,
    Low:      latestScan?.low_count      || 0,
  }

  // Count issues per service
  const serviceIssueCounts = allFindings.reduce((acc, f) => {
    acc[f.service] = (acc[f.service] || 0) + 1
    return acc
  }, {})

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner size="lg" text="Loading dashboard..." />
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white">Security Dashboard</h1>
          <p className="text-slate-400 text-sm mt-1">
            {latestScan
              ? `Last scan: ${timeAgo(latestScan.scan_date)}`
              : 'No scans yet — run your first scan'}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={fetchData} className="btn-secondary">
            <RefreshCw size={16} /> Refresh
          </button>
          {latestScan && (
            <button onClick={handleGenerateReport} disabled={generating} className="btn-secondary">
              <Download size={16} />
              {generating ? 'Generating...' : 'Download Report'}
            </button>
          )}
          <button onClick={handleStartScan} disabled={scanning} className="btn-primary">
            {scanning ? (
              <><span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Scanning...</>
            ) : (
              <><Play size={16} /> Start Scan</>
            )}
          </button>
        </div>
      </div>

      {/* No scan state */}
      {!latestScan && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="card text-center py-16"
        >
          <ScanLine size={48} className="text-slate-600 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-white mb-2">No Scans Yet</h3>
          <p className="text-slate-400 mb-6">Connect your AWS account and run your first security scan.</p>
          <button onClick={() => navigate('/connect')} className="btn-primary mx-auto">
            Connect AWS Account
          </button>
        </motion.div>
      )}

      {latestScan && (
        <>
          {/* Score + Stats row */}
          <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 mb-6">
            {/* Score gauge */}
            <div className="card flex flex-col items-center justify-center lg:col-span-1">
              <p className="text-sm font-semibold text-slate-400 mb-4">Security Score</p>
              <ScoreGauge score={latestScan.overall_score} riskLevel={latestScan.risk_level} />
            </div>

            {/* Stat cards */}
            <div className="lg:col-span-4 grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard title="Total Issues"    value={latestScan.total_issues}    icon={AlertTriangle} color="blue" />
              <StatCard title="Critical"        value={latestScan.critical_count}  icon={AlertTriangle} color="red" />
              <StatCard title="High"            value={latestScan.high_count}      icon={AlertTriangle} color="orange" />
              <StatCard title="Medium / Low"    value={`${latestScan.medium_count} / ${latestScan.low_count}`} icon={ShieldCheck} color="yellow" />
            </div>
          </div>

          {/* Charts row */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="card">
              <h3 className="text-sm font-semibold text-slate-300 mb-4">Severity Distribution</h3>
              <SeverityPieChart data={severityData} />
            </div>
            <div className="card">
              <h3 className="text-sm font-semibold text-slate-300 mb-4">Service Security Radar</h3>
              <ServiceScoreChart serviceScores={latestScan.service_scores} />
            </div>
            <div className="card">
              <h3 className="text-sm font-semibold text-slate-300 mb-4">Score History</h3>
              <ScoreHistoryChart scans={history} />
            </div>
          </div>

          {/* Service cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            {['iam', 's3', 'ec2', 'cloudtrail'].map(svc => (
              <ServiceCard
                key={svc}
                service={svc}
                score={latestScan.service_scores?.[svc] ?? 100}
                issueCount={serviceIssueCounts[svc] || 0}
              />
            ))}
          </div>

          {/* Findings */}
          <div className="card">
            <div className="flex items-center justify-between mb-4 flex-wrap gap-3">
              <h3 className="text-sm font-semibold text-slate-300">
                Security Findings ({filteredFindings.length})
              </h3>
              <div className="flex items-center gap-2 flex-wrap">
                {/* Severity filter */}
                <div className="flex gap-1">
                  {['All', 'Critical', 'High', 'Medium', 'Low'].map(s => (
                    <button
                      key={s}
                      onClick={() => setFilter(s)}
                      className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${
                        filter === s
                          ? 'bg-blue-600 text-white'
                          : 'bg-slate-700 text-slate-400 hover:bg-slate-600'
                      }`}
                    >
                      {s}
                    </button>
                  ))}
                </div>
                {/* Service filter */}
                <div className="flex gap-1">
                  {['All', 'iam', 's3', 'ec2', 'cloudtrail'].map(s => (
                    <button
                      key={s}
                      onClick={() => setServiceFilter(s)}
                      className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${
                        serviceFilter === s
                          ? 'bg-slate-500 text-white'
                          : 'bg-slate-700 text-slate-400 hover:bg-slate-600'
                      }`}
                    >
                      {s.toUpperCase()}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {filteredFindings.length === 0 ? (
              <div className="text-center py-10 text-slate-500">
                <ShieldCheck size={32} className="mx-auto mb-2 text-green-500" />
                <p>No findings match the selected filters</p>
              </div>
            ) : (
              <div className="space-y-2">
                {filteredFindings.map((finding, i) => (
                  <FindingRow key={finding.id || i} finding={finding} />
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </Layout>
  )
}
