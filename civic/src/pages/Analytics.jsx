import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'

const data = [
	{ name: 'Potholes', value: 8 },
	{ name: 'Streetlights', value: 5 },
	{ name: 'Trash', value: 7 },
]
const COLORS = ['#3b82f6', '#10b981', '#f59e0b']

export default function Analytics() {
	return (
		<div className="bg-white rounded shadow p-4" style={{ height: 340 }}>
			<ResponsiveContainer width="100%" height="100%">
				<PieChart>
					<Pie data={data} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label>
						{data.map((entry, index) => (
							<Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
						))}
					</Pie>
					<Tooltip />
					<Legend />
				</PieChart>
			</ResponsiveContainer>
		</div>
	)
}
