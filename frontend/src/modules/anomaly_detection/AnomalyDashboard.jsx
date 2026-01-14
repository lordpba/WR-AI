import React, { useEffect, useState } from 'react';
import { SignalChart } from './SignalChart';
import { AlertTriangle, CheckCircle, BrainCircuit, Activity } from 'lucide-react';

export function AnomalyDashboard() {
  const [stream, setStream] = useState([]);
  const [events, setEvents] = useState([]);
  const [status, setStatus] = useState({ status: 'init', model_ready: false });
  const [lastUpdate, setLastUpdate] = useState(Date.now());

  const fetchData = async () => {
    try {
      const [streamRes, eventsRes, statusRes] = await Promise.all([
        fetch('http://localhost:8000/api/anomaly/stream'),
        fetch('http://localhost:8000/api/anomaly/events'),
        fetch('http://localhost:8000/api/anomaly/status')
      ]);

      const streamData = await streamRes.json();
      const eventsData = await eventsRes.json();
      const statusData = await statusRes.json();

      setStream(streamData);
      setEvents(eventsData);
      setStatus(statusData);
      setLastUpdate(Date.now());
    } catch (e) {
      console.error("Anomaly Module fetch error", e);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 1000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (s) => {
      if (s === 'critical') return 'var(--danger)';
      if (s === 'warning') return 'var(--warning)';
      return 'var(--success)';
  }

  const getStatusIcon = (s) => {
    if (s === 'critical' || s === 'warning') return <AlertTriangle size={32} />;
    return <CheckCircle size={32} />;
  }

  return (
    <div className="dashboard-grid">
      {/* Header Stat Cards */}
      <div className="card" style={{ gridColumn: 'span 4', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
         <div>
             <h3 style={{ color: 'var(--text-muted)' }}>System Health</h3>
             <div style={{ fontSize: '1.5rem', fontWeight: 'bold', marginTop: '0.5rem', color: getStatusColor(status.status), textTransform: 'capitalize' }}>
                 {status.status}
             </div>
         </div>
         <div style={{ color: getStatusColor(status.status) }}>
             {getStatusIcon(status.status)}
         </div>
      </div>

      <div className="card" style={{ gridColumn: 'span 4' }}>
         <h3 style={{ color: 'var(--text-muted)' }}>AI Model Status</h3>
         <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginTop: '0.5rem' }}>
             <BrainCircuit size={24} color={status.model_ready ? 'var(--primary)' : 'var(--text-muted)'} />
             <div>
                <div style={{ fontWeight: 'bold' }}>{status.model_ready ? 'Active' : 'Calibrating...'}</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Isolation Forest (Unsupervised)</div>
             </div>
         </div>
      </div>

       <div className="card" style={{ gridColumn: 'span 4' }}>
         <h3 style={{ color: 'var(--text-muted)' }}>Anomaly Score</h3>
         <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginTop: '0.5rem' }}>
             <Activity size={24} color={stream.length > 0 && stream[stream.length-1].anomaly_score > 50 ? 'var(--danger)' : 'var(--success)'} />
             <div>
                <div style={{ fontWeight: 'bold', fontSize: '1.2rem' }}>
                    {stream.length > 0 ? stream[stream.length-1].anomaly_score.toFixed(1) : 0}%
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Real-time Risk Index</div>
             </div>
         </div>
      </div>

      {/* Charts Row */}
      <div style={{ gridColumn: 'span 4' }}>
        <SignalChart data={stream} dataKey="vibration" color="#8884d8" title="Vibration Sensor" unit="mm/s" domain={[0, 2]} />
      </div>
      <div style={{ gridColumn: 'span 4' }}>
        <SignalChart data={stream} dataKey="temperature" color="#82ca9d" title="Temperature Sensor" unit="°C" domain={[20, 80]} />
      </div>
      <div style={{ gridColumn: 'span 4' }}>
        <SignalChart data={stream} dataKey="power" color="#ffc658" title="Power Consumption" unit="kW" domain={[0, 100]} />
      </div>

      {/* Events Log */}
      <div className="card" style={{ gridColumn: 'span 12' }}>
        <h3 style={{ marginBottom: '1rem' }}>Anomaly Event Log</h3>
        <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                    <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', textAlign: 'left' }}>
                        <th style={{ padding: '0.5rem' }}>Time</th>
                        <th style={{ padding: '0.5rem' }}>Type</th>
                        <th style={{ padding: '0.5rem' }}>Message</th>
                        <th style={{ padding: '0.5rem' }}>Vibration</th>
                    </tr>
                </thead>
                <tbody>
                    {events.map((evt, i) => (
                        <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                            <td style={{ padding: '0.5rem', color: 'var(--text-muted)' }}>
                                {new Date(evt.timestamp * 1000).toLocaleTimeString()}
                            </td>
                            <td style={{ padding: '0.5rem' }}>
                                <span style={{ 
                                    padding: '2px 8px', borderRadius: '4px', fontSize: '0.8rem',
                                    backgroundColor: evt.type === 'CRITICAL' ? 'rgba(255,50,50,0.2)' : 'rgba(255,200,0,0.2)',
                                    color: evt.type === 'CRITICAL' ? 'var(--danger)' : 'var(--warning)'
                                }}>
                                    {evt.type}
                                </span>
                            </td>
                            <td style={{ padding: '0.5rem' }}>{evt.message}</td>
                            <td style={{ padding: '0.5rem' }}>{evt.details.vibration.toFixed(3)} mm/s</td>
                        </tr>
                    ))}
                    {events.length === 0 && (
                        <tr>
                            <td colSpan="4" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                                No anomalies detected recently. System running smoothly.
                            </td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
      </div>
    </div>
  );
}

