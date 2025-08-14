import React from 'react'
import { PieChart, Pie, Tooltip, Legend } from 'recharts'

export default function SeverityChart({ data }) {
    return (
        <div style={{ display: 'flex', justifyContent: 'center' }}>
            <PieChart width={360} height={240}>
                <Pie dataKey="value" data={data} outerRadius={100} label />
                <Tooltip />
                <Legend />
            </PieChart>
        </div>
    )
}
