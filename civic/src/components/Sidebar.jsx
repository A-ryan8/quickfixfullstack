import { NavLink } from 'react-router-dom'

export default function Sidebar() {
	const linkClass = ({ isActive }) => `block px-4 py-2 rounded hover:bg-slate-100 ${isActive ? 'bg-slate-200 font-semibold' : ''}`
	return (
		<aside className="w-60 border-r border-slate-200 h-screen sticky top-0 bg-white">
			<div className="px-4 py-4 text-xl font-bold">Civic Admin</div>
			<nav className="px-2 space-y-1">
				<NavLink to="/dashboard" className={linkClass}>Dashboard</NavLink>
				<NavLink to="/analytics" className={linkClass}>Analytics</NavLink>
				<NavLink to="/messages" className={linkClass}>Messages</NavLink>
			</nav>
		</aside>
	)
}
