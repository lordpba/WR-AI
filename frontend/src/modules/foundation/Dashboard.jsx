import React from 'react';
import { Activity, Zap, Box, AlertTriangle } from 'lucide-react';
import { KPIWidget } from '../../components/KPIWidget';
import { OEEGauge } from '../../components/OEEGauge';
import { EnergyChart } from '../../components/EnergyChart';
import { SignalChart } from '../anomaly_detection/SignalChart';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

export function Dashboard({ status, history, pareto, stream }) {
  if (!status) return <div>Loading Dashboard...</div>;

  return (
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

      {/* Row 3: Real-time Signal Monitoring */}
      <h3 style={{ gridColumn: 'span 12', marginTop: '1rem', marginBottom: '0.5rem' }}>Real-time Signal Monitoring</h3>
      
      <div style={{ gridColumn: 'span 6' }}>
        <SignalChart 
            title="Vibration (Real-time)" 
            data={stream || []} 
            dataKey="vibration" 
            color="#00f2ff" 
            unit="mm/s" 
            domain={[0, 5]}
        />
      </div>

      <div style={{ gridColumn: 'span 6' }}>
        <SignalChart 
            title="Temperature (Real-time)" 
            data={stream || []} 
            dataKey="temperature" 
            color="#ff00cc" 
            unit="°C" 
            domain={[20, 100]}
        />
      </div>
    </main>
  );
}
