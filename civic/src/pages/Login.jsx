import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'react-toastify'
import { Mail, Lock, ArrowLeft, Building2, MapPin, Users, BarChart3, Shield } from 'lucide-react'
import api from '../api'

export default function Login() {
	const navigate = useNavigate()
	const [email, setEmail] = useState('')
	const [password, setPassword] = useState('')
	const [loading, setLoading] = useState(false)

	const handleSubmit = async (e) => {
		e.preventDefault()
		setLoading(true)
		try {
			// Placeholder: simulate API if backend not ready
			const res = await api.post('/auth/login', { email, password }).catch(() => ({ data: { token: 'dev-token' } }))
			const token = res?.data?.token
			if (!token) throw new Error('Invalid credentials')
			localStorage.setItem('token', token)
			toast.success('Logged in successfully')
			navigate('/dashboard')
		} catch (err) {
			toast.error('Login failed')
		} finally {
			setLoading(false)
		}
	}

	return (
		<div className="min-h-screen flex">
			{/* Left Side - Login Form */}
			<div className="flex-1 flex flex-col justify-center px-8 lg:px-16 bg-white">
				{/* Header */}
				<div className="mb-8">
					<div className="flex items-center gap-3 mb-4">
						<div className="w-10 h-10 bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg flex items-center justify-center">
							<Building2 className="w-6 h-6 text-white" />
						</div>
						<span className="text-lg font-semibold text-slate-800">CIVIC DASHBOARD</span>
					</div>
					<div className="text-center mb-8">
						<div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
							<Shield className="w-8 h-8 text-white" />
						</div>
						<h1 className="text-2xl font-bold text-slate-800 mb-2">ADMIN PORTAL</h1>
						<p className="text-slate-600">Access your municipal management dashboard</p>
					</div>
				</div>

				{/* Login Form */}
				<form onSubmit={handleSubmit} className="space-y-6">
					<div>
						<label className="block text-sm font-medium text-slate-700 mb-2">Email Address</label>
						<div className="relative">
							<Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
							<input
								type="email"
								value={email}
								onChange={(e) => setEmail(e.target.value)}
								className="w-full pl-10 pr-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
								placeholder="admin@city.gov"
								required
							/>
						</div>
					</div>

					<div>
						<label className="block text-sm font-medium text-slate-700 mb-2">Password</label>
						<div className="relative">
							<Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
							<input
								type="password"
								value={password}
								onChange={(e) => setPassword(e.target.value)}
								className="w-full pl-10 pr-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
								placeholder="Enter your password"
								required
							/>
						</div>
					</div>

					<div className="flex items-center justify-between">
						<button
							type="submit"
							disabled={loading}
							className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-3 rounded-lg font-semibold hover:shadow-lg transition-all duration-300 disabled:opacity-60 disabled:cursor-not-allowed"
						>
							{loading ? 'Signing in...' : 'Login'}
						</button>
						<button
							type="button"
							className="text-slate-500 hover:text-slate-700 text-sm"
						>
							Forgot Password?
						</button>
					</div>
				</form>

				{/* Back to Home */}
				<div className="mt-8">
					<button
						onClick={() => navigate('/')}
						className="flex items-center gap-2 text-slate-500 hover:text-slate-700 transition-colors"
					>
						<ArrowLeft size={16} />
						Back to Home
					</button>
				</div>
			</div>

			{/* Right Side - Isometric Illustration */}
			<div className="hidden lg:flex flex-1 bg-gradient-to-br from-blue-50 via-purple-50 to-indigo-100 relative overflow-hidden">
				{/* Background Elements */}
				<div className="absolute inset-0">
					{/* Floating geometric shapes */}
					<div className="absolute top-20 left-20 w-16 h-16 bg-blue-200/30 rounded-lg transform rotate-12"></div>
					<div className="absolute top-40 right-32 w-12 h-12 bg-purple-200/30 rounded-full"></div>
					<div className="absolute bottom-32 left-16 w-20 h-20 bg-indigo-200/30 rounded-lg transform -rotate-12"></div>
					<div className="absolute bottom-20 right-20 w-14 h-14 bg-blue-300/20 rounded-full"></div>
				</div>

				{/* Main Illustration */}
				<div className="relative z-10 flex items-center justify-center w-full">
					<div className="grid grid-cols-2 gap-8 max-w-2xl">
						{/* Left Column */}
						<div className="space-y-6">
							{/* City Hall Building */}
							<div className="bg-gradient-to-b from-blue-400 to-blue-600 w-24 h-32 rounded-lg shadow-lg flex items-center justify-center">
								<Building2 className="w-8 h-8 text-white" />
							</div>
							
							{/* Reports Stack */}
							<div className="bg-gradient-to-b from-purple-400 to-purple-600 w-20 h-16 rounded-lg shadow-lg flex items-center justify-center">
								<BarChart3 className="w-6 h-6 text-white" />
							</div>
						</div>

						{/* Right Column */}
						<div className="space-y-6 mt-8">
							{/* Map Platform */}
							<div className="bg-gradient-to-b from-green-400 to-green-600 w-28 h-20 rounded-lg shadow-lg flex items-center justify-center">
								<MapPin className="w-6 h-6 text-white" />
							</div>
							
							{/* Users Platform */}
							<div className="bg-gradient-to-b from-orange-400 to-orange-600 w-24 h-18 rounded-lg shadow-lg flex items-center justify-center">
								<Users className="w-6 h-6 text-white" />
							</div>
						</div>
					</div>
				</div>

				{/* Decorative Elements */}
				<div className="absolute bottom-8 left-8 flex items-center gap-2">
					<div className="w-3 h-3 bg-blue-400 rounded-full"></div>
					<div className="w-2 h-2 bg-purple-400 rounded-full"></div>
					<div className="w-4 h-4 bg-green-400 rounded-full"></div>
				</div>
			</div>
		</div>
	)
}
