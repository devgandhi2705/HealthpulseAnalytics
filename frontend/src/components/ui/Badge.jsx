import { SOURCE_COLORS, SOURCE_MUTED } from '../../constants/colors'

export function SourceBadge({ source }) {
  const color = SOURCE_COLORS[source] ?? '#1E40AF'
  const bg    = SOURCE_MUTED[source]  ?? '#DBEAFE'
  return (
    <span
      className="badge"
      style={{ '--badge-bg': bg, '--badge-color': color }}
    >
      {source}
    </span>
  )
}

export function CategoryBadge({ category }) {
  return <span className="badge badge--category">{category}</span>
}
