import axios from 'axios'

const api = axios.create({
	baseURL: '/api',
})

// Create a separate instance for the FastAPI backend
const API = axios.create({ baseURL: 'http://localhost:8000' });

api.interceptors.request.use((config) => {
	const token = localStorage.getItem('token')
	if (token) config.headers.Authorization = `Bearer ${token}`
	return config
})

// FastAPI backend endpoints for complaints
export const fetchComplaints = () => API.get('/api/complaints');

export const updateComplaintStatus = (id, newStatus) => API.put(`/api/complaints/${id}`, { status: newStatus });

export const fetchComplaintStats = () => API.get('/api/complaints/stats');

export const deleteComplaint = (id) => API.delete(`/api/complaints/${id}`);

export default api
