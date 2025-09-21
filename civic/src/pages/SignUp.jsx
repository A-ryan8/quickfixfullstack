import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { toast } from 'react-toastify'
import { ArrowLeft, Building2, Mail, Lock, MapPin, Globe } from 'lucide-react'

export default function SignUp() {
	const navigate = useNavigate()
	const { t, i18n } = useTranslation()
	const [formData, setFormData] = useState({
		municipalCorp: '',
		department: '',
		email: '',
		password: '',
		confirmPassword: '',
		officeLocation: '',
		preferredLanguage: 'en'
	})
	const [errors, setErrors] = useState({})
	const [loading, setLoading] = useState(false)

	const handleChange = (e) => {
		const { name, value } = e.target
		setFormData({
			...formData,
			[name]: value
		})
		// Clear error when user starts typing
		if (errors[name]) {
			setErrors({
				...errors,
				[name]: ''
			})
		}
	}

	const validateForm = () => {
		const newErrors = {}

		// Required field validation
		if (!formData.municipalCorp.trim()) newErrors.municipalCorp = t('signup.validation.required')
		if (!formData.department) newErrors.department = t('signup.validation.required')
		if (!formData.email.trim()) newErrors.email = t('signup.validation.required')
		if (!formData.password) newErrors.password = t('signup.validation.required')
		if (!formData.confirmPassword) newErrors.confirmPassword = t('signup.validation.required')
		if (!formData.officeLocation.trim()) newErrors.officeLocation = t('signup.validation.required')

		// Email validation
		const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
		if (formData.email && !emailRegex.test(formData.email)) {
			newErrors.email = t('signup.validation.emailInvalid')
		}

		// Password validation
		if (formData.password && formData.password.length < 8) {
			newErrors.password = t('signup.validation.passwordMinLength')
		}

		// Password match validation
		if (formData.password !== formData.confirmPassword) {
			newErrors.confirmPassword = t('signup.validation.passwordMismatch')
		}

		setErrors(newErrors)
		return Object.keys(newErrors).length === 0
	}

	const handleSubmit = async (e) => {
		e.preventDefault()
		
		if (!validateForm()) {
			return
		}

		setLoading(true)
		try {
			// Placeholder: simulate API call
			await new Promise(resolve => setTimeout(resolve, 1500))
			
			// Save department info to localStorage for navbar display
			localStorage.setItem('department', formData.department)
			localStorage.setItem('email', formData.email)
			
			toast.success(t('signup.success'))
			navigate('/login')
		} catch (err) {
			toast.error(t('signup.error'))
		} finally {
			setLoading(false)
		}
	}

	const changeLanguage = (lng) => {
		i18n.changeLanguage(lng)
		setFormData({
			...formData,
			preferredLanguage: lng
		})
	}

	const departments = [
		{ value: 'sanitation', label: t('departments.sanitation') },
		{ value: 'publicWorks', label: t('departments.publicWorks') },
		{ value: 'streetlights', label: t('departments.streetlights') },
		{ value: 'waterSupply', label: t('departments.waterSupply') },
		{ value: 'wasteManagement', label: t('departments.wasteManagement') },
		{ value: 'transportation', label: t('departments.transportation') },
		{ value: 'planning', label: t('departments.planning') },
		{ value: 'safety', label: t('departments.safety') }
	]

	const languages = [
		{ value: 'en', label: t('languages.english') },
		{ value: 'hi', label: t('languages.hindi') },
		{ value: 'mr', label: t('languages.marathi') }
	]

	return (
		<div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-100 py-8">
			<div className="w-full max-w-2xl mx-auto px-6">
				{/* Language Switcher */}
				<div className="flex justify-end mb-4">
					<select
						value={i18n.language}
						onChange={(e) => changeLanguage(e.target.value)}
						className="bg-white border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
					>
						{languages.map(lang => (
							<option key={lang.value} value={lang.value}>{lang.label}</option>
						))}
					</select>
				</div>

				{/* Back Button */}
				<button
					onClick={() => navigate('/')}
					className="flex items-center gap-2 text-slate-600 hover:text-slate-800 transition-colors mb-6"
				>
					<ArrowLeft size={20} />
					Back to Home
				</button>

				{/* Main Card */}
				<div className="bg-white rounded-2xl shadow-2xl border border-slate-200 p-8">
					{/* Header */}
					<div className="text-center mb-8">
						<h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-2">
							{t('signup.title')}
						</h1>
						<p className="text-slate-600">{t('signup.subtitle')}</p>
					</div>

					{/* Sign Up Form */}
					<form onSubmit={handleSubmit} className="space-y-6">
						{/* Municipal Corporation */}
						<div>
							<label className="block text-sm font-medium text-slate-700 mb-2 flex items-center gap-2">
								<Building2 size={16} />
								{t('signup.municipalCorp')}
							</label>
							<input
								type="text"
								name="municipalCorp"
								value={formData.municipalCorp}
								onChange={handleChange}
								className={`w-full border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent ${
									errors.municipalCorp ? 'border-red-500' : 'border-slate-300'
								}`}
								placeholder={t('signup.municipalCorpPlaceholder')}
							/>
							{errors.municipalCorp && <p className="text-red-500 text-sm mt-1">{errors.municipalCorp}</p>}
						</div>

						{/* Department */}
						<div>
							<label className="block text-sm font-medium text-slate-700 mb-2 flex items-center gap-2">
								<Building2 size={16} />
								{t('signup.department')}
							</label>
							<select
								name="department"
								value={formData.department}
								onChange={handleChange}
								className={`w-full border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent ${
									errors.department ? 'border-red-500' : 'border-slate-300'
								}`}
							>
								<option value="">{t('signup.departmentPlaceholder')}</option>
								{departments.map(dept => (
									<option key={dept.value} value={dept.value}>{dept.label}</option>
								))}
							</select>
							{errors.department && <p className="text-red-500 text-sm mt-1">{errors.department}</p>}
						</div>

						{/* Email */}
						<div>
							<label className="block text-sm font-medium text-slate-700 mb-2 flex items-center gap-2">
								<Mail size={16} />
								{t('signup.email')}
							</label>
							<input
								type="email"
								name="email"
								value={formData.email}
								onChange={handleChange}
								className={`w-full border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent ${
									errors.email ? 'border-red-500' : 'border-slate-300'
								}`}
								placeholder={t('signup.emailPlaceholder')}
							/>
							{errors.email && <p className="text-red-500 text-sm mt-1">{errors.email}</p>}
						</div>

						{/* Password */}
						<div>
							<label className="block text-sm font-medium text-slate-700 mb-2 flex items-center gap-2">
								<Lock size={16} />
								{t('signup.password')}
							</label>
							<input
								type="password"
								name="password"
								value={formData.password}
								onChange={handleChange}
								className={`w-full border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent ${
									errors.password ? 'border-red-500' : 'border-slate-300'
								}`}
								placeholder={t('signup.passwordPlaceholder')}
							/>
							{errors.password && <p className="text-red-500 text-sm mt-1">{errors.password}</p>}
						</div>

						{/* Confirm Password */}
						<div>
							<label className="block text-sm font-medium text-slate-700 mb-2 flex items-center gap-2">
								<Lock size={16} />
								{t('signup.confirmPassword')}
							</label>
							<input
								type="password"
								name="confirmPassword"
								value={formData.confirmPassword}
								onChange={handleChange}
								className={`w-full border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent ${
									errors.confirmPassword ? 'border-red-500' : 'border-slate-300'
								}`}
								placeholder={t('signup.confirmPasswordPlaceholder')}
							/>
							{errors.confirmPassword && <p className="text-red-500 text-sm mt-1">{errors.confirmPassword}</p>}
						</div>

						{/* Office Location */}
						<div>
							<label className="block text-sm font-medium text-slate-700 mb-2 flex items-center gap-2">
								<MapPin size={16} />
								{t('signup.officeLocation')}
							</label>
							<input
								type="text"
								name="officeLocation"
								value={formData.officeLocation}
								onChange={handleChange}
								className={`w-full border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent ${
									errors.officeLocation ? 'border-red-500' : 'border-slate-300'
								}`}
								placeholder={t('signup.officeLocationPlaceholder')}
							/>
							{errors.officeLocation && <p className="text-red-500 text-sm mt-1">{errors.officeLocation}</p>}
						</div>

						{/* Preferred Language */}
						<div>
							<label className="block text-sm font-medium text-slate-700 mb-2 flex items-center gap-2">
								<Globe size={16} />
								{t('signup.preferredLanguage')}
							</label>
							<select
								name="preferredLanguage"
								value={formData.preferredLanguage}
								onChange={handleChange}
								className="w-full border border-slate-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
							>
								{languages.map(lang => (
									<option key={lang.value} value={lang.value}>{lang.label}</option>
								))}
							</select>
						</div>

						{/* Submit Button */}
						<button
							type="submit"
							disabled={loading}
							className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white py-4 rounded-lg font-semibold text-lg hover:shadow-lg hover:scale-105 transition-all duration-300 disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:scale-100"
						>
							{loading ? t('signup.signupButtonLoading') : t('signup.signupButton')}
						</button>
					</form>

					{/* Login Link */}
					<div className="text-center mt-6">
						<p className="text-slate-600">
							{t('signup.loginLink')}{' '}
							<button
								onClick={() => navigate('/login')}
								className="text-purple-600 hover:text-purple-700 font-semibold"
							>
								Login
							</button>
						</p>
					</div>
				</div>
			</div>
		</div>
	)
}
