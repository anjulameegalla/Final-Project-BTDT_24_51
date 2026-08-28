import { severityBadgeClass } from '../../utils/helpers'

export default function SeverityBadge({ severity }) {
  return (
    <span className={severityBadgeClass(severity)}>
      {severity}
    </span>
  )
}
