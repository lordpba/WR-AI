import React, { useEffect, useState } from 'react';
import { RefreshCw, Save } from 'lucide-react';

export function SettingsPage() {
  const [config, setConfig] = useState({
    llm_provider: 'ollama',
    ollama_base_url: 'http://localhost:11434',
    ollama_model: 'llama3.1:latest',
    gemini_api_key: '',
    gemini_model: 'gemini-1.5-pro'
  });
  const [acq, setAcq] = useState({
    source_type: 'none',
    poll_interval_s: 1.0,
    modbus_host: '',
    modbus_port: 502,
    modbus_unit_id: 1,
    modbus_reg_map_json: ''
  });
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  const loadConfig = async () => {
    try {
      setLoading(true);
      const [res, acqRes] = await Promise.all([
        fetch('http://localhost:8000/api/llm/config'),
        fetch('http://localhost:8000/api/realtime/config')
      ]);
      const data = await res.json();
      const acqData = await acqRes.json();
      setConfig({
        llm_provider: data.llm_provider || 'ollama',
        ollama_base_url: data.ollama_base_url || 'http://localhost:11434',
        ollama_model: data.ollama_model || 'llama3.1:latest',
        gemini_api_key: data.gemini_api_key || '',
        gemini_model: data.gemini_model || 'gemini-1.5-pro'
      });
      setAcq({
        source_type: acqData.source_type || 'none',
        poll_interval_s: acqData.poll_interval_s ?? 1.0,
        modbus_host: acqData.modbus_host || '',
        modbus_port: acqData.modbus_port ?? 502,
        modbus_unit_id: acqData.modbus_unit_id ?? 1,
        modbus_reg_map_json: acqData.modbus_reg_map_json || ''
      });
    } catch (e) {
      console.error('Failed to load config', e);
    } finally {
      setLoading(false);
    }
  };

  const refreshModels = async () => {
    try {
      setLoading(true);
      const res = await fetch(`http://localhost:8000/api/llm/ollama/models?base_url=${encodeURIComponent(config.ollama_base_url)}`);
      const data = await res.json();
      setModels(data.models || []);
    } catch (e) {
      console.error('Failed to fetch models', e);
      setModels([]);
    } finally {
      setLoading(false);
    }
  };

  const saveConfig = async () => {
    try {
      setSaving(true);
      const [res, acqRes] = await Promise.all([
        fetch('http://localhost:8000/api/llm/config', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(config)
        }),
        fetch('http://localhost:8000/api/realtime/config', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(acq)
        })
      ]);
      const data = await res.json();
      const acqData = await acqRes.json();
      if (!res.ok) {
        alert(`Save failed: ${data.detail || 'Unknown error'}`);
        return;
      }
      if (!acqRes.ok) {
        alert(`Save acquisition failed: ${acqData.detail || 'Unknown error'}`);
        return;
      }
      alert('✅ Saved');
      await refreshModels();
    } catch (e) {
      console.error('Failed to save config', e);
      alert('Save failed. Check console.');
    } finally {
      setSaving(false);
    }
  };

  useEffect(() => {
    loadConfig();
    refreshModels();
  }, []);

  return (
    <main className="dashboard-grid">
      <div className="card" style={{ gridColumn: 'span 12', maxWidth: 900, margin: '0 auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <div>
            <strong>Settings</strong>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Shared backend configuration (Ollama remote + model selection)
            </div>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button className="btn" onClick={refreshModels} disabled={loading}>
              <RefreshCw size={16} /> Refresh models
            </button>
            <button className="btn" onClick={saveConfig} disabled={saving}>
              <Save size={16} /> {saving ? 'Saving...' : 'Save'}
            </button>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          <div className="form-group">
            <label>LLM provider</label>
            <select
              className="form-control"
              value={config.llm_provider}
              onChange={(e) => setConfig({ ...config, llm_provider: e.target.value })}
            >
              <option value="ollama">Ollama</option>
              <option value="gemini">Gemini</option>
            </select>
          </div>
          <div />

          {config.llm_provider === 'ollama' && (
            <>
              <div className="form-group">
                <label>Ollama base URL</label>
                <input
                  className="form-control"
                  value={config.ollama_base_url}
                  onChange={(e) => setConfig({ ...config, ollama_base_url: e.target.value })}
                  placeholder="http://192.168.1.10:11434"
                />
              </div>

              <div className="form-group">
                <label>Ollama model</label>
                <select
                  className="form-control"
                  value={config.ollama_model}
                  onChange={(e) => setConfig({ ...config, ollama_model: e.target.value })}
                >
                  {models.length === 0 ? (
                    <option value={config.ollama_model}>{config.ollama_model}</option>
                  ) : (
                    models.map((m) => (
                      <option key={m} value={m}>{m}</option>
                    ))
                  )}
                </select>
                {models.length === 0 && (
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                    No models found. Set Ollama URL and click “Refresh models”.
                  </div>
                )}
              </div>
            </>
          )}

          {config.llm_provider === 'gemini' && (
            <>
              <div className="form-group">
                <label>Gemini API key</label>
                <input
                  className="form-control"
                  type="password"
                  value={config.gemini_api_key}
                  onChange={(e) => setConfig({ ...config, gemini_api_key: e.target.value })}
                  placeholder="AIza..."
                />
              </div>

              <div className="form-group">
                <label>Gemini model</label>
                <select
                  className="form-control"
                  value={config.gemini_model}
                  onChange={(e) => setConfig({ ...config, gemini_model: e.target.value })}
                >
                  <option value="gemini-1.5-pro">gemini-1.5-pro</option>
                  <option value="gemini-1.5-flash">gemini-1.5-flash</option>
                  <option value="gemini-2.0-flash">gemini-2.0-flash</option>
                </select>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                  Model list is preset; we can refine it later.
                </div>
              </div>
            </>
          )}
        </div>

        <div style={{ marginTop: '2rem', borderTop: '1px solid rgba(255,255,255,0.08)', paddingTop: '1.5rem' }}>
          <strong>Data acquisition</strong>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
            Prepared settings for when the PLC/data source will be connected.
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label>Source type</label>
              <select
                className="form-control"
                value={acq.source_type}
                onChange={(e) => setAcq({ ...acq, source_type: e.target.value })}
              >
                <option value="none">None / Waiting device</option>
                <option value="modbus_tcp">Modbus TCP (future)</option>
                <option value="serial_raw">Serial raw (future)</option>
              </select>
            </div>
            <div className="form-group">
              <label>Poll interval (s)</label>
              <input
                className="form-control"
                type="number"
                step="0.1"
                value={acq.poll_interval_s}
                onChange={(e) => setAcq({ ...acq, poll_interval_s: Number(e.target.value) })}
              />
            </div>

            <div className="form-group">
              <label>Modbus host (TCP)</label>
              <input
                className="form-control"
                value={acq.modbus_host}
                onChange={(e) => setAcq({ ...acq, modbus_host: e.target.value })}
                placeholder="192.168.1.50"
              />
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div className="form-group">
                <label>Port</label>
                <input
                  className="form-control"
                  type="number"
                  value={acq.modbus_port}
                  onChange={(e) => setAcq({ ...acq, modbus_port: Number(e.target.value) })}
                />
              </div>
              <div className="form-group">
                <label>Unit ID</label>
                <input
                  className="form-control"
                  type="number"
                  value={acq.modbus_unit_id}
                  onChange={(e) => setAcq({ ...acq, modbus_unit_id: Number(e.target.value) })}
                />
              </div>
            </div>

            <div className="form-group" style={{ gridColumn: 'span 2' }}>
              <label>Modbus register map (JSON)</label>
              <textarea
                className="form-control"
                rows={4}
                value={acq.modbus_reg_map_json}
                onChange={(e) => setAcq({ ...acq, modbus_reg_map_json: e.target.value })}
                placeholder='[{"name":"voltage_v","address":0,"count":1,"scale":0.1}]'
              />
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}

