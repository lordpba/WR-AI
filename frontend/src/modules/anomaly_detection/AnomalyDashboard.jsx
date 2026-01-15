import React, { useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle, BrainCircuit, Activity, Play, Settings, Download, Trash2 } from 'lucide-react';
import { SignalChart } from './SignalChart';

// Internal Component for Historical Chart
const HistoryChart = ({ data, dataKey, color, title, unit, onPointClick }) => {
  // This component is no longer needed as we're using SignalChart
  return null;
};

export function AnomalyDashboard({ onDiagnose }) {
  const [historyData, setHistoryData] = useState([]);
  const [events, setEvents] = useState([]);
  const [status, setStatus] = useState({ status: 'init', model_ready: false });
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [mlAnalyzing, setMlAnalyzing] = useState(false);
  const [mlResult, setMlResult] = useState(null);
  const [showMLSettings, setShowMLSettings] = useState(false);
  const [mlAlgorithm, setMlAlgorithm] = useState('isolation_forest');
  const [algorithms, setAlgorithms] = useState([]);
  const [selectedVibrationAnomaly, setSelectedVibrationAnomaly] = useState(null);
  const [showDataMgmt, setShowDataMgmt] = useState(false);
  const [clearLoading, setClearLoading] = useState(false);
  const [exportLoading, setExportLoading] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [historyRes, eventsRes, statusRes, statsRes] = await Promise.all([
        fetch('http://localhost:8000/api/anomaly/stream?limit=1000'), // Fetch large history
        fetch('http://localhost:8000/api/anomaly/events'),
        fetch('http://localhost:8000/api/anomaly/status'),
        fetch('http://localhost:8000/api/anomaly/stats')
      ]);

      const hData = await historyRes.json();
      const eventsData = await eventsRes.json();
      const statusData = await statusRes.json();
      const statsData = await statsRes.json();

      setHistoryData(hData);
      setEvents(eventsData);
      setStatus(statusData);
      setStats(statsData.stats);
    } catch (e) {
      console.error("Anomaly Module fetch error", e);
    } finally {
        setLoading(false);
    }
  };

  const fetchMLAlgorithms = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/anomaly/ml/algorithms');
      const data = await res.json();
      setAlgorithms(data.algorithms || []);
    } catch (e) {
      console.error("Failed to fetch ML algorithms", e);
    }
  };

  const runMLAnalysis = async () => {
    try {
      setMlAnalyzing(true);
      const res = await fetch('http://localhost:8000/api/anomaly/ml/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          algorithm: mlAlgorithm,
          window_size: 500,
          params: null
        })
      });
      const result = await res.json();
      setMlResult(result);
      alert(`ML Analysis Complete!\n${result.summary}\nFound ${result.anomaly_count} anomalies`);
    } catch (e) {
      console.error("ML Analysis failed", e);
      alert('ML Analysis failed. Check console for details.');
    } finally {
      setMlAnalyzing(false);
    }
  };

  const exportToCSV = async () => {
    try {
      setExportLoading(true);
      const res = await fetch('http://localhost:8000/api/anomaly/export/csv');
      const result = await res.json();
      
      if (result.status === 'success') {
        // Create blob and download
        const blob = new Blob([result.data], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', result.filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        alert(`✅ Exported ${result.rows_count} data points to ${result.filename}`);
      } else {
        alert(`Export failed: ${result.detail || 'Unknown error'}`);
      }
    } catch (e) {
      console.error("Export failed", e);
      alert('Export failed. Check console for details.');
    } finally {
      setExportLoading(false);
    }
  };

  const clearHistoryData = async () => {
    if (!window.confirm('⚠️ This will delete all historical monitoring data from memory.\n\nContinue?')) {
      return;
    }
    
    try {
      setClearLoading(true);
      const res = await fetch('http://localhost:8000/api/anomaly/clear-history', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ confirm: true })
      });
      const result = await res.json();
      
      if (result.status === 'success') {
        alert(`✅ ${result.message}\nDeleted ${result.data_deleted} data points`);
        fetchData(); // Refresh data
      } else {
        alert(`Failed: ${result.message}`);
      }
    } catch (e) {
      console.error("Clear failed", e);
      alert('Clear operation failed. Check console for details.');
    } finally {
      setClearLoading(false);
    }
  };

  const clearEventsData = async () => {
    if (!window.confirm('⚠️ This will clear the event log from memory.\n\nContinue?')) {
      return;
    }
    
    try {
      const res = await fetch('http://localhost:8000/api/anomaly/clear-events', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ confirm: true })
      });
      const result = await res.json();
      
      if (result.status === 'success') {
        alert(`✅ ${result.message}\nCleared ${result.events_deleted} events`);
        fetchData(); // Refresh data
      } else {
        alert(`Failed: ${result.message}`);
      }
    } catch (e) {
      console.error("Clear events failed", e);
      alert('Clear operation failed. Check console for details.');
    }
  };

  useEffect(() => {
    fetchData();
    fetchMLAlgorithms();
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
                <strong>Anomaly Detection - Statistical Baseline Mode</strong>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  Real-time monitoring with statistical thresholds. Use ML Analysis for deeper insights.
                </div>
            </div>
         </div>
         <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
             <button onClick={() => setShowMLSettings(!showMLSettings)} className="btn" style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                 <Settings size={16} /> ML Analysis
             </button>
             <button onClick={() => setShowDataMgmt(!showDataMgmt)} className="btn" style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                 <Download size={16} /> Data
             </button>
             <button onClick={fetchData} className="btn" disabled={loading}>
                 {loading ? 'Refreshing...' : 'Refresh Data'}
             </button>
         </div>
      </div>

      {/* ML Analysis Settings Panel */}
      {showMLSettings && (
        <div className="card" style={{ gridColumn: 'span 12', backgroundColor: 'rgba(0, 242, 255, 0.05)' }}>
          <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <BrainCircuit size={20} /> ML-Based Deep Analysis
          </h3>
          <div style={{ display: 'flex', gap: '2rem', alignItems: 'end' }}>
            <div style={{ flex: 1 }}>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem' }}>Algorithm</label>
              <select 
                value={mlAlgorithm} 
                onChange={(e) => setMlAlgorithm(e.target.value)}
                style={{ 
                  width: '100%', 
                  padding: '0.5rem', 
                  backgroundColor: 'var(--bg-card)', 
                  border: '1px solid var(--glass-border)',
                  borderRadius: '4px',
                  color: 'white'
                }}
              >
                {algorithms.map(alg => (
                  <option key={alg.id} value={alg.id}>{alg.name}</option>
                ))}
              </select>
              {algorithms.find(a => a.id === mlAlgorithm) && (
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                  {algorithms.find(a => a.id === mlAlgorithm).description}
                </div>
              )}
            </div>
            <div>
              <button 
                onClick={runMLAnalysis} 
                disabled={mlAnalyzing}
                className="btn"
                style={{ 
                  display: 'flex', 
                  gap: '0.5rem', 
                  alignItems: 'center',
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  padding: '0.75rem 1.5rem'
                }}
              >
                <Play size={16} /> {mlAnalyzing ? 'Analyzing...' : 'Run Analysis Now'}
              </button>
            </div>
          </div>
          {mlResult && (
            <div style={{ marginTop: '1rem', padding: '1rem', backgroundColor: 'rgba(0,0,0,0.3)', borderRadius: '4px' }}>
              <strong>Last Analysis Result:</strong>
              <div style={{ marginTop: '0.5rem', fontSize: '0.9rem' }}>
                {mlResult.summary}
              </div>
              <div style={{ marginTop: '0.5rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Analyzed at: {new Date(mlResult.analyzed_at).toLocaleString()}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Data Management Panel */}
      {showDataMgmt && (
        <div className="card" style={{ gridColumn: 'span 12', backgroundColor: 'rgba(255, 107, 107, 0.05)' }}>
          <h3 style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#ff6b6b' }}>
            <Download size={20} /> Data Management
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '2rem' }}>
            {/* Export Section */}
            <div style={{ padding: '1rem', backgroundColor: 'rgba(0, 242, 255, 0.1)', borderRadius: '4px', border: '1px solid rgba(0, 242, 255, 0.2)' }}>
              <h4 style={{ marginBottom: '0.5rem', color: '#00f2ff' }}>📥 Export Data</h4>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
                Download all historical monitoring data as CSV file
              </p>
              <div style={{ marginBottom: '0.5rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Data points: <strong>{historyData.length}</strong>
              </div>
              <button 
                onClick={exportToCSV}
                disabled={exportLoading || historyData.length === 0}
                className="btn"
                style={{ 
                  width: '100%',
                  display: 'flex', 
                  gap: '0.5rem', 
                  alignItems: 'center',
                  justifyContent: 'center',
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  padding: '0.75rem'
                }}
              >
                <Download size={16} /> {exportLoading ? 'Exporting...' : 'Export to CSV'}
              </button>
            </div>

            {/* Clear Section */}
            <div>
              <div style={{ padding: '1rem', backgroundColor: 'rgba(255, 107, 107, 0.1)', borderRadius: '4px', border: '1px solid rgba(255, 107, 107, 0.2)', marginBottom: '1rem' }}>
                <h4 style={{ marginBottom: '0.5rem', color: '#ff6b6b' }}>🗑️ Clear History</h4>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
                  Delete all monitoring data from memory. Resets statistical baseline.
                </p>
                <div style={{ marginBottom: '0.5rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  Data points: <strong>{historyData.length}</strong>
                </div>
                <button 
                  onClick={clearHistoryData}
                  disabled={clearLoading || historyData.length === 0}
                  className="btn"
                  style={{ 
                    width: '100%',
                    display: 'flex', 
                    gap: '0.5rem', 
                    alignItems: 'center',
                    justifyContent: 'center',
                    background: 'linear-gradient(135deg, #ff6b6b 0%, #ff4757 100%)',
                    padding: '0.75rem'
                  }}
                >
                  <Trash2 size={16} /> {clearLoading ? 'Clearing...' : 'Clear History'}
                </button>
              </div>

              <div style={{ padding: '1rem', backgroundColor: 'rgba(255, 200, 0, 0.1)', borderRadius: '4px', border: '1px solid rgba(255, 200, 0, 0.2)' }}>
                <h4 style={{ marginBottom: '0.5rem', color: 'var(--warning)' }}>🔔 Clear Event Log</h4>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
                  Clear anomaly events from memory (database records remain)
                </p>
                <div style={{ marginBottom: '0.5rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  Events: <strong>{events.length}</strong>
                </div>
                <button 
                  onClick={clearEventsData}
                  disabled={events.length === 0}
                  className="btn"
                  style={{ 
                    width: '100%',
                    display: 'flex', 
                    gap: '0.5rem', 
                    alignItems: 'center',
                    justifyContent: 'center',
                    background: 'linear-gradient(135deg, #ffa500 0%, #ff8c00 100%)',
                    padding: '0.75rem'
                  }}
                >
                  <Trash2 size={16} /> Clear Event Log
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Real-time Charts with Statistical Bands */}
      {/* Show focused anomaly panel if vibration anomaly is selected */}
      {selectedVibrationAnomaly && (
        <div className="card" style={{ gridColumn: 'span 12', backgroundColor: 'rgba(255, 107, 107, 0.1)', borderLeft: '4px solid #ff6b6b' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <div>
              <h3 style={{ color: '#ff6b6b', marginBottom: '0.5rem' }}>🔴 Vibration Anomaly Detected</h3>
              <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                <strong>Time:</strong> {new Date(selectedVibrationAnomaly.timestamp * 1000).toLocaleString()} | 
                <strong style={{ marginLeft: '1rem' }}>Type:</strong> {selectedVibrationAnomaly.anomaly.type.toUpperCase()} | 
                <strong style={{ marginLeft: '1rem' }}>Deviation:</strong> {selectedVibrationAnomaly.anomaly.deviation_sigma.toFixed(2)}σ
              </div>
            </div>
            <button 
              onClick={() => setSelectedVibrationAnomaly(null)}
              style={{ background: 'none', border: 'none', color: '#ff6b6b', cursor: 'pointer', fontSize: '1.2rem' }}
            >
              ✕
            </button>
          </div>
          <div style={{ display: 'flex', gap: '2rem' }}>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Current Value:</div>
              <div style={{ fontSize: '1.8rem', color: '#00f2ff', fontWeight: 'bold' }}>
                {selectedVibrationAnomaly.anomaly.value.toFixed(2)} mm/s
              </div>
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Normal Range:</div>
              <div style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>
                {selectedVibrationAnomaly.anomaly.threshold.toFixed(2)} {selectedVibrationAnomaly.anomaly.type === 'high' ? '(above)' : '(below)'}
              </div>
            </div>
            <div>
              <button 
                onClick={() => {
                  const evt = {
                    timestamp: selectedVibrationAnomaly.timestamp,
                    type: 'CRITICAL',
                    message: `Vibration anomaly: ${selectedVibrationAnomaly.anomaly.type} (${selectedVibrationAnomaly.anomaly.deviation_sigma.toFixed(1)}σ)`,
                    details: historyData.find(d => d.timestamp === selectedVibrationAnomaly.timestamp)
                  };
                  onDiagnose && onDiagnose(evt);
                }}
                className="btn"
                style={{ background: 'linear-gradient(135deg, #ff6b6b 0%, #ff4757 100%)' }}
              >
                🔍 Diagnose Now
              </button>
            </div>
          </div>
        </div>
      )}

      <div style={{ gridColumn: 'span 12' }}>
        <SignalChart 
            data={historyData} 
            dataKey="vibration" 
            color="#00f2ff" 
            title="Vibration History (History)" 
            unit="mm/s"
            stats={stats}
            onPointClick={(point) => {
              // Save selected vibration anomaly and also prepare for diagnosis
              setSelectedVibrationAnomaly(point);
              const evt = {
                timestamp: point.timestamp,
                type: 'WARNING',
                message: `Vibration anomaly: ${point.anomaly.type} (${point.anomaly.deviation_sigma.toFixed(1)}σ)`,
                details: historyData.find(d => d.timestamp === point.timestamp)
              };
            }}
        />
      </div>
      
      <div style={{ gridColumn: 'span 6' }}>
        <SignalChart 
            data={historyData} 
            dataKey="temperature" 
            color="#ff00cc" 
            title="Temperature History (History)" 
            unit="°C"
            stats={stats}
            onPointClick={(point) => {
              const evt = {
                timestamp: point.timestamp,
                type: 'WARNING',
                message: `Temperature anomaly: ${point.anomaly.type} (${point.anomaly.deviation_sigma.toFixed(1)}σ)`,
                details: historyData.find(d => d.timestamp === point.timestamp)
              };
              onDiagnose && onDiagnose(evt);
            }}
        />
      </div>

      <div style={{ gridColumn: 'span 6' }}>
         <SignalChart 
            data={historyData} 
            dataKey="power" 
            color="#ffc658" 
            title="Power History (History)" 
            unit="kW"
            stats={stats}
            onPointClick={(point) => {
              const evt = {
                timestamp: point.timestamp,
                type: 'WARNING',
                message: `Power anomaly: ${point.anomaly.type} (${point.anomaly.deviation_sigma.toFixed(1)}σ)`,
                details: historyData.find(d => d.timestamp === point.timestamp)
              };
              onDiagnose && onDiagnose(evt);
            }}
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
