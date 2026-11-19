interface FilterChipProps {
  label: string
  selected?: boolean
  onToggle?: () => void
  onRemove?: () => void
  removeLabel?: string
}

export function FilterChip({
  label,
  selected = false,
  onToggle,
  onRemove,
  removeLabel,
}: FilterChipProps) {
  if (onRemove) {
    return (
      <button
        type="button"
        className="chip"
        aria-label={`Remove filter ${removeLabel ?? label}`}
        onClick={onRemove}
      >
        <span>{label}</span>
        <span aria-hidden="true">✕</span>
      </button>
    )
  }

  return (
    <button
      type="button"
      className="chip"
      aria-pressed={selected}
      onClick={onToggle}
    >
      {label}
    </button>
  )
}
