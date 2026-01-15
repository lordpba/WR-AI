import React from 'react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, Line, ComposedChart } from 'recharts';

const formatTimestamp = (unixTime) => {
  const date = new Date(unixTime * 1000);
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);
  
  // Se è oggi, mostra l'ora
  if (date.toDateString() === today.toDateString()) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }
  // Se è ieri, mostra ieri + ora
  else if (date.toDateString() === yesterday.toDateString()) {
    return 'Ieri ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }
  // Altrimenti mostra data completa
  else {
    return date.toLocaleDateString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  }
};

export const SignalChart = ({ data, dataKey, color, title, unit, domain, stats, onPointClick }) => {
  // Get statistical bounds if available
  const statData = stats?.[dataKey];
  const showBands = statData && statData.mean !== undefined;

  // Prepare data with anomaly flag for dot rendering
  const chartData = data.map((point, index) => ({
    ...point,
    isAnomaly: point.anomalies?.[dataKey] ? true : false,
    anomalyData: point.anomalies?.[dataKey] || null
  }));

  // Count anomalies
  const anomalyCount = chartData.filter(p => p.isAnomaly).length;

  // Custom dot renderer for anomaly points
  const renderDot = (props) => {
    const { cx, cy, payload } = props;
    if (payload.isAnomaly && cx && cy) {
      return (
        <circle 
          cx={cx} 
          cy={cy} 
          r={6} 
          fill="#ff6b6b" 
          stroke="#ff0000"
          strokeWidth={2}
          style={{ cursor: 'pointer' }}
          onClick={() => {
            if (onPointClick) {
              onPointClick({
                timestamp: payload.timestamp,
                [dataKey]: payload[dataKey],
                anomaly: payload.anomalyData
              });
            }
          }}
        />
      );
    }
    return null;
  };

  return (
    <div className="card" style={{ height: '280px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
        <h3 style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>{title}</h3>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          {showBands && (
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              {statData.mean.toFixed(1)} ± {statData.std.toFixed(1)} {unit}
            </span>
          )}
          <span style={{ fontWeight: 'bold', color: color }}>
            {data.length > 0 ? data[data.length-1][dataKey].toFixed(1) : '-'} {unit}
          </span>
        </div>
      </div>
      <ResponsiveContainer width="100%" height="85%">
        <ComposedChart data={chartData} margin={{ top: 10, right: 30, bottom: 30, left: 10 }}>
          <defs>
            <linearGradient id={`gradient-${dataKey}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={color} stopOpacity={0.6}/>
              <stop offset="95%" stopColor={color} stopOpacity={0.1}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.1)" />
          <XAxis 
            dataKey="timestamp" 
            tickFormatter={formatTimestamp}
            minTickGap={60}
            angle={-35}
            textAnchor="end"
            height={50}
            tick={{ fontSize: 11, fill: 'var(--text-muted)' }}
          />
          <YAxis 
            domain={domain || ['dataMin - 1', 'dataMax + 1']} 
            tick={{ fontSize: 10, fill: 'var(--text-muted)' }}
            width={40}
            tickFormatter={(value) => value.toFixed(1)}
          />
          <Tooltip 
            contentStyle={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--glass-border)', borderRadius: '8px' }}
            itemStyle={{ color: color }}
            formatter={(value, name) => {
              if (name === dataKey) {
                return [value.toFixed(2) + ' ' + unit, title.replace(' (History)', '')];
              }
              return [value, name];
            }}
            labelFormatter={(timestamp) => new Date(timestamp * 1000).toLocaleString()}
          />
          
          {/* Statistical reference lines */}
          {showBands && (
            <>
              <ReferenceLine 
                y={statData.mean} 
                stroke={color} 
                strokeDasharray="5 5" 
                strokeOpacity={0.7}
                strokeWidth={1.5}
              />
              <ReferenceLine 
                y={statData.upper_bound} 
                stroke="#ff6b6b" 
                strokeDasharray="3 3" 
                strokeOpacity={0.5}
                strokeWidth={1}
              />
              <ReferenceLine 
                y={statData.lower_bound} 
                stroke="#ff6b6b" 
                strokeDasharray="3 3" 
                strokeOpacity={0.5}
                strokeWidth={1}
              />
            </>
          )}
          
          {/* Main signal area */}
          <Area 
            type="monotone" 
            dataKey={dataKey} 
            stroke={color} 
            strokeWidth={2}
            fillOpacity={1} 
            fill={`url(#gradient-${dataKey})`} 
            isAnimationActive={false}
            dot={renderDot}
            activeDot={{ r: 4, fill: color }}
          />
        </ComposedChart>
      </ResponsiveContainer>
      {/* Stats and anomaly info */}
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', marginTop: '0.25rem' }}>
        {showBands && (
          <span style={{ color: 'var(--text-muted)' }}>
            Range: {statData.lower_bound.toFixed(1)} - {statData.upper_bound.toFixed(1)} {unit}
          </span>
        )}
        {anomalyCount > 0 && (
          <span style={{ color: '#ff6b6b' }}>
            {anomalyCount} anomal{anomalyCount > 1 ? 'ies' : 'y'} detected (click red points to diagnose)
          </span>
        )}
      </div>
    </div>
  );
};
