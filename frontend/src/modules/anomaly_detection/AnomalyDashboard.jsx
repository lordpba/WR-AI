import React, { useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle, BrainCircuit, Activity } from 'lucide-react';
import { ResponsiveContainer, ComposedChart, Line, Scatter, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

// Internal Component for Historical Chart
const HistoryChart = ({ data, dataKey, color, title, unit, onPointClick }) => {
    return (
      <div className="card" style={{ height: '350px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
          <h3 style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>{title} (History)</h3>
          <div style={{ fontSize: '0.8rem', opacity: 0.7 }}>Click red points to Diagnose</div>
        </div>
        <ResponsiveContainer width="100%" height="85%">
          <ComposedChart data={data} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
            <XAxis 
                dataKey="timestamp" 
                tickFormatter={(unixTime) => new Date(unixTime * 1000).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})} 
                minTickGap={30}
            />
            <YAxis />
            <Tooltip 
              contentStyle={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--glass-border)' }}
              labelFormatter={(unixTime) => new Date(unixTime * 1000).toLocaleString()}
            />
            <Line 
              type="monotone" 
              dataKey={dataKey} 
              stroke={color} 
              strokeWidth={2}
              dot={(props) => {
                  const { cx, cy, payload } = props;
                  // Highlight anomalies with red dots
                  if (payload.status === 'critical' || payload.status === 'warning') {
                      return (
                          <circle 
                              cx={cx} 
                              cy={cy} 
                              r={6} 
                              fill="red" 
                              stroke="white"
                              strokeWidth={2}
                              style={{ cursor: 'pointer' }}
                              onClick={() => {
                                  const evt = {
                                      timestamp: payload.timestamp,
                                      type: payload.status === 'critical' ? 'CRITICAL' : 'WARNING',
                                      message: `Historical Anomaly detected in ${dataKey}`,
                                      details: {
                                          vibration: payload.vibration,
                                          temperature: payload.temperature,
                                          power: payload.power
                                      },
                                      value: payload[dataKey]
                                  };
                                  onPointClick(evt);
                              }}
                          />
                      );
                  }
                  return null;
              }}
              isAnimationActive={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    );
  };

export function AnomalyDashboard({ onDiagnose }) {
  const [historyData, setHistoryData] = useState([]);
  const [events, setEvents] = useState([]);
  const [status, setStatus] = useState({ status: 'init', model_ready: false });
  const [loading, setLoading] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [historyRes, eventsRes, statusRes] = await Promise.all([
        fetch('http://localhost:8000/api/anomaly/stream?limit=1000'), // Fetch large history
        fetch('http://localhost:8000/api/anomaly/events'),
        fetch('http://localhost:8000/api/anomaly/status')
      ]);

      const hData = await historyRes.json();
      const eventsData = await eventsRes.json();
      const statusData = await statusRes.json();

      setHistoryData(hData);
      setEvents(eventsData);
      setStatus(statusData);
    } catch (e) {
      console.error("Anomaly Module fetch error", e);
    } finally {
        setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // Refresh history every 10 seconds (less frequent than real-time)
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="dashboard-grid">
      
      {/* Header Actions */}
      <div className="card" style={{ gridColumn: 'span 12', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
         <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <BrainCircuit size={24} color={status.model_ready ? 'var(--primary)' : 'var(--text-muted)'} />
            <div>
                <strong>Anomaly History Analysis</strong>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Review past performance and detailed anomalies</div>
            </div>
         </div>
         <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
             <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Last 1000 points</span>
             <button onClick={fetchData} className="btn" disabled={loading}>
                 {loading ? 'Refreshing...' : 'Refresh Data'}
             </button>
         </div>
      </div>

      {/* Historical Charts Row */}
      <div style={{ gridColumn: 'span 12' }}>
        <HistoryChart 
            data={historyData} 
            dataKey="vibration" 
            color="#00f2ff" 
            title="Vibration History" 
            unit="mm/s" 
            onPointClick={onDiagnose}
        />
      </div>
      
      <div style={{ gridColumn: 'span 6' }}>
        <HistoryChart 
            data={historyData} 
            dataKey="temperature" 
            color="#ff00cc" 
            title="Temperature History" 
            unit="°C" 
            onPointClick={onDiagnose}
        />
      </div>

      <div style={{ gridColumn: 'span 6' }}>
         <HistoryChart 
            data={historyData} 
            dataKey="power" 
            color="#ffc658" 
            title="Power History" 
            unit="kW" 
            onPointClick={onDiagnose}
        />
      </div>

      {/* Events Log */}
      <div className="card" style={{ gridColumn: 'span 12' }}>
        <h3 style={{ marginBottom: '1rem' }}>Anomaly Event Log</h3>
        <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                    <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', textAlign: 'left' }}>
                        <th style={{ padding: '0.5rem' }}>Time</th>
                        <th style={{ padding: '0.5rem' }}>Type</th>
                        <th style={{ padding: '0.5rem' }}>Message</th>
                        <th style={{ padding: '0.5rem' }}>Details</th>
                        <th style={{ padding: '0.5rem' }}>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {events.map((evt, i) => (
                        <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                            <td style={{ padding: '0.5rem', color: 'var(--text-muted)' }}>
                                {new Date(evt.timestamp * 1000).toLocaleString()}
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
                            <td style={{ padding: '0.5rem' }}>
                                V: {evt.details.vibration?.toFixed(2)} | T: {evt.details.temperature?.toFixed(1)}
                            </td>
                            <td style={{ padding: '0.5rem' }}>
                                <button 
                                    onClick={() => onDiagnose && onDiagnose(evt)}
                                    className="btn" 
                                    style={{ 
                                        padding: '0.25rem 0.5rem', 
                                        fontSize: '0.75rem',
                                        background: 'var(--primary)',
                                        border: 'none',
                                        borderRadius: '4px',
                                        color: 'white',
                                        cursor: 'pointer',
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '0.25rem'
                                    }}
                                >
                                    <BrainCircuit size={12} /> Diagnose
                                </button>
                            </td>
                        </tr>
                    ))}
                    {events.length === 0 && (
                        <tr>
                            <td colSpan="5" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                                No anomalies in history.
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
