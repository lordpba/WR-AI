import React, { useEffect, useState } from 'react';
import { Activity, Zap, Box, AlertTriangle, Settings, RefreshCw } from 'lucide-react';
import { KPIWidget } from './components/KPIWidget';
import { OEEGauge } from './components/OEEGauge';
import { EnergyChart } from './components/EnergyChart';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

function App() {
  const [status, setStatus] = useState(null);
  const [history, setHistory] = useState([]);
  const [pareto, setPareto] = useState([]);
  const [connected, setConnected] = useState(false);

  const fetchData = async () => {
    try {
      const [statusRes, metricsRes, paretoRes] = await Promise.all([
        fetch('http://localhost:8000/api/status'),
        fetch('http://localhost:8000/api/metrics'),
        fetch('http://localhost:8000/api/pareto')
      ]);

      const statusData = await statusRes.json();
      const metricsData = await metricsRes.json();
      const paretoData = await paretoRes.json();

      setStatus(statusData);
      setHistory(metricsData.history);
      setPareto(paretoData);
      setConnected(true);
    } catch (e) {
      console.error("Connection failed", e);
      setConnected(false);
    }
  };

  useEffect(() => {
    // Poll every 1 second
    const interval = setInterval(fetchData, 1000);
    return () => clearInterval(interval);
  }, []);

  if (!status) return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
      <div>Waiting for Backend...</div>
    </div>
  );

  return (
    <div className="app">
      {/* Header */}
      <header style={{
        padding: '1.5rem 2rem',
        borderBottom: 'var(--glass-border)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: 'rgba(15, 17, 21, 0.8)',
        backdropFilter: 'blur(10px)',
        position: 'sticky',
        top: 0,
        zIndex: 10
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ fontWeight: '900', fontSize: '1.5rem', letterSpacing: '-1px' }}>
            WR<span style={{ color: 'var(--primary)' }}>-AI</span>
          </div>
          <div style={{
            padding: '0.25rem 0.75rem',
            borderRadius: '20px',
            background: 'var(--bg-card)',
            fontSize: '0.8rem',
            border: '1px solid rgba(255,255,255,0.05)'
          }}>
            LINE 01 • {status.recipe}
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div className={`status-indicator ${status.state.toLowerCase()}`} />
            <span style={{ fontWeight: 'bold' }}>{status.state}</span>
          </div>
          <div style={{ color: 'var(--text-muted)' }}>{new Date(status.timestamp).toLocaleTimeString()}</div>
        </div>
      </header>

      {/* Main Dashboard */}
      <main className="dashboard-grid">

        {/* Row 1: KPI Widgets (Span 3 each) */}
        <div style={{ gridColumn: 'span 3' }}>
          <KPIWidget
            title="Current Speed"
            value={status.speed}
            unit="pcs/min"
            icon={Activity}
          />
        </div>
        <div style={{ gridColumn: 'span 3' }}>
          <KPIWidget
            title="Production"
            value={status.produced}
            unit="pcs"
            icon={Box}
          />
        </div>
        <div style={{ gridColumn: 'span 3' }}>
          <KPIWidget
            title="Scrap"
            value={status.scrap}
            unit="pcs"
            icon={AlertTriangle}
          />
        </div>
        <div style={{ gridColumn: 'span 3' }}>
          <KPIWidget
            title="Total Energy"
            value={status.energy_kwh}
            unit="kWh"
            icon={Zap}
          />
        </div>

        {/* Row 2: OEE Gauge (3) + Energy Chart (6) + Pareto (3) */}
        <OEEGauge value={status.oee_percent} />

        <EnergyChart data={history} />

        {/* Pareto Chart Widget */}
        <div className="card" style={{ gridColumn: 'span 3', height: '350px' }}>
          <h3 style={{ marginBottom: '1rem', color: 'var(--text-muted)' }}>Top Stop Causes</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={pareto} layout="vertical" margin={{ left: 40 }}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="rgba(255,255,255,0.1)" />
              <XAxis type="number" hide />
              <YAxis dataKey="reason" type="category" width={80} tick={{ fontSize: 10, fill: '#fff' }} />
              <Tooltip cursor={{ fill: 'rgba(255,255,255,0.05)' }} contentStyle={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--glass-border)' }} />
              <Bar dataKey="duration_min" fill="var(--warning)" radius={[0, 4, 4, 0]}>
                {pareto.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={index === 0 ? 'var(--danger)' : 'var(--warning)'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

      </main>
    </div>
  );
}

export default App;
