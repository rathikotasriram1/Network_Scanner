import React, { useEffect, useMemo, useState } from 'react'
import SeverityChart from './components/SeverityChart'
import StartScan from './components/StartScan'

export default function App() {
    const [scans, setScans] = useState([])
    const [counts, setCounts] = useState({ info: 0, low: 0, medium: 0, high: 0, critical: 0 })

    async function load() {
        const r = await fetch('/api/scans')
        const data = await r.json()
        setScans(data)
        // aggregate totals for chart
        const agg = { info: 0, low: 0, medium: 0, high: 0, critical: 0 }
        for (const s of data) {
            if (!s.summary_json) continue
            try {
                const j = JSON.parse(s.summary_json)
                const c = j.severity_counts || {}
                for (const k of Object.keys(agg)) agg[k] += c[k] || 0
            } catch { }
        }
        setCounts(agg)
    }

    useEffect(() => { load() }, [])

    useEffect(() => {
        const wsProto = location.protocol === 'https:' ? 'wss' : 'ws'
        const ws = new WebSocket(`${wsProto}://${location.host}/ws`)
        ws.onmessage = (e) => {
            const msg = JSON.parse(e.data)
            if (msg.status) load()
        }
        return () => ws.close()
    }, [])

    const chartData = useMemo(() => [
        { name: 'Critical', value: counts.critical },
        { name: 'High', value: counts.high },
        { name: 'Medium', value: counts.medium },
        { name: 'Low', value: counts.low },
        { name: 'Info', value: counts.info }
    ], [counts])

    return (
        <div style={{ padding: '24px', maxWidth: 1100, margin: '0 auto' }}>
            <h1 style={{ marginBottom: 12 }}>AI Cyber Dashboard</h1>
            <p style={{ opacity: .8, marginBottom: 24 }}>Start Nessus scans, watch live status, and review severity counts.</p>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
                <div style={{ background: '#0f1720', padding: 16, borderRadius: 16, boxShadow: '0 0 0 1px #1f2a37 inset' }}>
                    <StartScan onStarted={load} />
                </div>
                <div style={{ background: '#0f1720', padding: 16, borderRadius: 16, boxShadow: '0 0 0 1px #1f2a37 inset' }}>
                    <h3 style={{ margin: '0 0 12px' }}>Severity (All Scans)</h3>
                    <SeverityChart data={chartData} />
                </div>
            </div>

            <div style={{ marginTop: 24, background: '#0f1720', padding: 16, borderRadius: 16, boxShadow: '0 0 0 1px #1f2a37 inset' }}>
                <h3 style={{ margin: '0 0 12px' }}>Recent Scans</h3>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <thead>
                        <tr>
                            <th style={th}>ID</th><th style={th}>Target</th><th style={th}>Nessus ID</th>
                            <th style={th}>Status</th><th style={th}>Started</th><th style={th}>Finished</th>

                        </tr>
                    </thead>
                    <tbody>
                        {scans.map(s => (
                            <tr key={s.id}>
                                <td style={td}>{s.id}</td>
                                <td style={td}>{s.target}</td>
                                <td style={td}>{s.raw_ref}</td>
                                <td style={td}>{s.status}</td>
                                <td style={td}>{s.started_at?.replace('T', ' ').slice(0, 19)}</td>
                                <td style={td}>{s.finished_at?.replace('T', ' ').slice(0, 19) || '-'}</td>
                            </tr>
                        ))}
                        {scans.length === 0 && <tr><td style={td} colSpan={6}>(no scans yet)</td></tr>}
                    </tbody>
                </table>
            </div>
        </div >
    )
}

const th = { textAlign: 'left', padding: '8px 10px', borderBottom: '1px solid #1f2a37', fontWeight: 600 }
const td = { padding: '8px 10px', borderBottom: '1px solid #1f2a37', fontFamily: 'ui-monospace, SFMono-Regular, Menlo' }
