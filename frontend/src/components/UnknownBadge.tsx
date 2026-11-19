interface UnknownBadgeProps {
  label?: string
  title?: string
}

export function UnknownBadge({
  label = 'Not specified',
  title = "The official source doesn't say",
}: UnknownBadgeProps) {
  return (
    <span className="status-unknown" title={title}>
      {label}
    </span>
  )
}
