import React, { useState } from 'react'

export default function StartScan({ onStarted }) {
    const [target, setTarget] = useState('')
    const [uuid, setUuid] = useState('')
    const [loading, setLoading] = useState(false)
    const [msg, setMsg] = useState('')

    async function submit() {
        if (!target || !uuid) { setMsg('Enter target and template UUID'); return }
        setLoading(true); setMsg('')
        const r = await fetch('/api/scan/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ target, template_uuid: uuid, name: `Scan ${target}` })
        })
        const j = await r.json()
        setLoading(false)
        if (j.ok) { setMsg(`Scan started (DB id ${j.scan_db_id})`); onStarted?.() }
        else { setMsg('Failed to start scan') }
    }

    return (
        <>
            <h3 style={{ margin: '0 0 12px' }}>Start Nessus Scan</h3>
            <div style={{ display: 'grid', gap: 10 }}>
                <label>
                    <div style={{ opacity: .8, fontSize: 13, marginBottom: 4 }}>Target(s)</div>
                    <input value={target} onChange={e => setTarget(e.target.value)}
                        placeholder="192.168.1.0/24 or host.com"
                        style={inp} />
                </label>
                <label>
                    <div style={{ opacity: .8, fontSize: 13, marginBottom: 4 }}>Nessus Template UUID</div>
                    <input value={uuid} onChange={e => setUuid(e.target.value)} placeholder="e.g. basic network scan UUID" style={inp} />
                </label>
                <button onClick={submit} disabled={loading}
                    style={{ padding: '10px 14px', borderRadius: 10, border: '1px solid #1f2a37', background: '#111827', color: '#e6edf3', cursor: 'pointer' }}>
                    {loading ? 'Starting…' : 'Start Scan'}
                </button>
                {msg && <div style={{ fontSize: 13, opacity: .9 }}>{msg}</div>}
            </div>
        </>
    )
}

const inp = { width: '100%', padding: '10px 12px', borderRadius: 10, border: '1px solid #1f2a37', background: '#0b1220', color: '#e6edf3' }
