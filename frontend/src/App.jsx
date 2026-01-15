import React, { useEffect, useState } from 'react';
import { Activity, Zap, Box, AlertTriangle, Settings, RefreshCw, LayoutDashboard, BrainCircuit, MessageSquareText } from 'lucide-react';
import { Dashboard } from './modules/foundation/Dashboard';
import { AnomalyDashboard } from './modules/anomaly_detection/AnomalyDashboard';
import { DiagnosisDashboard } from './modules/guided_diagnosis/DiagnosisDashboard';

function App() {
  const [activeModule, setActiveModule] = useState('foundation');
  const [status, setStatus] = useState(null);
  const [history, setHistory] = useState([]);
  const [pareto, setPareto] = useState([]);
  const [connected, setConnected] = useState(false);
  
  // Cross-module state
  const [selectedAnomaly, setSelectedAnomaly] = useState(null);

  const handleStartDiagnosis = (anomaly) => {
      setSelectedAnomaly(anomaly);
      setActiveModule('diagnosis');
  };

  const fetchData = async () => {
    try {
      // Always fetch status for the header
      const statusRes = await fetch('http://localhost:8000/api/status');
      const statusData = await statusRes.json();
      setStatus(statusData);
      setConnected(true);

      // Only fetch heavy dashboard data if we are on the foundation tab
      if (activeModule === 'foundation') {
          const [metricsRes, paretoRes] = await Promise.all([
            fetch('http://localhost:8000/api/metrics'),
            fetch('http://localhost:8000/api/pareto')
          ]);
          const metricsData = await metricsRes.json();
          const paretoData = await paretoRes.json();
          setHistory(metricsData.history);
          setPareto(paretoData);
      }
    } catch (e) {
      console.error("Connection failed", e);
      setConnected(false);
    }
  };

  useEffect(() => {
    // Poll every 1 second
    fetchData(); // Fetch immediately
    const interval = setInterval(fetchData, 1000);
    return () => clearInterval(interval);
  }, [activeModule]); // Re-fetch when module changes

  if (!status) return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', color: 'white' }}>
      <div>Waiting for Backend...</div>
    </div>
  );

  return (
    <div className="app">
      {/* Header */}
      <header style={{
        padding: '0 2rem',
        height: '80px',
        borderBottom: 'var(--glass-border)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: 'rgba(15, 17, 21, 0.95)',
        backdropFilter: 'blur(10px)',
        position: 'sticky',
        top: 0,
        zIndex: 10
      }}>
        {/* Left: Logo & Machine Info */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
            <div style={{ fontWeight: '900', fontSize: '1.5rem', letterSpacing: '-1px' }}>
                WR<span style={{ color: 'var(--primary)' }}>-AI</span>
            </div>
            
            {/* Module Navigation */}
            <nav style={{ display: 'flex', gap: '0.5rem', background: 'rgba(255,255,255,0.03)', padding: '0.25rem', borderRadius: '8px' }}>
                <button 
                    onClick={() => setActiveModule('foundation')}
                    style={{ 
                        display: 'flex', alignItems: 'center', gap: '0.5rem',
                        padding: '0.5rem 1rem', 
                        borderRadius: '6px', 
                        border: 'none', 
                        background: activeModule === 'foundation' ? 'var(--primary)' : 'transparent',
                        color: activeModule === 'foundation' ? 'white' : 'var(--text-muted)',
                        cursor: 'pointer',
                        fontWeight: '500',
                        transition: 'all 0.2s'
                    }}
                >
                    <LayoutDashboard size={16} />
                    Foundation
                </button>
                <button 
                    onClick={() => setActiveModule('anomaly')}
                    style={{ 
                        display: 'flex', alignItems: 'center', gap: '0.5rem',
                        padding: '0.5rem 1rem', 
                        borderRadius: '6px', 
                        border: 'none', 
                        background: activeModule === 'anomaly' ? 'var(--primary)' : 'transparent',
                        color: activeModule === 'anomaly' ? 'white' : 'var(--text-muted)',
                        cursor: 'pointer',
                        fontWeight: '500',
                        transition: 'all 0.2s'
                    }}
                >
                    <BrainCircuit size={16} />
                    Anomaly Detection
                </button>

                <button 
                    onClick={() => setActiveModule('diagnosis')}
                    style={{
                        background: activeModule === 'diagnosis' ? 'rgba(255,255,255,0.1)' : 'transparent',
                        border: 'none',
                        padding: '0.5rem 1rem',
                        borderRadius: '6px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        color: activeModule === 'diagnosis' ? 'white' : 'var(--text-muted)',
                        cursor: 'pointer',
                        fontWeight: '500',
                        transition: 'all 0.2s'
                    }}
                >
                    <MessageSquareText size={16} />
                    Guided Diagnosis
                </button>
            </nav>
        </div>

        {/* Right: Status */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          <div style={{
            padding: '0.25rem 0.75rem',
            borderRadius: '20px',
            background: 'var(--bg-card)',
            fontSize: '0.8rem',
            border: '1px solid rgba(255,255,255,0.05)'
          }}>
            LINE 01 • {status.recipe}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div className={`status-indicator ${status.state.toLowerCase()}`} />
            <span style={{ fontWeight: 'bold' }}>{status.state}</span>
          </div>
          <div style={{ color: 'var(--text-muted)' }}>{new Date(status.timestamp).toLocaleTimeString()}</div>
        </div>
      </header>

      {/* Main Content Area */}
      {activeModule === 'foundation' && (
          <Dashboard status={status} history={history} pareto={pareto} />
      )}
      
      {activeModule === 'anomaly' && (
          <AnomalyDashboard onDiagnose={handleStartDiagnosis} />
      )}

      {activeModule === 'diagnosis' && (
          <DiagnosisDashboard initialAnomaly={selectedAnomaly} />
      )}
      
    </div>
  );
}

export default App;
