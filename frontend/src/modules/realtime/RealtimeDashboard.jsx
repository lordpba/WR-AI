import React, { useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle, PlugZap } from 'lucide-react';

export function RealtimeDashboard() {
  const [rtStatus, setRtStatus] = useState(null);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchRealtime = async () => {
    try {
      setLoading(true);
      const [sRes, eRes] = await Promise.all([
        fetch('http://localhost:8000/api/realtime/status'),
        fetch('http://localhost:8000/api/realtime/events?limit=100')
      ]);
      const s = await sRes.json();
      const e = await eRes.json();
      setRtStatus(s);
      setEvents(Array.isArray(e) ? e : []);
    } catch (err) {
      console.error('Realtime fetch failed', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRealtime();
    const t = setInterval(fetchRealtime, 2000);
    return () => clearInterval(t);
  }, []);

  const connected = !!rtStatus?.connected;
  const configured = !!rtStatus?.configured;

  return (
    <main className="dashboard-grid">
      <div className="card" style={{ gridColumn: 'span 12', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <PlugZap size={22} color={connected ? 'var(--primary)' : 'var(--text-muted)'} />
          <div>
            <strong>Realtime (Modbus TCP)</strong>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Status: <strong>{connected ? 'CONNECTED' : (configured ? 'DISCONNECTED' : 'NOT CONFIGURED')}</strong>
              {rtStatus?.last_error ? ` • last_error: ${rtStatus.last_error}` : ''}
            </div>
          </div>
        </div>
        <button className="btn" onClick={fetchRealtime} disabled={loading}>
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      <div className="card" style={{ gridColumn: 'span 12' }}>
        <h3 style={{ marginBottom: '1rem' }}>Realtime Alerts (rule-based)</h3>
        <div style={{ maxHeight: 420, overflowY: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', textAlign: 'left' }}>
                <th style={{ padding: '0.5rem' }}>Time</th>
                <th style={{ padding: '0.5rem' }}>Type</th>
                <th style={{ padding: '0.5rem' }}>Message</th>
                <th style={{ padding: '0.5rem' }}>Details</th>
              </tr>
            </thead>
            <tbody>
              {events.map((evt) => (
                <tr key={evt.id || `${evt.timestamp}-${evt.type}`} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                  <td style={{ padding: '0.5rem', color: 'var(--text-muted)' }}>
                    {new Date(evt.timestamp * 1000).toLocaleString()}
                  </td>
                  <td style={{ padding: '0.5rem' }}>
                    <span style={{
                      padding: '2px 8px',
                      borderRadius: '4px',
                      fontSize: '0.8rem',
                      backgroundColor: evt.type === 'CRITICAL' ? 'rgba(255,50,50,0.2)' : (evt.type === 'WARNING' ? 'rgba(255,200,0,0.2)' : 'rgba(0,242,255,0.15)'),
                      color: evt.type === 'CRITICAL' ? 'var(--danger)' : (evt.type === 'WARNING' ? 'var(--warning)' : 'var(--primary)'),
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '0.35rem'
                    }}>
                      {evt.type === 'CRITICAL' ? <AlertTriangle size={12} /> : <CheckCircle size={12} />}
                      {evt.type}
                    </span>
                  </td>
                  <td style={{ padding: '0.5rem' }}>{evt.message}</td>
                  <td style={{ padding: '0.5rem', color: 'var(--text-muted)' }}>
                    {evt.details ? JSON.stringify(evt.details) : ''}
                  </td>
                </tr>
              ))}
              {events.length === 0 && (
                <tr>
                  <td colSpan="4" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                    No realtime alerts yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </main>
  );
}

