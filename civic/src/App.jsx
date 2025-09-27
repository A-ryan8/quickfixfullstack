import { Routes, Route, Navigate, createBrowserRouter, RouterProvider } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Login from './pages/Login'
import SignUp from './pages/SignUp'
import Dashboard from './pages/Dashboard'
import Reports from './pages/Reports'
import Analytics from './pages/Analytics'
import Messages from './pages/Messages'
import Landing from './pages/Landing'
import FirebaseTest from './pages/FirebaseTest'
import Layout from './components/Layout'

// Protected Route component
function ProtectedRoute({ children }) {
  const { currentUser, loading } = useAuth()
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading...</p>
        </div>
      </div>
    )
  }
  
  return currentUser ? children : <Navigate to="/login" />
}

const router = createBrowserRouter([
	{
		path: "/",
		element: <Landing />
	},
	{
		path: "/login",
		element: <Login />
	},
	{
		path: "/signup",
		element: <SignUp />
	},
	{
		path: "/firebase-test",
		element: <FirebaseTest />
	},
	{
		path: "/",
		element: <ProtectedRoute><Layout /></ProtectedRoute>,
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
	return (
		<AuthProvider>
			<RouterProvider router={router} />
		</AuthProvider>
	)
}
