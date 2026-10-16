export default function StatCards({ stats }) {
  const cards = [
    { label: "Today's Visits", value: stats.today, hint: 'Excludes cancellations', tone: 'teal', icon: '⏱' },
    { label: 'Upcoming', value: stats.scheduled, hint: 'Scheduled & confirmed', tone: 'blue', icon: '📅' },
    { label: 'In-Clinic Now', value: stats.checkedIn, hint: 'Checked in & waiting', tone: 'amber', icon: '🏥' },
    { label: 'Completed', value: stats.completed, hint: `${stats.total} total recorded`, tone: 'green', icon: '✓' },
    { label: 'Teleconsultations', value: stats.teleconsult ?? 0, hint: 'Remote video sessions', tone: 'cyan', icon: '💻' },
    { label: 'Cancelled / No-show', value: (stats.cancelled ?? 0) + (stats.noShow ?? 0), hint: 'Released slots', tone: 'red', icon: '✕' },
  ];

  return (
    <section className="stats" aria-label="Clinical Metrics Overview">
      {cards.map((card) => (
        <div className="stat" key={card.label}>
          <div className={`stat-icon tone-${card.tone}`} aria-hidden>
            {card.icon}
          </div>
          <div>
            <small>{card.label}</small>
            <strong>{card.value}</strong>
            <span>{card.hint}</span>
          </div>
        </div>
      ))}
    </section>
  );
}
