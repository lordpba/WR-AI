import React from 'react';

export const KPIWidget = ({ title, value, unit, icon: Icon, trend }) => {
  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem', textTransform: 'uppercase', letterSpacing: '1px' }}>{title}</span>
        {Icon && <Icon size={20} color="var(--primary)" />}
      </div>
      <div style={{ fontSize: '2rem', fontWeight: 'bold' }}>
        {value} <span style={{ fontSize: '1rem', color: 'var(--text-muted)' }}>{unit}</span>
      </div>
      {trend && (
        <div style={{ fontSize: '0.8rem', color: trend > 0 ? 'var(--success)' : 'var(--danger)', marginTop: '0.5rem' }}>
          {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}% vs last hr
        </div>
      )}
    </div>
  );
};
