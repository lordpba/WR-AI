import React from 'react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';

export const SignalChart = ({ data, dataKey, color, title, unit, domain }) => {
  return (
    <div className="card" style={{ height: '240px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
        <h3 style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>{title}</h3>
        <span style={{ fontWeight: 'bold', color: color }}>
          {data.length > 0 ? data[data.length-1][dataKey] : '-'} {unit}
        </span>
      </div>
      <ResponsiveContainer width="100%" height="80%">
        <AreaChart data={data}>
          <defs>
            <linearGradient id={`color-${dataKey}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={color} stopOpacity={0.8}/>
              <stop offset="95%" stopColor={color} stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
          <XAxis dataKey="timestamp" hide />
          <YAxis domain={domain || ['auto', 'auto']} hide />
          <Tooltip 
            contentStyle={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--glass-border)' }}
            itemStyle={{ color: color }}
            labelStyle={{ display: 'none' }}
          />
          <Area 
            type="monotone" 
            dataKey={dataKey} 
            stroke={color} 
            fillOpacity={1} 
            fill={`url(#color-${dataKey})`} 
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};
