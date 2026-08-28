import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import toast from 'react-hot-toast'
import { Cloud, CheckCircle, AlertCircle, Info, Copy, ExternalLink } from 'lucide-react'
import Layout from '../components/common/Layout'
import { awsService } from '../services/scanService'

const SAMPLE_POLICY = `{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "CloudGuardReadOnly",
      "Effect": "Allow",
      "Action": [
        "iam:List*", "iam:Get*",
        "s3:ListAllMyBuckets", "s3:GetBucket*", "s3:GetEncryptionConfiguration",
        "ec2:DescribeSecurityGroups", "ec2:DescribeInstances",
        "cloudtrail:LookupEvents", "cloudtrail:GetTrailStatus",
        "sts:GetCallerIdentity"
      ],
      "Resource": "*"
    }
  ]
}`

export default function ConnectAWSPage() {
  const navigate = useNavigate()
  const [mode, setMode]       = useState('demo')   // 'demo' | 'role' | 'keys'
  const [status, setStatus]   = useState(null)
  const [loading, setLoading] = useState(false)
  const [copied, setCopied]   = useState(false)

  const [form, setForm] = useState({
    account_name: '',
    region: 'us-east-1',
    role_arn: '',
    access_key_id: '',
    secret_access_key: '',
  })

  useEffect(() => {
    awsService.getStatus()
      .then(res => setStatus(res.data))
      .catch(() => {})
  }, [])

  const handleConnect = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const payload = {
        account_name: form.account_name || 'Demo Account',
        region: form.region,
        use_demo: mode === 'demo',
        role_arn: mode === 'role' ? form.role_arn : undefined,
        access_key_id: mode === 'keys' ? form.access_key_id : undefined,
        secret_access_key: mode === 'keys' ? form.secret_access_key : undefined,
      }
      const res = await awsService.connect(payload)
      toast.success('AWS account connected successfully!')
      setStatus({ connection_status: 'connected', is_demo: mode === 'demo', account_name: payload.account_name, region: payload.region })
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Connection failed')
    } finally {
      setLoading(false)
    }
  }

  const copyPolicy = () => {
    navigator.clipboard.writeText(SAMPLE_POLICY)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
    toast.success('Policy copied to clipboard')
  }

  const regions = [
    'us-east-1','us-east-2','us-west-1','us-west-2',
    'eu-west-1','eu-west-2','eu-central-1',
    'ap-south-1','ap-southeast-1','ap-southeast-2','ap-northeast-1',
  ]

  return (
    <Layout>
      <div className="max-w-3xl mx-auto">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-white">Connect AWS Account</h1>
          <p className="text-slate-400 text-sm mt-1">
            Link your AWS account to start scanning for security issues.
          </p>
        </div>

        {/* Current status */}
        {status && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`flex items-center gap-3 p-4 rounded-lg border mb-6 ${
              status.connection_status === 'connected'
                ? 'bg-green-900/20 border-green-800/40'
                : 'bg-red-900/20 border-red-800/40'
            }`}
          >
            {status.connection_status === 'connected'
              ? <CheckCircle size={18} className="text-green-400" />
              : <AlertCircle size={18} className="text-red-400" />
            }
            <div>
              <p className="text-sm font-medium text-white">
                {status.connection_status === 'connected' ? 'Account Connected' : 'Connection Failed'}
              </p>
              <p className="text-xs text-slate-400">
                {status.account_name} · {status.region}
                {status.is_demo && ' · Demo Mode'}
              </p>
            </div>
            {status.connection_status === 'connected' && (
              <button
                onClick={() => navigate('/dashboard')}
                className="ml-auto btn-primary text-sm"
              >
                Go to Dashboard
              </button>
            )}
          </motion.div>
        )}

        {/* Mode selector */}
        <div className="card mb-6">
          <h2 className="text-sm font-semibold text-slate-300 mb-4">Connection Method</h2>
          <div className="grid grid-cols-3 gap-3">
            {[
              { id: 'demo', label: '🎯 Demo Mode',    desc: 'Use sample data — no AWS needed' },
              { id: 'role', label: '🔐 IAM Role ARN', desc: 'Recommended for production' },
              { id: 'keys', label: '🔑 Access Keys',  desc: 'Direct key authentication' },
            ].map(opt => (
              <button
                key={opt.id}
                onClick={() => setMode(opt.id)}
                className={`p-3 rounded-lg border text-left transition-all ${
                  mode === opt.id
                    ? 'border-blue-500 bg-blue-900/20'
                    : 'border-slate-700 hover:border-slate-500'
                }`}
              >
                <p className="text-sm font-medium text-white">{opt.label}</p>
                <p className="text-xs text-slate-400 mt-0.5">{opt.desc}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Connection form */}
        <div className="card mb-6">
          <form onSubmit={handleConnect} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="label">Account Name</label>
                <input
                  type="text"
                  className="input"
                  placeholder="My AWS Account"
                  value={form.account_name}
                  onChange={e => setForm({ ...form, account_name: e.target.value })}
                />
              </div>
              <div>
                <label className="label">AWS Region</label>
                <select
                  className="input"
                  value={form.region}
                  onChange={e => setForm({ ...form, region: e.target.value })}
                >
                  {regions.map(r => <option key={r} value={r}>{r}</option>)}
                </select>
              </div>
            </div>

            {mode === 'role' && (
              <div>
                <label className="label">IAM Role ARN</label>
                <input
                  type="text"
                  className="input font-mono text-sm"
                  placeholder="arn:aws:iam::123456789012:role/CloudGuardReadOnly"
                  value={form.role_arn}
                  onChange={e => setForm({ ...form, role_arn: e.target.value })}
                  required
                />
                <p className="text-xs text-slate-500 mt-1">
                  Create an IAM role with the policy below and paste the ARN here.
                </p>
              </div>
            )}

            {mode === 'keys' && (
              <>
                <div>
                  <label className="label">Access Key ID</label>
                  <input
                    type="text"
                    className="input font-mono text-sm"
                    placeholder="AKIAIOSFODNN7EXAMPLE"
                    value={form.access_key_id}
                    onChange={e => setForm({ ...form, access_key_id: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label className="label">Secret Access Key</label>
                  <input
                    type="password"
                    className="input font-mono text-sm"
                    placeholder="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
                    value={form.secret_access_key}
                    onChange={e => setForm({ ...form, secret_access_key: e.target.value })}
                    required
                  />
                </div>
                <div className="flex items-start gap-2 p-3 bg-yellow-900/20 border border-yellow-800/40 rounded-lg">
                  <Info size={16} className="text-yellow-400 flex-shrink-0 mt-0.5" />
                  <p className="text-xs text-yellow-300">
                    Use IAM Role ARN in production. Access keys are stored only for the session and never persisted in plaintext.
                  </p>
                </div>
              </>
            )}

            {mode === 'demo' && (
              <div className="flex items-start gap-2 p-3 bg-blue-900/20 border border-blue-800/40 rounded-lg">
                <Info size={16} className="text-blue-400 flex-shrink-0 mt-0.5" />
                <p className="text-xs text-blue-300">
                  Demo mode uses realistic sample AWS findings. No real AWS account required.
                  Perfect for testing and demonstration purposes.
                </p>
              </div>
            )}

            <button type="submit" disabled={loading} className="btn-primary w-full justify-center py-2.5">
              {loading ? (
                <span className="flex items-center gap-2">
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Connecting...
                </span>
              ) : (
                <><Cloud size={16} /> Connect AWS Account</>
              )}
            </button>
          </form>
        </div>

        {/* Required IAM Policy */}
        <div className="card">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold text-slate-300">Required IAM Policy</h2>
            <button onClick={copyPolicy} className="btn-secondary text-xs py-1.5">
              <Copy size={13} />
              {copied ? 'Copied!' : 'Copy Policy'}
            </button>
          </div>
          <p className="text-xs text-slate-400 mb-3">
            Attach this read-only policy to the IAM role or user used for scanning.
          </p>
          <pre className="bg-slate-900 border border-slate-700 rounded-lg p-4 text-xs text-green-400 overflow-x-auto">
            {SAMPLE_POLICY}
          </pre>
        </div>
      </div>
    </Layout>
  )
}
