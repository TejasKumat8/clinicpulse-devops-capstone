const NAV = [
  { id: 'dashboard', label: 'Appointments', icon: '▦' },
  { id: 'doctors', label: 'Doctor Roster', icon: '⚕' },
];

const PIPELINE = ['Pytest', 'Docker', 'Trivy', 'GHCR', 'Helm'];

export default function Sidebar({ view, onNavigate, info }) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <span className="brand-mark" aria-hidden>
          ✚
        </span>
        <div>
          <b>ClinicPulse</b>
          <small>Triage & Scheduling</small>
        </div>
      </div>

      <nav aria-label="Main Navigation">
        {NAV.map((item) => (
          <button
            key={item.id}
            className={`nav-link ${view === item.id ? 'active' : ''}`}
            onClick={() => onNavigate(item.id)}
            aria-current={view === item.id ? 'page' : undefined}
          >
            <span className="nav-icon" aria-hidden>{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="side-bottom">
        <div className="deploy-card">
          <div className="deploy-header">
            <strong>DevOps Delivery</strong>
            <span className="badge-live">LIVE</span>
          </div>
          <div className="pipeline">
            {PIPELINE.map((step, i) => (
              <span key={step} className="pipeline-step">
                {i > 0 && <i aria-hidden />}
                {step}
              </span>
            ))}
          </div>
          <p className="build-info">
            Build Commit: <code>{info?.gitSha?.slice(0, 7) ?? 'local'}</code>
          </p>
        </div>

        <div className="profile">
          <div className="avatar">TK</div>
          <div>
            <b>Tejas Kumat</b>
            <small>DevOps Lead / SRE</small>
          </div>
        </div>
      </div>
    </aside>
  );
}
