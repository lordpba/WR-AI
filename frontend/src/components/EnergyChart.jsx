import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export const EnergyChart = ({ data }) => {
    return (
        <div className="card" style={{ gridColumn: 'span 6', height: '350px' }}>
            <h3 style={{ marginBottom: '1rem', color: 'var(--text-muted)' }}>Real-time Power Consumption (kW)</h3>
            <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data}>
                    <defs>
                        <linearGradient id="colorPower" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.8} />
                            <stop offset="95%" stopColor="var(--primary)" stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
                    <XAxis
                        dataKey="timestamp"
                        tickFormatter={(str) => new Date(str).toLocaleTimeString([], { minute: '2-digit', second: '2-digit' })}
                        stroke="var(--text-muted)"
                        tick={{ fontSize: 12 }}
                    />
                    <YAxis stroke="var(--text-muted)" tick={{ fontSize: 12 }} />
                    <Tooltip
                        contentStyle={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--glass-border)', color: '#fff' }}
                        labelFormatter={(label) => new Date(label).toLocaleTimeString()}
                    />
                    <Area type="monotone" dataKey="power" stroke="var(--primary)" fillOpacity={1} fill="url(#colorPower)" isAnimationActive={false} />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
};
