export default function EmptyState({
  icon,
  title   = 'No data yet',
  message = 'Data will appear here after your first data collection.',
}) {
  return (
    <div className="empty-state">
      {icon && <div className="empty-state__icon">{icon}</div>}
      <p className="empty-state__title">{title}</p>
      <p className="empty-state__message">{message}</p>
    </div>
  )
}
