import React from 'react';

export const OEEGauge = ({ value }) => {
    const radius = 80;
    const stroke = 12;
    const normalizedValue = Math.min(Math.max(value, 0), 100);
    const circumference = normalizedValue / 100 * (2 * Math.PI * radius);
    const fullCircumference = 2 * Math.PI * radius;

    // Color based on value
    let color = 'var(--danger)';
    if (value > 65) color = 'var(--warning)';
    if (value > 85) color = 'var(--success)';

    return (
        <div className="card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gridColumn: 'span 3' }}>
            <h3 style={{ marginBottom: '1rem', color: 'var(--text-muted)' }}>OEE</h3>
            <div style={{ position: 'relative', width: 200, height: 200 }}>
                {/* Background Circle */}
                <svg width="200" height="200" style={{ transform: 'rotate(-90deg)' }}>
                    <circle
                        cx="100"
                        cy="100"
                        r={radius}
                        stroke="rgba(255,255,255,0.1)"
                        strokeWidth={stroke}
                        fill="transparent"
                    />
                    {/* Progress Circle */}
                    <circle
                        cx="100"
                        cy="100"
                        r={radius}
                        stroke={color}
                        strokeWidth={stroke}
                        fill="transparent"
                        strokeDasharray={`${circumference} ${fullCircumference}`}
                        strokeLinecap="round"
                        style={{ transition: 'stroke-dasharray 0.5s ease, stroke 0.5s ease' }}
                    />
                </svg>
                <div style={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    textAlign: 'center'
                }}>
                    <div style={{ fontSize: '2.5rem', fontWeight: 'bold' }}>{Math.round(value)}%</div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Efficiency</div>
                </div>
            </div>
        </div>
    );
};
