import { useEffect, useMemo, useState } from 'react';
import { DEPARTMENTS, defaultSlot, titleCase, toDateInput, toTimeInput, toWallClockIso } from '../lib/appointments.js';

const DURATIONS = [15, 20, 30, 45, 60, 90];

function initialForm(appointment, doctors) {
  if (appointment) {
    const start = new Date(appointment.scheduled_at);
    return {
      patient_name: appointment.patient_name,
      patient_phone: appointment.patient_phone,
      department: appointment.department,
      doctor_id: String(appointment.doctor_id),
      date: toDateInput(start),
      time: toTimeInput(start),
      duration_minutes: appointment.duration_minutes,
      reason: appointment.reason || '',
      appointment_type: appointment.appointment_type || 'IN_PERSON',
      notes: appointment.notes || '',
    };
  }
  const slot = defaultSlot();
  const first = doctors[0];
  return {
    patient_name: '',
    patient_phone: '',
    department: first?.department ?? 'GENERAL',
    doctor_id: first ? String(first.id) : '',
    date: toDateInput(slot),
    time: toTimeInput(slot),
    duration_minutes: 30,
    reason: '',
    appointment_type: 'IN_PERSON',
    notes: '',
  };
}

export default function AppointmentModal({ mode, appointment, doctors, onClose, onSave }) {
  const [form, setForm] = useState(() => initialForm(appointment, doctors));
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const doctorsInDept = useMemo(
    () => doctors.filter((d) => d.department === form.department),
    [doctors, form.department],
  );

  useEffect(() => {
    const onKey = (e) => e.key === 'Escape' && onClose();
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [onClose]);

  const update = (patch) => setForm((f) => ({ ...f, ...patch }));

  const changeDepartment = (department) => {
    const firstDoctor = doctors.find((d) => d.department === department);
    update({ department, doctor_id: firstDoctor ? String(firstDoctor.id) : '' });
  };

  const submit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    try {
      await onSave({
        patient_name: form.patient_name.trim(),
        patient_phone: form.patient_phone.trim(),
        doctor_id: Number(form.doctor_id),
        scheduled_at: toWallClockIso(form.date, form.time),
        duration_minutes: Number(form.duration_minutes),
        reason: form.reason.trim(),
        appointment_type: form.appointment_type,
        notes: form.notes.trim(),
      });
      onClose();
    } catch (err) {
      setError(err.message);
      setSaving(false);
    }
  };

  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="modal-title">
      <div className="modal">
        <div className="modal-head">
          <div>
            <h2 id="modal-title">{mode === 'edit' ? 'Reschedule / Edit Visit' : 'Schedule New Appointment'}</h2>
            <p className="muted">
              {mode === 'edit' ? 'Update consultation details or timing' : 'Book a confirmed slot with conflict checking'}
            </p>
          </div>
          <button className="btn-close" onClick={onClose} aria-label="Close dialog">
            ✕
          </button>
        </div>

        {error && (
          <div className="alert-error" role="alert">
            <span aria-hidden>⚠</span> {error}
          </div>
        )}

        <form onSubmit={submit}>
          <div className="form-grid">
            <label>
              <span>Patient Full Name *</span>
              <input
                required
                minLength={2}
                maxLength={120}
                placeholder="e.g. Ramesh Patel"
                value={form.patient_name}
                onChange={(e) => update({ patient_name: e.target.value })}
              />
            </label>

            <label>
              <span>Phone Number *</span>
              <input
                required
                type="tel"
                placeholder="+91 98765 43210"
                value={form.patient_phone}
                onChange={(e) => update({ patient_phone: e.target.value })}
              />
            </label>
          </div>

          <div className="form-group">
            <span className="field-label">Consultation Mode *</span>
            <div className="radio-pill-group">
              <label className={`radio-pill ${form.appointment_type === 'IN_PERSON' ? 'active' : ''}`}>
                <input
                  type="radio"
                  name="appointment_type"
                  value="IN_PERSON"
                  checked={form.appointment_type === 'IN_PERSON'}
                  onChange={(e) => update({ appointment_type: e.target.value })}
                />
                🏥 In-Person Clinic Visit
              </label>
              <label className={`radio-pill ${form.appointment_type === 'TELECONSULT' ? 'active' : ''}`}>
                <input
                  type="radio"
                  name="appointment_type"
                  value="TELECONSULT"
                  checked={form.appointment_type === 'TELECONSULT'}
                  onChange={(e) => update({ appointment_type: e.target.value })}
                />
                💻 Teleconsultation (Video)
              </label>
            </div>
          </div>

          <div className="form-grid">
            <label>
              <span>Department *</span>
              <select value={form.department} onChange={(e) => changeDepartment(e.target.value)}>
                {DEPARTMENTS.map((dept) => (
                  <option key={dept} value={dept}>
                    {titleCase(dept)}
                  </option>
                ))}
              </select>
            </label>

            <label>
              <span>Doctor *</span>
              <select
                required
                value={form.doctor_id}
                onChange={(e) => update({ doctor_id: e.target.value })}
              >
                {doctorsInDept.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.name} {d.room ? `(${d.room})` : ''}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <div className="form-grid form-grid-3">
            <label>
              <span>Date *</span>
              <input
                required
                type="date"
                value={form.date}
                onChange={(e) => update({ date: e.target.value })}
              />
            </label>

            <label>
              <span>Time *</span>
              <input
                required
                type="time"
                step="300"
                value={form.time}
                onChange={(e) => update({ time: e.target.value })}
              />
            </label>

            <label>
              <span>Duration *</span>
              <select
                value={form.duration_minutes}
                onChange={(e) => update({ duration_minutes: Number(e.target.value) })}
              >
                {DURATIONS.map((m) => (
                  <option key={m} value={m}>
                    {m} minutes
                  </option>
                ))}
              </select>
            </label>
          </div>

          <label>
            <span>Primary Reason / Symptoms</span>
            <input
              placeholder="e.g. Chest tightness on exertion, routine cardiology follow-up"
              maxLength={1000}
              value={form.reason}
              onChange={(e) => update({ reason: e.target.value })}
            />
          </label>

          <label>
            <span>Internal Clinical Notes</span>
            <textarea
              rows={2}
              placeholder="e.g. Needs previous ECG records; allergy to penicillin"
              maxLength={1000}
              value={form.notes}
              onChange={(e) => update({ notes: e.target.value })}
            />
          </label>

          <div className="modal-foot">
            <button type="button" className="btn-cancel-modal" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn-submit-modal" disabled={saving || !form.doctor_id}>
              {saving ? 'Validating slot…' : mode === 'edit' ? 'Save Changes' : 'Confirm & Book'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
