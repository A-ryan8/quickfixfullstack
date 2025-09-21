import { useEffect, useMemo, useRef, useState } from 'react'
import { DataGrid } from '@mui/x-data-grid'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import api from '../api'

// Fix default icon paths in Leaflet when using bundlers
import iconUrl from 'leaflet/dist/images/marker-icon.png'
import shadowUrl from 'leaflet/dist/images/marker-shadow.png'

const DefaultIcon = L.icon({ iconUrl, shadowUrl, iconAnchor: [12, 41] })
L.Marker.prototype.options.icon = DefaultIcon

function FlyTo({ lat, lng }) {
	const map = useMap()
	useEffect(() => {
		if (lat && lng) {
			map.flyTo([lat, lng], 14, { duration: 0.5 })
		}
	}, [lat, lng, map])
	return null
}

export default function Reports() {
	const [rows, setRows] = useState([])
	const [loading, setLoading] = useState(true)
	const [status, setStatus] = useState('')
	const [category, setCategory] = useState('')
	const [selected, setSelected] = useState(null)

	useEffect(() => {
		const params = new URLSearchParams(window.location.search)
		const statusParam = params.get('status') || ''
		setStatus(statusParam)
	}, [])

	useEffect(() => {
		const load = async () => {
			try {
				const res = await api.get('/reports').catch(() => ({ data: mockReports }))
				setRows(res.data)
			} finally {
				setLoading(false)
			}
		}
		load()
	}, [])

	const categories = useMemo(() => Array.from(new Set(rows.map((r) => r.category))), [rows])
	const filtered = useMemo(() => rows.filter((r) => (!status || r.status === status) && (!category || r.category === category)), [rows, status, category])

	const columns = [
		{ field: 'id', headerName: 'ID', width: 90 },
		{ field: 'category', headerName: 'Category', flex: 1 },
		{ field: 'status', headerName: 'Status', flex: 1 },
		{ field: 'createdAt', headerName: 'Created At', flex: 1 },
	]

	const position = [19.07, 72.87]

	return (
		<div className="space-y-4">
			<div className="bg-white rounded shadow p-3 flex flex-wrap gap-3 items-center">
				<label className="text-sm">Status</label>
				<select value={status} onChange={(e) => setStatus(e.target.value)} className="border rounded px-2 py-1">
					<option value="">All</option>
					<option value="Open">Open</option>
					<option value="In Progress">In Progress</option>
					<option value="Resolved">Resolved</option>
				</select>
				<label className="text-sm ml-4">Category</label>
				<select value={category} onChange={(e) => setCategory(e.target.value)} className="border rounded px-2 py-1">
					<option value="">All</option>
					{categories.map((c) => (
						<option key={c} value={c}>{c}</option>
					))}
				</select>
				<button onClick={() => { setStatus(''); setCategory('') }} className="ml-auto text-sm px-3 py-1 rounded bg-slate-100 hover:bg-slate-200">Reset</button>
			</div>
			<div className="bg-white rounded shadow p-2" style={{ height: 420 }}>
				<DataGrid
					rows={filtered}
					columns={columns}
					loading={loading}
					disableRowSelectionOnClick
					onRowClick={(p) => setSelected(p.row)}
				/>
			</div>
			<div className="bg-white rounded shadow overflow-hidden">
				<MapContainer center={position} zoom={11} style={{ height: 400 }}>
					<TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution="&copy; OpenStreetMap contributors" />
					{filtered.map((r) => (
						<Marker key={r.id} position={[r.lat, r.lng]}>
							<Popup>
								<div className="font-semibold">{r.category}</div>
								<div className="text-sm">Status: {r.status}</div>
							</Popup>
						</Marker>
					))}
					{selected ? <FlyTo lat={selected.lat} lng={selected.lng} /> : null}
				</MapContainer>
			</div>
		</div>
	)
}

const mockReports = [
	{ id: 1, category: 'Pothole', status: 'Open', createdAt: '2025-09-10', lat: 19.076, lng: 72.8777 },
	{ id: 2, category: 'Streetlight', status: 'Resolved', createdAt: '2025-09-09', lat: 19.09, lng: 72.85 },
	{ id: 3, category: 'Trash', status: 'In Progress', createdAt: '2025-09-08', lat: 19.05, lng: 72.9 },
	{ id: 4, category: 'Pothole', status: 'Open', createdAt: '2025-09-07', lat: 19.02, lng: 72.88 },
]
