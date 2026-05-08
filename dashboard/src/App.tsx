import { useEffect, useState } from 'react'
import axios from 'axios'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

type Scan = {
  id: number
  target: string
  status: string
  started_at: string
  summary: string
}

export default function App() {
  const [scans, setScans] = useState<Scan[]>([])

  useEffect(() => {
    axios.get('http://localhost:8000/scan-history?limit=20')
      .then((res) => setScans(res.data))
      .catch(() => setScans([]))
  }, [])

  const chartData = scans.map((s) => ({
    target: s.target.slice(0, 12),
    id: s.id
  }))

  return (
    <div className="min-h-screen bg-gradient-to-br from-midnight via-steel to-black text-white p-6">
      <header className="mb-8">
        <h1 className="text-4xl font-extrabold tracking-wide">CyberRecon Dashboard</h1>
        <p className="text-slate-300">AI-powered bug bounty reconnaissance analytics</p>
      </header>

      <section className="grid gap-6 md:grid-cols-2">
        <div className="bg-white/10 backdrop-blur rounded-2xl p-4 border border-white/20">
          <h2 className="text-xl font-semibold mb-3">Recent Scans</h2>
          <div className="space-y-2 max-h-96 overflow-auto">
            {scans.map((scan) => (
              <div key={scan.id} className="bg-black/30 rounded-xl p-3">
                <div className="font-semibold">{scan.target}</div>
                <div className="text-sm text-slate-300">{scan.status} | {new Date(scan.started_at).toLocaleString()}</div>
                <div className="text-sm text-slate-200">{scan.summary}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white/10 backdrop-blur rounded-2xl p-4 border border-white/20 h-96">
          <h2 className="text-xl font-semibold mb-3">Scan Volume</h2>
          <ResponsiveContainer width="100%" height="85%">
            <BarChart data={chartData}>
              <XAxis dataKey="target" stroke="#d1d5db" />
              <YAxis stroke="#d1d5db" />
              <Tooltip />
              <Bar dataKey="id" fill="#22c55e" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </section>
    </div>
  )
}
