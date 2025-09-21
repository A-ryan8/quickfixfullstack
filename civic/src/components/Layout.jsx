import { Outlet, Navigate } from 'react-router-dom'
import Sidebar from './Sidebar'
import Navbar from './Navbar'

export default function Layout() {
	const isAuthed = Boolean(localStorage.getItem('token'))
	if (!isAuthed) return <Navigate to="/login" />
	return (
		<div className="min-h-screen bg-slate-50 text-slate-900">
			<div className="flex">
				<Sidebar />
				<div className="flex-1">
					<Navbar />
					<main className="p-4">
						<Outlet />
					</main>
				</div>
			</div>
		</div>
	)
}
