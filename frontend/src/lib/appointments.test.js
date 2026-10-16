import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  defaultSlot,
  filterAppointments,
  formatDay,
  initials,
  nextActions,
  titleCase,
  toWallClockIso,
} from './appointments.js';

const sample = [
  {
    patient_name: 'Asha Verma',
    patient_phone: '+91 98765 43210',
    doctor_name: 'Dr. Rajesh Sharma',
    department: 'GENERAL',
    appointment_type: 'IN_PERSON',
    status: 'SCHEDULED',
  },
  {
    patient_name: 'Kabir Joshi',
    patient_phone: '+91 91234 56789',
    doctor_name: 'Dr. Sunita Verma',
    department: 'CARDIOLOGY',
    appointment_type: 'TELECONSULT',
    status: 'COMPLETED',
  },
];

test('completed appointments have no further transitions', () => {
  assert.deepEqual(nextActions('COMPLETED'), []);
  assert.deepEqual(nextActions('SCHEDULED').map((a) => a.status), ['CHECKED_IN', 'NO_SHOW', 'CANCELLED']);
});

test('filters by status, department, consultation mode, and search text', () => {
  assert.equal(filterAppointments(sample, { status: 'COMPLETED' }).length, 1);
  assert.equal(filterAppointments(sample, { department: 'GENERAL' })[0].patient_name, 'Asha Verma');
  assert.equal(filterAppointments(sample, { type: 'TELECONSULT' })[0].patient_name, 'Kabir Joshi');
  assert.equal(filterAppointments(sample, { query: 'joshi' })[0].patient_name, 'Kabir Joshi');
  assert.equal(filterAppointments(sample, { query: '9876543210' }).length, 1);
});

test('formats labels and initials', () => {
  assert.equal(titleCase('CHECKED_IN'), 'Checked In');
  assert.equal(initials('Dr. Rajesh Sharma'), 'RS');
});

test('builds naive wall-clock ISO timestamps', () => {
  assert.equal(toWallClockIso('2030-01-02', '09:30'), '2030-01-02T09:30:00');
});

test('relative day labels', () => {
  const now = new Date(2030, 0, 1, 8, 0);
  assert.equal(formatDay(new Date(2030, 0, 1, 14, 0).toISOString(), now), 'Today');
  assert.equal(formatDay(new Date(2030, 0, 2, 9, 0).toISOString(), now), 'Tomorrow');
});

test('default booking slot is tomorrow 10:00', () => {
  const slot = defaultSlot(new Date(2030, 0, 1, 18, 45));
  assert.equal(slot.getDate(), 2);
  assert.equal(slot.getHours(), 10);
});
