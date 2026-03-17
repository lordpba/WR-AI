import React, { useState, useEffect, useRef } from 'react';
import { MessageSquare, FileText, Send, Save, Loader } from 'lucide-react';

export function DiagnosisDashboard({ initialAnomaly }) {
  const [activeTab, setActiveTab] = useState('chat');
  const [provider, setProvider] = useState('ollama');

  // Manual State
  const [manualText, setManualText] = useState('');
  const [manualLoading, setManualLoading] = useState(false);

  // Chat State
  const [query, setQuery] = useState('');
  const [chatHistory, setChatHistory] = useState([
    { role: 'system', content: 'Hello. I am your AI Diagnostic Assistant. How can I help you today?' }
  ]);
  const [analyzing, setAnalyzing] = useState(false);
  const [currentAnomaly, setCurrentAnomaly] = useState(null);
  
  // Use ref to track if we're already processing to prevent double execution in React StrictMode
  const isProcessingRef = useRef(false);
  const processedAnomalyIdRef = useRef(null);

  // Fetch Manual on load
  useEffect(() => {
    fetchManual();
    fetchProvider();
  }, []);

  // Handle initial anomaly separately to avoid duplicates
  useEffect(() => {
    if (initialAnomaly) {
        const anomalyId = `${initialAnomaly.timestamp}-${initialAnomaly.type}`;
        
        // Only process if it's a new anomaly and we're not already processing
        if (anomalyId !== processedAnomalyIdRef.current && !isProcessingRef.current) {
            isProcessingRef.current = true;
            processedAnomalyIdRef.current = anomalyId;
            
            setCurrentAnomaly(initialAnomaly);
            // Reset chat and auto-diagnose
            setChatHistory([
                { role: 'system', content: 'Hello. I am your AI Diagnostic Assistant. How can I help you today?' }
            ]);
            handleAutoDiagnose(initialAnomaly);
        }
    } else if (!isProcessingRef.current) {
        fetchLatestAnomaly();
    }
  }, [initialAnomaly]);

  const handleAutoDiagnose = async (anomaly) => {
      const autoQuery = "Analyze the detected anomaly and suggest immediate actions based on the manual.";
      const userMsg = { role: 'user', content: autoQuery };
      setChatHistory(prev => [...prev, userMsg]);
      setAnalyzing(true);
      
      try {
          const payload = {
              query: autoQuery,
              provider: provider,
              config: {},
              anomaly_context: anomaly
          };
  
          const res = await fetch('http://localhost:8000/api/diagnosis/analyze', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(payload)
          });
          
          const data = await res.json();
          if (data.error) {
              setChatHistory(prev => [...prev, { role: 'system', content: `Error: ${data.error}` }]);
          } else {
              setChatHistory(prev => [...prev, { role: 'assistant', content: data.response }]);
          }
      } catch (e) {
          setChatHistory(prev => [...prev, { role: 'system', content: "Failed to communicate with diagnosis service." }]);
      } finally {
          setAnalyzing(false);
          // Reset processing flag after completion
          isProcessingRef.current = false;
      }
  }

  const fetchManual = async () => {
    try {
      setManualLoading(true);
      const res = await fetch('http://localhost:8000/api/diagnosis/manual');
      const data = await res.json();
      setManualText(data.text);
    } catch (e) {
      console.error("Failed to fetch manual", e);
    } finally {
      setManualLoading(false);
    }
  };

  const fetchProvider = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/llm/config');
      const data = await res.json();
      setProvider(data.llm_provider || 'ollama');
    } catch (e) {
      // ignore; keep default
    }
  };

  const fetchLatestAnomaly = async () => {
    try {
        const res = await fetch('http://localhost:8000/api/anomaly/events');
        const data = await res.json();
        if (data && data.length > 0) {
            // Pick the most recent unassigned or just the last one
            setCurrentAnomaly(data[0]); // assuming sorted desc
        }
    } catch (e) {
        console.error("Failed to fetch anomalies", e);
    }
  }

  const saveManual = async () => {
    try {
      await fetch('http://localhost:8000/api/diagnosis/manual', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: manualText })
      });
      alert('Manual updated successfully!');
    } catch (e) {
      alert('Failed to save manual');
    }
  };

  const handleDiagnose = async () => {
    if (!query) return;

    const userMsg = { role: 'user', content: query };
    setChatHistory(prev => [...prev, userMsg]);
    setQuery('');
    setAnalyzing(true);

    try {
      const payload = {
        query: userMsg.content,
        provider: provider,
        config: {},
        anomaly_context: currentAnomaly
      };

      const res = await fetch('http://localhost:8000/api/diagnosis/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      const data = await res.json();
      if (data.error) {
          setChatHistory(prev => [...prev, { role: 'system', content: `Error: ${data.error}` }]);
      } else {
          setChatHistory(prev => [...prev, { role: 'assistant', content: data.response }]);
      }
    } catch (e) {
      setChatHistory(prev => [...prev, { role: 'system', content: "Failed to communicate with diagnosis service." }]);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="dashboard-grid" style={{ display: 'flex', flexDirection: 'column', height: '100%', gap: '1rem' }}>
      
      {/* Navigation Tabs */}
      <div className="card" style={{ display: 'flex', gap: '1rem', padding: '1rem' }}>
        <button 
          className={`btn ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => setActiveTab('chat')}
          style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '0.5rem', 
            background: activeTab === 'chat' ? 'var(--primary)' : 'rgba(255,255,255,0.05)',
            color: activeTab === 'chat' ? 'white' : 'var(--text-muted)',
            border: activeTab === 'chat' ? 'none' : '1px solid rgba(255,255,255,0.1)',
            padding: '0.5rem 1rem',
            borderRadius: '6px',
            cursor: 'pointer',
            transition: 'all 0.2s'
          }}
        >
          <MessageSquare size={18} /> Diagnosis Chat
        </button>
        <button 
          className={`btn ${activeTab === 'manual' ? 'active' : ''}`}
          onClick={() => setActiveTab('manual')}
          style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '0.5rem', 
            background: activeTab === 'manual' ? 'var(--primary)' : 'rgba(255,255,255,0.05)',
            color: activeTab === 'manual' ? 'white' : 'var(--text-muted)',
            border: activeTab === 'manual' ? 'none' : '1px solid rgba(255,255,255,0.1)',
            padding: '0.5rem 1rem',
            borderRadius: '6px',
            cursor: 'pointer',
            transition: 'all 0.2s'
          }}
        >
          <FileText size={18} /> Machine Manual
        </button>
      </div>

      {/* Main Content Area */}
      <div className="card" style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
        
        {/* CHAT TAB */}
        {activeTab === 'chat' && (
          <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
             <div style={{ flex: 1, overflowY: 'auto', padding: '1rem' }}>
                {currentAnomaly && (
                    <div style={{ marginBottom: '1rem', padding: '1rem', background: 'rgba(255,100,0,0.1)', borderLeft: '4px solid var(--warning)', borderRadius: '4px' }}>
                        <div style={{ fontWeight: 'bold', marginBottom: '0.5rem', display: 'flex', justifyContent: 'space-between' }}>
                            <span>⚠️ Analysis Context: Active Anomaly</span>
                            <span style={{ fontSize: '0.8rem', opacity: 0.7 }}>{new Date(currentAnomaly.timestamp * 1000).toLocaleString()}</span>
                        </div>
                        <div style={{ display: 'grid', gridTemplateColumns: 'auto 1fr', gap: '0.5rem 1rem', fontSize: '0.9rem' }}>
                            <span style={{ opacity: 0.7 }}>Message:</span>
                            <span>{currentAnomaly.message || currentAnomaly.description || 'N/A'}</span>
                            
                            <span style={{ opacity: 0.7 }}>Severity:</span>
                            <span style={{ 
                                color: currentAnomaly.type === 'CRITICAL' ? 'var(--danger)' : 'var(--warning)',
                                fontWeight: 'bold'
                            }}>{currentAnomaly.type || currentAnomaly.severity || 'N/A'}</span>
                            
                            <span style={{ opacity: 0.7 }}>Metrics:</span>
                            <span>
                                {currentAnomaly.details?.vibration ? `Vibration: ${currentAnomaly.details.vibration.toFixed(4)} mm/s` : (currentAnomaly.value || 'N/A')}
                            </span>
                        </div>
                    </div>
                )}
                {chatHistory.map((msg, idx) => (
                  <div key={idx} style={{ 
                    marginBottom: '1rem', 
                    textAlign: msg.role === 'user' ? 'right' : 'left' 
                  }}>
                    <div style={{ 
                      display: 'inline-block',
                      padding: '0.8rem',
                      borderRadius: '8px',
                      background: msg.role === 'user' ? 'var(--primary)' : 'var(--bg-secondary)',
                      maxWidth: '80%'
                    }}>
                      <strong>{msg.role === 'user' ? 'Operator' : 'AI Assistant'}:</strong>
                      <div style={{ whiteSpace: 'pre-wrap', marginTop: '0.4rem' }}>{msg.content}</div>
                    </div>
                  </div>
                ))}
                {analyzing && <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '1rem' }}><Loader className="spin" /> Analyzing...</div>}
             </div>
             
             <div style={{ padding: '1rem', borderTop: '1px solid var(--border)', display: 'flex', gap: '1rem' }}>
               <input 
                 type="text" 
                 value={query}
                 onChange={(e) => setQuery(e.target.value)}
                 onKeyDown={(e) => e.key === 'Enter' && handleDiagnose()}
                 placeholder="Describe the problem or ask for diagnosis..."
                 className="form-control"
                 style={{ flex: 1 }}
               />
               <button onClick={handleDiagnose} disabled={analyzing} className="btn primary">
                 <Send size={18} />
               </button>
             </div>
          </div>
        )}

        {/* MANUAL TAB */}
        {activeTab === 'manual' && (
          <div style={{ display: 'flex', flexDirection: 'column', height: '100%', padding: '1rem' }}>
            <div style={{ marginBottom: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3>Machine Manual Context</h3>
              <button onClick={saveManual} className="btn primary"><Save size={18} /> Save Changes</button>
            </div>
            {manualLoading ? <Loader className="spin" /> : (
                <textarea 
                  value={manualText}
                  onChange={(e) => setManualText(e.target.value)}
                  style={{ flex: 1, background: 'var(--bg-secondary)', color: 'var(--text-primary)', border: '1px solid var(--border)', borderRadius: '4px', padding: '1rem', fontFamily: 'monospace' }}
                />
            )}
          </div>
        )}

      </div>
    </div>
  );
}
