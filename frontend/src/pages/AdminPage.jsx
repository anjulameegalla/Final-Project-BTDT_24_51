import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { Users, ScanLine, FileText, AlertTriangle, Trash2, Shield } from 'lucide-react'
import Layout from '../components/common/Layout'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { adminService } from '../services/scanService'
import { formatDate, scoreColor, riskLevelColor } from '../utils/helpers'

export default function AdminPage() {
  const [tab, setTab]       = useState('stats')
  const [stats, setStats]   = useState(null)
  const [users, setUsers]   = useState([])
  const [scans, setScans]   = useState([])
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => { fetchAll() }, [])

  const fetchAll = async () => {
    setLoading(true)
    try {
      const [statsRes, usersRes, scansRes, reportsRes] = await Promise.allSettled([
        adminService.getStats(),
        adminService.getUsers(),
        adminService.getScans(),
        adminService.getReports(),
      ])
      if (statsRes.status === 'fulfilled')   setStats(statsRes.value.data)
      if (usersRes.status === 'fulfilled')   setUsers(usersRes.value.data.users || [])
      if (scansRes.status === 'fulfilled')   setScans(scansRes.value.data.scans || [])
      if (reportsRes.status === 'fulfilled') setReports(reportsRes.value.data.reports || [])
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteUser = async (userId, name) => {
    if (!confirm(`Delete user "${name}"? This will also delete all their scans and reports.`)) return
    try {
      await adminService.deleteUser(userId)
      toast.success('User deleted')
      fetchAll()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to delete user')
    }
  }

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner size="lg" text="Loading admin panel..." />
        </div>
      </Layout>
    )
  }

  const tabs = [
    { id: 'stats',   label: 'Overview',  icon: Shield },
    { id: 'users',   label: `Users (${users.length})`,   icon: Users },
    { id: 'scans',   label: `Scans (${scans.length})`,   icon: ScanLine },
    { id: 'reports', label: `Reports (${reports.length})`, icon: FileText },
  ]

  return (
    <Layout>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Shield size={24} className="text-blue-400" /> Admin Panel
        </h1>
        <p className="text-slate-400 text-sm mt-1">System-wide monitoring and management.</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b border-slate-700 pb-0">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setTab(id)}
            className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition-colors -mb-px ${
              tab === id
                ? 'border-blue-500 text-blue-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Icon size={15} /> {label}
          </button>
        ))}
      </div>

      {/* Stats tab */}
      {tab === 'stats' && stats && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
            {[
              { label: 'Total Users',    value: stats.total_users,    color: 'text-blue-400' },
              { label: 'Total Scans',    value: stats.total_scans,    color: 'text-purple-400' },
              { label: 'Reports',        value: stats.total_reports,  color: 'text-green-400' },
              { label: 'Alerts Sent',    value: stats.total_alerts,   color: 'text-yellow-400' },
              { label: 'Critical Scans', value: stats.critical_scans, color: 'text-red-400' },
            ].map(({ label, value, color }) => (
              <div key={label} className="card text-center">
                <p className={`text-3xl font-bold ${color}`}>{value}</p>
                <p className="text-xs text-slate-400 mt-1">{label}</p>
              </div>
            ))}
          </div>
          <div className="card">
            <h3 className="text-sm font-semibold text-slate-300 mb-3">System Health</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between py-2 border-b border-slate-700">
                <span className="text-slate-400">API Status</span>
                <span className="text-green-400 font-medium">● Healthy</span>
              </div>
              <div className="flex justify-between py-2 border-b border-slate-700">
                <span className="text-slate-400">Database</span>
                <span className="text-green-400 font-medium">● Connected</span>
              </div>
              <div className="flex justify-between py-2 border-b border-slate-700">
                <span className="text-slate-400">Demo Mode</span>
                <span className="text-yellow-400 font-medium">● Active</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-slate-400">AI Service</span>
                <span className="text-green-400 font-medium">● Available (Fallback)</span>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Users tab */}
      {tab === 'users' && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="card p-0 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-700/50 text-slate-400 text-xs uppercase tracking-wider">
                <th className="text-left px-4 py-3">Name</th>
                <th className="text-left px-4 py-3">Email</th>
                <th className="text-left px-4 py-3">Role</th>
                <th className="text-left px-4 py-3">Joined</th>
                <th className="text-left px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700">
              {users.map(user => (
                <tr key={user.id} className="hover:bg-slate-700/30 transition-colors">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-7 h-7 bg-blue-600 rounded-full flex items-center justify-center text-xs font-bold text-white">
                        {user.name?.[0]?.toUpperCase()}
                      </div>
                      <span className="text-white font-medium">{user.name}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-slate-400">{user.email}</td>
                  <td className="px-4 py-3">
                    <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
                      user.role === 'admin'
                        ? 'bg-purple-900/40 text-purple-400 border border-purple-800'
                        : 'bg-slate-700 text-slate-400'
                    }`}>
                      {user.role}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-400 text-xs">{formatDate(user.created_at)}</td>
                  <td className="px-4 py-3">
                    {user.role !== 'admin' && (
                      <button
                        onClick={() => handleDeleteUser(user.id, user.name)}
                        className="p-1.5 text-slate-500 hover:text-red-400 hover:bg-red-900/20 rounded transition-colors"
                      >
                        <Trash2 size={14} />
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </motion.div>
      )}

      {/* Scans tab */}
      {tab === 'scans' && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="card p-0 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-700/50 text-slate-400 text-xs uppercase tracking-wider">
                <th className="text-left px-4 py-3">Scan ID</th>
                <th className="text-left px-4 py-3">Score</th>
                <th className="text-left px-4 py-3">Risk Level</th>
                <th className="text-left px-4 py-3">Issues</th>
                <th className="text-left px-4 py-3">Status</th>
                <th className="text-left px-4 py-3">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700">
              {scans.map(scan => (
                <tr key={scan.id} className="hover:bg-slate-700/30 transition-colors">
                  <td className="px-4 py-3 font-mono text-xs text-slate-400">{scan.id?.slice(-8)}</td>
                  <td className="px-4 py-3">
                    <span className={`font-bold ${scoreColor(scan.overall_score)}`}>
                      {scan.overall_score}/100
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`text-xs font-medium ${riskLevelColor(scan.risk_level)}`}>
                      {scan.risk_level}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-300">{scan.total_issues}</td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                      scan.status === 'completed' ? 'bg-green-900/40 text-green-400' :
                      scan.status === 'running'   ? 'bg-blue-900/40 text-blue-400' :
                      'bg-red-900/40 text-red-400'
                    }`}>
                      {scan.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-400 text-xs">{formatDate(scan.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </motion.div>
      )}

      {/* Reports tab */}
      {tab === 'reports' && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="card p-0 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-700/50 text-slate-400 text-xs uppercase tracking-wider">
                <th className="text-left px-4 py-3">File Name</th>
                <th className="text-left px-4 py-3">Scan ID</th>
                <th className="text-left px-4 py-3">S3 URL</th>
                <th className="text-left px-4 py-3">Generated</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700">
              {reports.map(report => (
                <tr key={report.id} className="hover:bg-slate-700/30 transition-colors">
                  <td className="px-4 py-3 text-white text-xs font-mono">{report.file_name}</td>
                  <td className="px-4 py-3 text-slate-400 text-xs font-mono">{report.scan_id?.slice(-8)}</td>
                  <td className="px-4 py-3 text-xs">
                    {report.s3_url
                      ? <a href={report.s3_url} target="_blank" rel="noreferrer" className="text-blue-400 hover:underline">S3 Link</a>
                      : <span className="text-slate-500">Local only</span>
                    }
                  </td>
                  <td className="px-4 py-3 text-slate-400 text-xs">{formatDate(report.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </motion.div>
      )}
    </Layout>
  )
}
