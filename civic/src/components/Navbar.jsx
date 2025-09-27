import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'react-toastify'
import { Globe, ChevronDown, User, LogOut } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

export default function Navbar({ onLogout }) {
	const navigate = useNavigate()
	const { currentUser } = useAuth()
	const [isDropdownOpen, setIsDropdownOpen] = useState(false)
	const dropdownRef = useRef(null)
	
	// Get user info from Firebase or localStorage
	const userInfo = {
		name: currentUser?.displayName || localStorage.getItem('department') || 'Admin User',
		email: currentUser?.email || localStorage.getItem('email') || 'admin@city.gov',
		initials: currentUser?.displayName?.split(' ').map(word => word[0]).join('') || 
		         localStorage.getItem('department')?.split(' ').map(word => word[0]).join('') || 
		         'AU'
	}

	const handleLogout = async () => {
		try {
			if (onLogout) {
				await onLogout()
			} else {
				// Fallback to manual logout
				localStorage.removeItem('token')
				localStorage.removeItem('user')
				localStorage.removeItem('department')
				localStorage.removeItem('email')
			}
			toast.success('Logged out successfully')
			navigate('/login')
		} catch (error) {
			console.error('Logout error:', error)
			toast.error('Error during logout')
		} finally {
			setIsDropdownOpen(false)
		}
	}

	const handleProfile = () => {
		// Navigate to profile page or show profile modal
		toast.info('Profile page coming soon!')
		setIsDropdownOpen(false)
	}

	// Close dropdown when clicking outside
	useEffect(() => {
		const handleClickOutside = (event) => {
			if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
				setIsDropdownOpen(false)
			}
		}

		document.addEventListener('mousedown', handleClickOutside)
		return () => {
			document.removeEventListener('mousedown', handleClickOutside)
		}
	}, [])
	
	return (
		<header className="h-16 border-b border-slate-200 flex items-center justify-between px-6 bg-white">
			<div>
				<h1 className="text-xl font-semibold text-gray-900">Welcome to Dashboard</h1>
			</div>
			<div className="flex items-center gap-4">
				{/* Language Selector */}
				<div className="flex items-center gap-2 text-sm text-gray-600">
					<Globe className="w-4 h-4" />
					<select className="bg-transparent border-none focus:outline-none cursor-pointer">
						<option value="en">English</option>
						<option value="hi">Hindi</option>
						<option value="mr">Marathi</option>
					</select>
				</div>
				
				{/* User Profile Dropdown */}
				<div className="relative" ref={dropdownRef}>
					<button
						onClick={() => setIsDropdownOpen(!isDropdownOpen)}
						className="flex items-center gap-3 hover:bg-gray-50 rounded-lg p-2 transition-colors"
					>
						<div className="text-right">
							<div className="text-sm font-medium text-gray-900">{userInfo.name}</div>
							<div className="text-xs text-gray-500">{userInfo.email}</div>
						</div>
						<div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center text-white font-semibold text-sm">
							{userInfo.initials}
						</div>
						<ChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`} />
					</button>

					{/* Dropdown Menu */}
					{isDropdownOpen && (
						<div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
							<button
								onClick={handleProfile}
								className="w-full flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
							>
								<User className="w-4 h-4" />
								Profile
							</button>
							<button
								onClick={handleLogout}
								className="w-full flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
							>
								<LogOut className="w-4 h-4" />
								Logout
							</button>
						</div>
					)}
				</div>
			</div>
		</header>
	)
}
