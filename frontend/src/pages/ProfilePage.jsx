import { useState } from 'react'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { User, Mail, Shield, Calendar, Key } from 'lucide-react'
import Layout from '../components/common/Layout'
import { useAuth } from '../context/AuthContext'
import { formatDate } from '../utils/helpers'

export default function ProfilePage() {
  const { user, updateUser } = useAuth()
  const [form, setForm]     = useState({ name: user?.name || '', email: user?.email || '' })
  const [pwForm, setPwForm] = useState({ current: '', newPw: '', confirm: '' })
  const [saving, setSaving] = useState(false)

  const handleProfileSave = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      await updateUser(form)
      toast.success('Profile updated successfully!')
    } catch {
      toast.error('Failed to update profile')
    } finally {
      setSaving(false)
    }
  }

  return (
    <Layout>
      <div className="max-w-2xl mx-auto">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-white">Profile Settings</h1>
          <p className="text-slate-400 text-sm mt-1">Manage your account information.</p>
        </div>

        {/* Avatar card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card mb-6 flex items-center gap-5"
        >
          <div className="w-16 h-16 bg-blue-600 rounded-2xl flex items-center justify-center text-2xl font-bold text-white flex-shrink-0">
            {user?.name?.[0]?.toUpperCase()}
          </div>
          <div>
            <h2 className="text-lg font-bold text-white">{user?.name}</h2>
            <p className="text-slate-400 text-sm">{user?.email}</p>
            <div className="flex items-center gap-2 mt-1">
              <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${
                user?.role === 'admin'
                  ? 'bg-purple-900/40 text-purple-400 border border-purple-800'
                  : 'bg-slate-700 text-slate-400'
              }`}>
                {user?.role}
              </span>
              <span className="text-xs text-slate-500">
                Joined {formatDate(user?.created_at)}
              </span>
            </div>
          </div>
        </motion.div>

        {/* Profile form */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card mb-6"
        >
          <h2 className="text-sm font-semibold text-slate-300 mb-4 flex items-center gap-2">
            <User size={16} /> Personal Information
          </h2>
          <form onSubmit={handleProfileSave} className="space-y-4">
            <div>
              <label className="label">Full Name</label>
              <input
                type="text"
                className="input"
                value={form.name}
                onChange={e => setForm({ ...form, name: e.target.value })}
              />
            </div>
            <div>
              <label className="label">Email Address</label>
              <input
                type="email"
                className="input"
                value={form.email}
                onChange={e => setForm({ ...form, email: e.target.value })}
              />
            </div>
            <button type="submit" disabled={saving} className="btn-primary">
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
          </form>
        </motion.div>

        {/* Account info */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card"
        >
          <h2 className="text-sm font-semibold text-slate-300 mb-4 flex items-center gap-2">
            <Shield size={16} /> Account Details
          </h2>
          <div className="space-y-3 text-sm">
            {[
              { icon: User,     label: 'Account ID',  value: user?.id?.slice(-12) || 'N/A' },
              { icon: Shield,   label: 'Role',        value: user?.role || 'user' },
              { icon: Calendar, label: 'Member Since', value: formatDate(user?.created_at) },
            ].map(({ icon: Icon, label, value }) => (
              <div key={label} className="flex items-center justify-between py-2 border-b border-slate-700 last:border-0">
                <div className="flex items-center gap-2 text-slate-400">
                  <Icon size={14} /> {label}
                </div>
                <span className="text-slate-200 font-mono text-xs">{value}</span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </Layout>
  )
}
