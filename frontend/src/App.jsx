import { useCallback, useEffect, useMemo, useState } from 'react';
import { api } from './api.js';
import { filterAppointments } from './lib/appointments.js';
import Sidebar from './components/Sidebar.jsx';
import StatCards from './components/StatCards.jsx';
import AppointmentTable from './components/AppointmentTable.jsx';
import AppointmentModal from './components/AppointmentModal.jsx';
import TodayPanel from './components/TodayPanel.jsx';
import DepartmentChart from './components/DepartmentChart.jsx';
import DoctorsView from './components/DoctorsView.jsx';
import Toast from './components/Toast.jsx';

const EMPTY_STATS = {
  total: 0,
  today: 0,
  scheduled: 0,
  checkedIn: 0,
  completed: 0,
  cancelled: 0,
  noShow: 0,
  inPerson: 0,
  teleconsult: 0,
  byDepartment: {},
};
const REFRESH_MS = 30_000;

export default function App() {
  const [view, setView] = useState('dashboard');
  const [appointments, setAppointments] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [stats, setStats] = useState(EMPTY_STATS);
  const [info, setInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({ status: 'ALL', department: 'ALL', type: 'ALL', query: '' });
  const [modal, setModal] = useState(null); // null | { mode: 'create' } | { mode: 'edit', appointment }
  const [toast, setToast] = useState(null);

  const notify = useCallback((message, tone = 'success') => setToast({ message, tone, id: Date.now() }), []);
  const dismissToast = useCallback(() => setToast(null), []);
  const closeModal = useCallback(() => setModal(null), []);

  const load = useCallback(async () => {
    try {
      const [appts, docs, s] = await Promise.all([api.appointments(), api.doctors(), api.stats()]);
      setAppointments(appts || []);
      setDoctors(docs || []);
      setStats(s || EMPTY_STATS);
      setError('');
    } catch (e) {
      setError(e.message || 'ClinicPulse backend unreachable');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    api.info().then(setInfo).catch(() => setInfo(null));
    const timer = setInterval(load, REFRESH_MS);
    return () => clearInterval(timer);
  }, [load]);

  const visible = useMemo(() => filterAppointments(appointments, filters), [appointments, filters]);

  const runAction = async (fn, successMessage) => {
    try {
      await fn();
      notify(successMessage);
      await load();
      return true;
    } catch (e) {
      notify(e.message, 'error');
      return false;
    }
  };

  const changeStatus = (appointment, status, label) =>
    runAction(
      () => api.updateAppointment(appointment.id, { status }),
      `${appointment.patient_name}: marked as ${label.toLowerCase()}`,
    );

  const remove = (appointment) =>
    runAction(
      () => api.deleteAppointment(appointment.id),
      `Appointment for ${appointment.patient_name} removed`,
    );

  const save = async (payload) => {
    if (modal?.mode === 'edit') {
      await api.updateAppointment(modal.appointment.id, payload);
      notify('Appointment updated successfully');
    } else {
      await api.createAppointment(payload);
      notify(`Appointment scheduled for ${payload.patient_name}`);
    }
    await load();
  };

  const addDoctor = async (payload) => {
    return runAction(
      () => api.createDoctor(payload),
      `${payload.name} added to ${payload.department} roster`,
    );
  };

  return (
    <div className="app">
      <Sidebar view={view} onNavigate={setView} info={info} />

      <main className="main-content">
        <header className="top-bar">
          <div className="header-titles">
            <h1>{view === 'dashboard' ? 'Outpatient Operations & Appointments' : 'Doctor Directory & Specialists'}</h1>
            <p className="subtitle">
              {view === 'dashboard'
                ? 'Manage patient arrivals, clinical workflows, and visit lifecycles in real time.'
                : 'Manage clinical staffing, room allocation, and active department assignments.'}
            </p>
          </div>
          <div className="header-actions">
            <button
              className="btn-book"
              onClick={() => setModal({ mode: 'create' })}
              disabled={doctors.length === 0}
            >
              <span aria-hidden>+</span> Schedule Appointment
            </button>
          </div>
        </header>

        {error && (
          <div className="banner-error" role="alert">
            <span>⚠</span>
            <div>
              <strong>Backend Disconnected:</strong> {error}
            </div>
            <button onClick={load}>Retry Connection</button>
          </div>
        )}

        {view === 'dashboard' && (
          <>
            <StatCards stats={stats} />

            <div className="dashboard-grid">
              <div className="main-column">
                <AppointmentTable
                  loading={loading}
                  appointments={visible}
                  totalCount={appointments.length}
                  filters={filters}
                  onFiltersChange={setFilters}
                  onStatusChange={changeStatus}
                  onEdit={(appointment) => setModal({ mode: 'edit', appointment })}
                  onDelete={remove}
                />
              </div>

              <aside className="side-column">
                <TodayPanel appointments={appointments} />
                <DepartmentChart byDepartment={stats.byDepartment} />
              </aside>
            </div>
          </>
        )}

        {view === 'doctors' && (
          <DoctorsView doctors={doctors} appointments={appointments} onAdd={addDoctor} />
        )}

        <footer className="footer">
          <div>
            <b>ClinicPulse</b> · Healthcare Platform v1.0.0 · DevOps Final Capstone
          </div>
          <div className="footer-meta">
            <span>Engineer: <strong>Tejas Kumat</strong></span>
            <span>·</span>
            <span>Git SHA: <code>{info?.gitSha?.slice(0, 7) ?? 'local'}</code></span>
            <span>·</span>
            <span className="live-pill">● System Operational</span>
          </div>
        </footer>
      </main>

      {modal && (
        <AppointmentModal
          mode={modal.mode}
          appointment={modal.appointment}
          doctors={doctors}
          onClose={closeModal}
          onSave={save}
        />
      )}

      {toast && <Toast message={toast.message} tone={toast.tone} onDone={dismissToast} />}
    </div>
  );
}
