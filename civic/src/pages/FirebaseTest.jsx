import { useState } from 'react'
import { signInWithEmailAndPassword, createUserWithEmailAndPassword } from 'firebase/auth'
import { auth } from '../firebase'

export default function FirebaseTest() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [result, setResult] = useState('')
  const [loading, setLoading] = useState(false)

  const testLogin = async () => {
    setLoading(true)
    setResult('Testing login...')
    
    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password)
      setResult(`✅ Login successful! User: ${userCredential.user.email}`)
    } catch (error) {
      setResult(`❌ Login failed: ${error.code} - ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const testSignup = async () => {
    setLoading(true)
    setResult('Testing signup...')
    
    try {
      const userCredential = await createUserWithEmailAndPassword(auth, email, password)
      setResult(`✅ Signup successful! User: ${userCredential.user.email}`)
    } catch (error) {
      setResult(`❌ Signup failed: ${error.code} - ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const testConnection = () => {
    try {
      setResult(`✅ Firebase connected! Auth instance: ${auth ? 'Available' : 'Not available'}`)
    } catch (error) {
      setResult(`❌ Firebase connection failed: ${error.message}`)
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-md mx-auto bg-white rounded-lg shadow-md p-6">
        <h1 className="text-2xl font-bold mb-6 text-center">Firebase Test</h1>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="test@example.com"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="password123"
            />
          </div>
          
          <div className="space-y-2">
            <button
              onClick={testConnection}
              className="w-full bg-gray-500 text-white py-2 px-4 rounded-md hover:bg-gray-600"
            >
              Test Firebase Connection
            </button>
            
            <button
              onClick={testSignup}
              disabled={loading || !email || !password}
              className="w-full bg-green-500 text-white py-2 px-4 rounded-md hover:bg-green-600 disabled:opacity-50"
            >
              Test Signup
            </button>
            
            <button
              onClick={testLogin}
              disabled={loading || !email || !password}
              className="w-full bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600 disabled:opacity-50"
            >
              Test Login
            </button>
          </div>
          
          {result && (
            <div className="mt-4 p-3 bg-gray-100 rounded-md">
              <pre className="text-sm whitespace-pre-wrap">{result}</pre>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
