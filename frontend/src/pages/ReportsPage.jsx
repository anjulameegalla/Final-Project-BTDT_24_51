import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { FileText, Download, Plus, Calendar, Loader } from 'lucide-react'
import Layout from '../components/common/Layout'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { reportService, scanService } from '../services/scanService'
import { formatDate, scoreColor, riskLevelColor } from '../utils/helpers'

export default function ReportsPage() {
  const [reports, setReports]   = useState([])
  const [scans, setScans]       = useState([])
  const [loading, setLoading]   = useState(true)
  const [generating, setGenerating] = useState(null)  // scan_id being generated

  useEffect(() => { fetchData() }, [])

  const fetchData = async () => {
    setLoading(true)
    try {
      const [repRes, scanRes] = await Promise.allSettled([
        reportService.list(),
        scanService.getHistory(20),
      ])
      if (repRes.status === 'fulfilled')  setReports(repRes.value.data.reports || [])
      if (scanRes.status === 'fulfilled') setScans(scanRes.value.data.scans?.filter(s => s.status === 'completed') || [])
    } finally {
      setLoading(false)
    }
  }

  const handleGenerate = async (scanId) => {
    setGenerating(scanId)
    try {
      const res = await reportService.generate(scanId)
      toast.success('Report generated!')
      fetchData()
      // Auto-download
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
      setGenerating(null)
    }
  }

  const handleDownload = async (reportId, fileName) => {
    try {
      const report = await reportService.download(reportId)
      const url = URL.createObjectURL(report.data)
      const link = document.createElement('a')
      link.href = url
      link.download = fileName || 'cloudguard_report.pdf'
      link.click()
      URL.revokeObjectURL(url)
    } catch {
      toast.error('Failed to download report')
    }
  }

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner size="lg" text="Loading reports..." />
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white">Security Reports</h1>
        <p className="text-slate-400 text-sm mt-1">Generate and download PDF audit reports for your scans.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Generate new report */}
        <div className="card">
          <h2 className="text-sm font-semibold text-slate-300 mb-4 flex items-center gap-2">
            <Plus size={16} /> Generate New Report
          </h2>
          {scans.length === 0 ? (
            <p className="text-slate-500 text-sm">No completed scans available. Run a scan first.</p>
          ) : (
            <div className="space-y-2 max-h-80 overflow-y-auto">
              {scans.map(scan => (
                <div
                  key={scan.id}
                  className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg border border-slate-700"
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <span className={`text-sm font-bold ${scoreColor(scan.overall_score)}`}>
                        {scan.overall_score}/100
                      </span>
                      <span className={`text-xs ${riskLevelColor(scan.risk_level)}`}>
                        {scan.risk_level}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 flex items-center gap-1 mt-0.5">
                      <Calendar size={11} /> {formatDate(scan.scan_date || scan.created_at)}
                    </p>
                    <p className="text-xs text-slate-500">{scan.total_issues} issues</p>
                  </div>
                  <button
                    onClick={() => handleGenerate(scan.id)}
                    disabled={generating === scan.id}
                    className="btn-primary text-xs py-1.5"
                  >
                    {generating === scan.id ? (
                      <Loader size={13} className="animate-spin" />
                    ) : (
                      <><FileText size={13} /> Generate</>
                    )}
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Existing reports */}
        <div className="card">
          <h2 className="text-sm font-semibold text-slate-300 mb-4 flex items-center gap-2">
            <FileText size={16} /> Generated Reports ({reports.length})
          </h2>
          {reports.length === 0 ? (
            <div className="text-center py-10 text-slate-500">
              <FileText size={32} className="mx-auto mb-2" />
              <p className="text-sm">No reports generated yet</p>
            </div>
          ) : (
            <div className="space-y-2 max-h-80 overflow-y-auto">
              {reports.map(report => (
                <motion.div
                  key={report.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg border border-slate-700"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="w-8 h-8 bg-red-900/30 rounded-lg flex items-center justify-center flex-shrink-0">
                      <FileText size={16} className="text-red-400" />
                    </div>
                    <div className="min-w-0">
                      <p className="text-sm text-white truncate">{report.file_name}</p>
                      <p className="text-xs text-slate-400">{formatDate(report.created_at)}</p>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDownload(report.id, report.file_name)}
                    className="btn-secondary text-xs py-1.5 flex-shrink-0 ml-2"
                  >
                    <Download size={13} /> Download
                  </button>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Info card */}
      <div className="card mt-6">
        <h2 className="text-sm font-semibold text-slate-300 mb-3">📄 What's in the Report?</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            ['Executive Summary',    'Overall score, risk level, and key findings'],
            ['Severity Breakdown',   'Critical, High, Medium, Low issue counts'],
            ['Service-wise Scores',  'IAM, S3, EC2, CloudTrail individual scores'],
            ['AI Recommendations',   'Step-by-step fix instructions for each issue'],
          ].map(([title, desc]) => (
            <div key={title} className="bg-slate-700/50 rounded-lg p-3">
              <p className="text-xs font-semibold text-white mb-1">{title}</p>
              <p className="text-xs text-slate-400">{desc}</p>
            </div>
          ))}
        </div>
      </div>
    </Layout>
  )
}
