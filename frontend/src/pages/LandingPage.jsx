import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Shield, Zap, BarChart3, Bell, FileText,
  Cloud, Lock, Eye, ChevronRight, CheckCircle
} from 'lucide-react'

const features = [
  { icon: Shield,    title: 'Multi-Service Scanning',   desc: 'Scan IAM, S3, EC2, and CloudTrail for misconfigurations and threats.' },
  { icon: Zap,       title: 'AI-Powered Explanations',  desc: 'Get plain-English explanations and step-by-step fix recommendations.' },
  { icon: BarChart3, title: 'Security Score Dashboard', desc: 'Real-time security score with service-wise breakdown and trend charts.' },
  { icon: Bell,      title: 'Instant Alerts',           desc: 'Email alerts for critical findings via AWS SES.' },
  { icon: FileText,  title: 'PDF Audit Reports',        desc: 'Professional PDF reports ready for compliance and management review.' },
  { icon: Lock,      title: 'Role-Based Access',        desc: 'Admin and user roles with JWT authentication and protected routes.' },
]

const checks = [
  'IAM users without MFA',
  'Public S3 buckets',
  'SSH/RDP open to internet',
  'Root account usage',
  'Old & unused access keys',
  'Failed login attempts',
  'Overly permissive policies',
  'CloudTrail anomalies',
]

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      {/* Navbar */}
      <nav className="border-b border-slate-800 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-blue-600 rounded-lg flex items-center justify-center">
              <Shield size={20} className="text-white" />
            </div>
            <span className="font-bold text-white text-lg">CloudGuard AI</span>
          </div>
          <div className="flex items-center gap-3">
            <Link to="/login" className="btn-secondary text-sm">Sign In</Link>
            <Link to="/register" className="btn-primary text-sm">Get Started</Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-6xl mx-auto px-6 py-24 text-center">
        <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
          <span className="inline-flex items-center gap-2 bg-blue-900/40 border border-blue-700/50 text-blue-400 text-xs font-semibold px-3 py-1.5 rounded-full mb-6">
            <Zap size={12} /> AI-Powered Cloud Security
          </span>
          <h1 className="text-5xl md:text-6xl font-extrabold text-white leading-tight mb-6">
            Secure Your AWS<br />
            <span className="text-blue-400">Cloud Infrastructure</span>
          </h1>
          <p className="text-xl text-slate-400 max-w-2xl mx-auto mb-10">
            CloudGuard AI scans your AWS environment, detects security misconfigurations,
            explains risks using AI, and provides actionable fix recommendations — all in one dashboard.
          </p>
          <div className="flex items-center justify-center gap-4 flex-wrap">
            <Link to="/register" className="btn-primary text-base px-6 py-3">
              Start Free Scan <ChevronRight size={18} />
            </Link>
            <Link to="/login" className="btn-secondary text-base px-6 py-3">
              View Demo Dashboard
            </Link>
          </div>
        </motion.div>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="grid grid-cols-3 gap-6 max-w-lg mx-auto mt-16"
        >
          {[['50+', 'Security Checks'], ['4', 'AWS Services'], ['AI', 'Powered Fixes']].map(([val, label]) => (
            <div key={label} className="text-center">
              <p className="text-3xl font-bold text-blue-400">{val}</p>
              <p className="text-sm text-slate-500 mt-1">{label}</p>
            </div>
          ))}
        </motion.div>
      </section>

      {/* What We Check */}
      <section className="bg-slate-800/50 border-y border-slate-700 py-16">
        <div className="max-w-6xl mx-auto px-6">
          <h2 className="text-2xl font-bold text-white text-center mb-10">What CloudGuard AI Detects</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {checks.map(check => (
              <div key={check} className="flex items-center gap-2 text-sm text-slate-300">
                <CheckCircle size={16} className="text-green-400 flex-shrink-0" />
                {check}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="max-w-6xl mx-auto px-6 py-20">
        <h2 className="text-3xl font-bold text-white text-center mb-4">Everything You Need</h2>
        <p className="text-slate-400 text-center mb-12">A complete cloud security platform built for developers and security teams.</p>
        <div className="grid md:grid-cols-3 gap-6">
          {features.map(({ icon: Icon, title, desc }) => (
            <motion.div
              key={title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="card hover:border-blue-700/50 transition-colors"
            >
              <div className="w-10 h-10 bg-blue-900/40 rounded-lg flex items-center justify-center mb-4">
                <Icon size={20} className="text-blue-400" />
              </div>
              <h3 className="font-semibold text-white mb-2">{title}</h3>
              <p className="text-sm text-slate-400">{desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="bg-blue-600 py-16">
        <div className="max-w-3xl mx-auto px-6 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">Ready to Secure Your Cloud?</h2>
          <p className="text-blue-100 mb-8">Connect your AWS account and get your security score in minutes.</p>
          <Link to="/register" className="inline-flex items-center gap-2 bg-white text-blue-600 font-bold px-8 py-3 rounded-lg hover:bg-blue-50 transition-colors">
            Get Started Free <ChevronRight size={18} />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-8 text-center text-slate-500 text-sm">
        <p>© 2026 CloudGuard AI — AWS Cloud Security Monitoring & Threat Detection</p>
        <p className="mt-1 text-xs">Final HND/DT Project | Built with FastAPI + React + AWS</p>
      </footer>
    </div>
  )
}
