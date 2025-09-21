import { useNavigate, Link } from 'react-router-dom'
import { MapPin, Route as RouteIcon, BarChart3, CheckCircle, Clock, AlertCircle, Bot } from 'lucide-react'
import { useState, useEffect } from 'react'

export default function Landing() {
	const navigate = useNavigate()
	const [counts, setCounts] = useState({ solved: 0, pending: 0, ongoing: 0 })

	// Animate counters on mount
	useEffect(() => {
		const targetCounts = { solved: 1247, pending: 89, ongoing: 156 }
		const duration = 2000
		const steps = 60
		const stepDuration = duration / steps

		let step = 0
		const timer = setInterval(() => {
			step++
			const progress = step / steps
			const easeOut = 1 - Math.pow(1 - progress, 3)

			setCounts({
				solved: Math.floor(targetCounts.solved * easeOut),
				pending: Math.floor(targetCounts.pending * easeOut),
				ongoing: Math.floor(targetCounts.ongoing * easeOut)
			})

			if (step >= steps) {
				setCounts(targetCounts)
				clearInterval(timer)
			}
		}, stepDuration)

		return () => clearInterval(timer)
	}, [])

	return (
		<div className="min-h-screen flex flex-col bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-100">
			{/* Navbar */}
			<header className="sticky top-0 z-20 bg-white/90 backdrop-blur supports-[backdrop-filter]:bg-white/70 border-b border-purple-200 shadow-lg">
				<div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
					<div className="text-lg sm:text-xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">Civic Dashboard</div>
					<nav className="hidden sm:flex items-center gap-6 text-sm text-slate-600">
						<Link to="/" className="hover:text-purple-600 transition-colors">Home</Link>
						<a href="#features" className="hover:text-purple-600 transition-colors">Features</a>
						<a href="#stats" className="hover:text-purple-600 transition-colors">Stats</a>
						<Link to="/login" className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-4 py-2 rounded-full hover:shadow-lg transition-all">Login</Link>
					</nav>
				</div>
			</header>

			{/* Hero */}
			<section className="relative overflow-hidden">
				<div className="absolute inset-0 pointer-events-none">
					<div className="absolute -top-32 -right-32 w-96 h-96 rounded-full bg-gradient-to-r from-purple-300/40 to-pink-300/40 blur-3xl" />
					<div className="absolute -bottom-32 -left-32 w-96 h-96 rounded-full bg-gradient-to-r from-blue-300/40 to-indigo-300/40 blur-3xl" />
					<div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-64 h-64 rounded-full bg-gradient-to-r from-cyan-300/30 to-emerald-300/30 blur-3xl" />
				</div>
				<div className="flex items-center">
					<div className="mx-auto w-full max-w-4xl px-6 py-20 sm:py-24 text-center relative">
						<h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight bg-gradient-to-r from-purple-600 via-blue-600 to-indigo-600 bg-clip-text text-transparent">
							Civic Issue Management Dashboard
						</h1>
						<p className="mt-6 text-slate-600 text-lg sm:text-xl md:text-2xl max-w-2xl mx-auto">
							Empowering municipalities to track and resolve civic issues efficiently with real-time insights.
						</p>
						<div className="mt-10">
							<button
								onClick={() => navigate('/signup')}
								className="inline-flex items-center justify-center rounded-full bg-gradient-to-r from-purple-600 to-blue-600 px-8 py-4 text-white font-semibold text-lg shadow-2xl hover:shadow-purple-300/50 hover:scale-105 transition-all duration-300 focus:outline-none focus:ring-4 focus:ring-purple-300"
							>
								Get Started
							</button>
						</div>
					</div>
				</div>
			</section>

			{/* Stats Section */}
			<section id="stats" className="w-full max-w-6xl mx-auto px-6 py-12">
				<div className="text-center mb-8">
					<h2 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-4">Real-time Impact</h2>
					<p className="text-slate-600 text-lg">Track the progress of civic issue resolution across the city</p>
				</div>
				<div className="grid gap-6 sm:gap-8 grid-cols-1 md:grid-cols-3">
					<div className="bg-gradient-to-br from-green-50 to-emerald-100 rounded-xl shadow-lg p-6 border border-green-200">
						<div className="flex items-center justify-center w-16 h-16 rounded-full bg-green-500 text-white mb-4 mx-auto">
							<CheckCircle size={32} />
						</div>
						<div className="text-4xl font-bold text-green-600 mb-2">{counts.solved.toLocaleString()}</div>
						<div className="text-green-700 font-semibold">Cases Solved</div>
						<div className="text-green-600 text-sm mt-1">Successfully resolved</div>
					</div>
					<div className="bg-gradient-to-br from-yellow-50 to-amber-100 rounded-xl shadow-lg p-6 border border-yellow-200">
						<div className="flex items-center justify-center w-16 h-16 rounded-full bg-yellow-500 text-white mb-4 mx-auto">
							<Clock size={32} />
						</div>
						<div className="text-4xl font-bold text-yellow-600 mb-2">{counts.pending.toLocaleString()}</div>
						<div className="text-yellow-700 font-semibold">Pending Cases</div>
						<div className="text-yellow-600 text-sm mt-1">Awaiting review</div>
					</div>
					<div className="bg-gradient-to-br from-blue-50 to-cyan-100 rounded-xl shadow-lg p-6 border border-blue-200">
						<div className="flex items-center justify-center w-16 h-16 rounded-full bg-blue-500 text-white mb-4 mx-auto">
							<AlertCircle size={32} />
						</div>
						<div className="text-4xl font-bold text-blue-600 mb-2">{counts.ongoing.toLocaleString()}</div>
						<div className="text-blue-700 font-semibold">In Progress</div>
						<div className="text-blue-600 text-sm mt-1">Currently being addressed</div>
					</div>
				</div>
			</section>

			{/* Features */}
			<section id="features" className="w-full max-w-6xl mx-auto px-6 py-12">
				<div className="text-center mb-12">
					<h2 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-4">Powerful Features</h2>
					<p className="text-slate-600 text-lg">Everything you need to manage civic issues effectively</p>
				</div>
				<div className="grid gap-8 sm:gap-10 grid-cols-1 md:grid-cols-2 lg:grid-cols-4">
					<div className="bg-white rounded-xl shadow-lg p-8 transition-all duration-300 hover:scale-105 hover:shadow-2xl border border-purple-100">
						<div className="w-16 h-16 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 text-white flex items-center justify-center mb-6">
							<MapPin size={28} />
						</div>
						<h3 className="text-xl font-bold text-slate-900 mb-3">Real-time Issue Tracking</h3>
						<p className="text-slate-600">
							Citizens can report issues with photos & location. Get instant notifications and track resolution progress.
						</p>
					</div>
					<div className="bg-white rounded-xl shadow-lg p-8 transition-all duration-300 hover:scale-105 hover:shadow-2xl border border-green-100">
						<div className="w-16 h-16 rounded-full bg-gradient-to-r from-green-500 to-emerald-500 text-white flex items-center justify-center mb-6">
							<RouteIcon size={28} />
						</div>
						<h3 className="text-xl font-bold text-slate-900 mb-3">Smart Department Suggestions</h3>
						<p className="text-slate-600">
							AI analyzes reports and suggests the most relevant department for faster routing and resolution, reducing delays caused by misclassification.
						</p>
					</div>
					<div className="bg-white rounded-xl shadow-lg p-8 transition-all duration-300 hover:scale-105 hover:shadow-2xl border border-blue-100">
						<div className="w-16 h-16 rounded-full bg-gradient-to-r from-blue-500 to-cyan-500 text-white flex items-center justify-center mb-6">
							<BarChart3 size={28} />
						</div>
						<h3 className="text-xl font-bold text-slate-900 mb-3">Analytics & Insights</h3>
						<p className="text-slate-600">
							Track performance with interactive dashboards and generate detailed reports for stakeholders.
						</p>
					</div>
					<div className="bg-white rounded-xl shadow-lg p-8 transition-all duration-300 hover:scale-105 hover:shadow-2xl border border-orange-100">
						<div className="w-16 h-16 rounded-full bg-gradient-to-r from-orange-500 to-red-500 text-white flex items-center justify-center mb-6">
							<Bot size={28} />
						</div>
						<h3 className="text-xl font-bold text-slate-900 mb-3">AI-Powered Urgency Prediction</h3>
						<p className="text-slate-600">
							Automatically predicts the urgency of each issue using AI, helping departments prioritize critical problems first and improve response times.
						</p>
					</div>
				</div>
			</section>

			{/* CTA Section */}
			<section className="w-full max-w-6xl mx-auto px-6 pb-12">
				<div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl shadow-2xl p-8 sm:p-12 text-center text-white">
					<h3 className="text-2xl sm:text-3xl font-bold mb-4">Ready to make your city smarter?</h3>
					<p className="text-purple-100 text-lg mb-8 max-w-2xl mx-auto">Sign in to manage issues or explore the dashboard and see how we're transforming civic management.</p>
					<div className="flex flex-col sm:flex-row gap-4 justify-center">
						<button 
							onClick={() => navigate('/signup')} 
							className="inline-flex items-center justify-center rounded-full bg-white text-purple-600 px-8 py-4 font-semibold text-lg shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-300"
						>
							Get Started
						</button>
						<button 
							onClick={() => navigate('/dashboard')} 
							className="inline-flex items-center justify-center rounded-full bg-purple-500/20 text-white px-8 py-4 font-semibold text-lg border border-white/30 hover:bg-purple-500/30 hover:scale-105 transition-all duration-300"
						>
							Explore Dashboard
						</button>
					</div>
				</div>
			</section>

			{/* Footer */}
			<footer className="w-full py-8 text-center text-slate-500 bg-slate-50">
				<div className="max-w-6xl mx-auto px-6">
					<div className="text-lg font-semibold text-slate-700 mb-2">Civic Dashboard</div>
					<div>© 2025 Civic Dashboard. Empowering smart cities worldwide.</div>
				</div>
			</footer>
		</div>
	)
}
