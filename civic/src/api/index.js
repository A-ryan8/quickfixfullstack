import axios from 'axios'

const api = axios.create({
	baseURL: '/api',
})

// Create a separate instance for the FastAPI backend
const API = axios.create({ baseURL: 'http://localhost:8000' });

// Add authentication interceptor to the FastAPI instance
API.interceptors.request.use((config) => {
	const token = localStorage.getItem('token')
	if (token) {
		config.headers.Authorization = `Bearer ${token}`
		console.log('🔐 Sending authentication token with request:', config.url)
	} else {
		console.warn('⚠️ No authentication token found in localStorage')
	}
	return config
})

// Add response interceptor for debugging
API.interceptors.response.use(
	(response) => {
		console.log('✅ API Response:', response.status, response.config.url)
		return response
	},
	(error) => {
		console.error('❌ API Error:', error.response?.status, error.response?.data, error.config?.url)
		return Promise.reject(error)
	}
)

api.interceptors.request.use((config) => {
	const token = localStorage.getItem('token')
	if (token) config.headers.Authorization = `Bearer ${token}`
	return config
})

// FastAPI backend endpoints for complaints
export const fetchComplaints = () => API.get('/api/complaints/public');

export const updateComplaintStatus = (id, newStatus) => API.put(`/api/complaints/${id}`, { status: newStatus });

export const fetchComplaintStats = () => API.get('/api/complaints/stats/public');

export const deleteComplaint = (id) => API.delete(`/api/complaints/${id}`);

export default api
