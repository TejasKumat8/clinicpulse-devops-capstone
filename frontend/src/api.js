// API fetch client for ClinicPulse using relative /api paths
const API = '/api';

function errorMessage(body, status) {
  const detail = body?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail) && detail.length) {
    return detail.map((d) => `${d.loc?.slice(-1)[0] ?? 'field'}: ${d.msg}`).join('; ');
  }
  return `Request failed with HTTP ${status}`;
}

async function request(path, { method = 'GET', body } = {}) {
  const response = await fetch(`${API}${path}`, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (response.status === 204) return null;
  const data = await response.json().catch(() => null);
  if (!response.ok) throw new Error(errorMessage(data, response.status));
  return data;
}

export const api = {
  info: () => request('/info'),
  doctors: () => request('/doctors'),
  createDoctor: (doctor) => request('/doctors', { method: 'POST', body: doctor }),
  appointments: () => request('/appointments?limit=500'),
  stats: () => request('/appointments/stats'),
  createAppointment: (payload) => request('/appointments', { method: 'POST', body: payload }),
  updateAppointment: (id, payload) => request(`/appointments/${id}`, { method: 'PUT', body: payload }),
  deleteAppointment: (id) => request(`/appointments/${id}`, { method: 'DELETE' }),
};
