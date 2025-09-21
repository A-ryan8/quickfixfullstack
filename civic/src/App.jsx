import { Routes, Route, Navigate, createBrowserRouter, RouterProvider } from 'react-router-dom'
import Login from './pages/Login'
import SignUp from './pages/SignUp'
import Dashboard from './pages/Dashboard'
import Reports from './pages/Reports'
import Analytics from './pages/Analytics'
import Messages from './pages/Messages'
import Landing from './pages/Landing'
import Layout from './components/Layout'

const isAuthenticated = () => {
	return Boolean(localStorage.getItem('token'))
}

const router = createBrowserRouter([
	{
		path: "/",
		element: <Landing />
	},
	{
		path: "/login",
		element: isAuthenticated() ? <Navigate to="/dashboard" /> : <Login />
	},
	{
		path: "/signup",
		element: isAuthenticated() ? <Navigate to="/dashboard" /> : <SignUp />
	},
	{
		path: "/",
		element: <Layout />,
		children: [
			{
				path: "dashboard",
				element: <Dashboard />
			},
			{
				path: "reports",
				element: <Reports />
			},
			{
				path: "analytics",
				element: <Analytics />
			},
			{
				path: "messages",
				element: <Messages />
			}
		]
	},
	{
		path: "*",
		element: <Navigate to="/" />
	}
], {
	future: {
		v7_startTransition: true,
		v7_relativeSplatPath: true
	}
})

export default function App() {
	return <RouterProvider router={router} />
}
