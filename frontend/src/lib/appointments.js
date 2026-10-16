// Domain helpers for appointments and clinical scheduling (tested via `node --test`)

export const DEPARTMENTS = ['GENERAL', 'CARDIOLOGY', 'DERMATOLOGY', 'PEDIATRICS', 'ORTHOPEDICS', 'NEUROLOGY'];

export const STATUS_META = {
  SCHEDULED: { label: 'Scheduled', tone: 'blue' },
  CHECKED_IN: { label: 'Checked In', tone: 'amber' },
  COMPLETED: { label: 'Completed', tone: 'green' },
  CANCELLED: { label: 'Cancelled', tone: 'grey' },
  NO_SHOW: { label: 'No-Show', tone: 'red' },
};

export const TYPE_META = {
  IN_PERSON: { label: 'In-Person', tone: 'emerald' },
  TELECONSULT: { label: 'Teleconsult', tone: 'cyan' },
};

const ACTIONS = {
  SCHEDULED: [
    { status: 'CHECKED_IN', label: 'Check In', kind: 'primary' },
    { status: 'NO_SHOW', label: 'No-Show', kind: 'ghost' },
    { status: 'CANCELLED', label: 'Cancel', kind: 'ghost' },
  ],
  CHECKED_IN: [
    { status: 'COMPLETED', label: 'Complete Visit', kind: 'primary' },
    { status: 'CANCELLED', label: 'Cancel', kind: 'ghost' },
  ],
  CANCELLED: [{ status: 'SCHEDULED', label: 'Rebook', kind: 'ghost' }],
  NO_SHOW: [{ status: 'SCHEDULED', label: 'Rebook', kind: 'ghost' }],
  COMPLETED: [],
};

export function nextActions(status) {
  return ACTIONS[status] ?? [];
}

export function titleCase(value) {
  return value
    .toLowerCase()
    .split('_')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');
}

export function initials(name) {
  return name
    .replace(/^dr\.?\s+/i, '')
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0].toUpperCase())
    .join('');
}

const pad = (n) => String(n).padStart(2, '0');

export function toDateInput(date) {
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
}

export function toTimeInput(date) {
  return `${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

export function toWallClockIso(dateStr, timeStr) {
  return `${dateStr}T${timeStr}:00`;
}

export function isSameDay(a, b) {
  return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate();
}

export function formatTime(iso) {
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

export function formatDay(iso, now = new Date()) {
  const date = new Date(iso);
  if (isSameDay(date, now)) return 'Today';
  const tomorrow = new Date(now);
  tomorrow.setDate(now.getDate() + 1);
  if (isSameDay(date, tomorrow)) return 'Tomorrow';
  return date.toLocaleDateString([], { weekday: 'short', day: 'numeric', month: 'short' });
}

export function filterAppointments(list, { status = 'ALL', department = 'ALL', type = 'ALL', query = '' } = {}) {
  const q = query.trim().toLowerCase();
  return list.filter(
    (a) =>
      (status === 'ALL' || a.status === status) &&
      (department === 'ALL' || a.department === department) &&
      (type === 'ALL' || a.appointment_type === type) &&
      (!q ||
        a.patient_name.toLowerCase().includes(q) ||
        a.doctor_name.toLowerCase().includes(q) ||
        a.patient_phone.replace(/\s/g, '').includes(q.replace(/\s/g, ''))),
  );
}

export function defaultSlot(now = new Date()) {
  const slot = new Date(now);
  slot.setDate(slot.getDate() + 1);
  slot.setHours(10, 0, 0, 0);
  return slot;
}
