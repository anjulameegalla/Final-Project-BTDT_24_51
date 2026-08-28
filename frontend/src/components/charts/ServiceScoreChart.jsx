import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis,
  PolarRadiusAxis, ResponsiveContainer, Tooltip
} from 'recharts'

export default function ServiceScoreChart({ serviceScores = {} }) {
  const data = [
    { service: 'IAM',        score: serviceScores.iam        ?? 100 },
    { service: 'S3',         score: serviceScores.s3         ?? 100 },
    { service: 'EC2',        score: serviceScores.ec2        ?? 100 },
    { service: 'CloudTrail', score: serviceScores.cloudtrail ?? 100 },
  ]

  return (
    <ResponsiveContainer width="100%" height={240}>
      <RadarChart data={data}>
        <PolarGrid stroke="#334155" />
        <PolarAngleAxis dataKey="service" tick={{ fill: '#94a3b8', fontSize: 12 }} />
        <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 10 }} />
        <Radar
          name="Score"
          dataKey="score"
          stroke="#3b82f6"
          fill="#3b82f6"
          fillOpacity={0.25}
          strokeWidth={2}
        />
        <Tooltip
          contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8 }}
          labelStyle={{ color: '#f1f5f9' }}
          itemStyle={{ color: '#3b82f6' }}
        />
      </RadarChart>
    </ResponsiveContainer>
  )
}
