import { formatTime, isSameDay } from '../lib/appointments.js';
import { StatusBadge, TypeBadge } from './AppointmentTable.jsx';

export default function TodayPanel({ appointments }) {
  const now = new Date();
  const today = appointments
    .filter((a) => isSameDay(new Date(a.scheduled_at), now) && a.status !== 'CANCELLED')
    .sort((a, b) => a.scheduled_at.localeCompare(b.scheduled_at));

  return (
    <div className="panel today-panel">
      <div className="panel-head">
        <div>
          <h2>Today's Patient Queue</h2>
          <p className="muted">
            {now.toLocaleDateString([], { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}
          </p>
        </div>
      </div>
      {today.length === 0 ? (
        <div className="empty small">No appointments scheduled for today yet.</div>
      ) : (
        <ol className="timeline">
          {today.map((a) => (
            <li key={a.id}>
              <time>{formatTime(a.scheduled_at)}</time>
              <div className="timeline-info">
                <b>{a.patient_name}</b>
                <small>{a.doctor_name} · {a.department}</small>
              </div>
              <div className="timeline-badges">
                <TypeBadge type={a.appointment_type} />
                <StatusBadge status={a.status} />
              </div>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
