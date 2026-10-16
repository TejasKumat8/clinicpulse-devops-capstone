import { useState } from 'react';
import {
  DEPARTMENTS,
  STATUS_META,
  TYPE_META,
  formatDay,
  formatTime,
  nextActions,
  titleCase,
} from '../lib/appointments.js';

const STATUS_FILTERS = ['ALL', 'SCHEDULED', 'CHECKED_IN', 'COMPLETED', 'CANCELLED', 'NO_SHOW'];
const TYPE_FILTERS = ['ALL', 'IN_PERSON', 'TELECONSULT'];

export function StatusBadge({ status }) {
  const meta = STATUS_META[status] ?? { label: status, tone: 'grey' };
  return <span className={`badge tone-${meta.tone}`}>{meta.label}</span>;
}

export function TypeBadge({ type }) {
  const meta = TYPE_META[type] ?? { label: type || 'In-Person', tone: 'emerald' };
  return <span className={`badge-pill tone-${meta.tone}`}>{meta.label}</span>;
}

export default function AppointmentTable({
  loading,
  appointments,
  totalCount,
  filters,
  onFiltersChange,
  onStatusChange,
  onEdit,
  onDelete,
}) {
  const [confirmingId, setConfirmingId] = useState(null);
  const set = (patch) => onFiltersChange({ ...filters, ...patch });

  return (
    <div className="panel appointment-panel">
      <div className="panel-head wrap">
        <div>
          <h2>Clinical Appointment Directory</h2>
          <p className="muted">
            Displaying {appointments.length} of {totalCount} total visits
          </p>
        </div>
        <div className="toolbar">
          <input
            type="search"
            className="search"
            placeholder="Search patient, phone, doctor…"
            value={filters.query}
            onChange={(e) => set({ query: e.target.value })}
            aria-label="Search appointments"
          />
          <select
            value={filters.department}
            onChange={(e) => set({ department: e.target.value })}
            aria-label="Department Filter"
          >
            <option value="ALL">All Departments</option>
            {DEPARTMENTS.map((d) => (
              <option key={d} value={d}>
                {titleCase(d)}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="filter-bars">
        <div className="chips" role="tablist" aria-label="Filter by status">
          <span className="filter-label">Status:</span>
          {STATUS_FILTERS.map((s) => (
            <button
              key={s}
              role="tab"
              aria-selected={filters.status === s}
              className={`chip ${filters.status === s ? 'selected' : ''}`}
              onClick={() => set({ status: s })}
            >
              {s === 'ALL' ? 'All' : STATUS_META[s].label}
            </button>
          ))}
        </div>

        <div className="chips type-chips" role="tablist" aria-label="Filter by consultation type">
          <span className="filter-label">Mode:</span>
          {TYPE_FILTERS.map((t) => (
            <button
              key={t}
              role="tab"
              aria-selected={filters.type === t}
              className={`chip ${filters.type === t ? 'selected' : ''}`}
              onClick={() => set({ type: t })}
            >
              {t === 'ALL' ? 'All Modes' : TYPE_META[t].label}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="empty">
          <span className="spinner" aria-hidden /> Loading appointments…
        </div>
      ) : appointments.length === 0 ? (
        <div className="empty">
          <p>No appointments match the selected filters.</p>
        </div>
      ) : (
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Patient Details</th>
                <th>Mode</th>
                <th>Doctor & Speciality</th>
                <th>Date & Time</th>
                <th>Duration & Reason</th>
                <th>Status</th>
                <th className="actions-header">Actions</th>
              </tr>
            </thead>
            <tbody>
              {appointments.map((a) => {
                const actions = nextActions(a.status);
                const isLocked = a.status === 'COMPLETED';
                return (
                  <tr key={a.id} className={`row-status-${a.status.toLowerCase()}`}>
                    <td>
                      <div className="patient-cell">
                        <b>{a.patient_name}</b>
                        <span className="mono-phone">{a.patient_phone}</span>
                      </div>
                    </td>
                    <td>
                      <TypeBadge type={a.appointment_type} />
                    </td>
                    <td>
                      <div className="doctor-cell">
                        <b>{a.doctor_name}</b>
                        <small>{titleCase(a.department)}</small>
                      </div>
                    </td>
                    <td>
                      <div className="time-cell">
                        <b>{formatTime(a.scheduled_at)}</b>
                        <small>{formatDay(a.scheduled_at)}</small>
                      </div>
                    </td>
                    <td>
                      <div className="reason-cell">
                        <span>{a.reason || 'General examination'}</span>
                        <small>{a.duration_minutes} min</small>
                      </div>
                    </td>
                    <td>
                      <StatusBadge status={a.status} />
                    </td>
                    <td className="actions-cell">
                      <div className="row-actions">
                        {actions.map((act) => (
                          <button
                            key={act.status}
                            className={`btn-action btn-${act.kind}`}
                            onClick={() => onStatusChange(a, act.status, act.label)}
                          >
                            {act.label}
                          </button>
                        ))}
                        {!isLocked && (
                          <button className="btn-icon" onClick={() => onEdit(a)} title="Edit appointment">
                            ✎
                          </button>
                        )}
                        {confirmingId === a.id ? (
                          <span className="confirm-delete">
                            <button
                              className="btn-danger-confirm"
                              onClick={() => {
                                onDelete(a);
                                setConfirmingId(null);
                              }}
                            >
                              Confirm
                            </button>
                            <button className="btn-cancel" onClick={() => setConfirmingId(null)}>
                              ✕
                            </button>
                          </span>
                        ) : (
                          <button
                            className="btn-icon btn-delete"
                            onClick={() => setConfirmingId(a.id)}
                            title="Delete appointment"
                          >
                            🗑
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
