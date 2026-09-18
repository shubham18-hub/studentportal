import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { GoogleLogin } from '@react-oauth/google'
import { Mail, Lock, AlertCircle } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'
import { authAPI } from '../api/auth'

export default function LoginPage() {
  const [isAdminMode, setIsAdminMode] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleAdminLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      const response = await authAPI.adminLogin(email, password)
      login(response.access_token, response.user!)
      navigate('/')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed')
    } finally {
      setIsLoading(false)
    }
  }

  const handleGoogleSuccess = async (credentialResponse: any) => {
    setError('')
    setIsLoading(true)

    try {
      const response = await authAPI.googleLogin(credentialResponse.credential)
      login(response.access_token, response.user!)
      navigate('/')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Google login failed')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 to-blue-800 dark:from-slate-900 dark:to-slate-800 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo and Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <div className="text-blue-300 text-4xl font-bold">E</div>
            <div className="text-white text-2xl font-bold">Cell Portal</div>
          </div>
          <p className="text-blue-100">Task Management & Submission System</p>
        </div>

        {/* Card */}
        <div className="bg-white dark:bg-slate-900 rounded-2xl shadow-xl p-8">
          {error && (
            <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start space-x-3">
              <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
              <p className="text-red-700 dark:text-red-300 text-sm">{error}</p>
            </div>
          )}

          {/* Mode Toggle */}
          <div className="flex rounded-lg bg-slate-100 dark:bg-slate-800 p-1 mb-6">
            <button
              onClick={() => {
                setIsAdminMode(false)
                setError('')
              }}
              className={`flex-1 py-2 rounded font-medium transition-colors ${
                !isAdminMode
                  ? 'bg-white dark:bg-slate-700 text-blue-600 dark:text-blue-400 shadow'
                  : 'text-slate-600 dark:text-slate-400'
              }`}
            >
              Google Login
            </button>
            <button
              onClick={() => {
                setIsAdminMode(true)
                setError('')
              }}
              className={`flex-1 py-2 rounded font-medium transition-colors ${
                isAdminMode
                  ? 'bg-white dark:bg-slate-700 text-blue-600 dark:text-blue-400 shadow'
                  : 'text-slate-600 dark:text-slate-400'
              }`}
            >
              Admin
            </button>
          </div>

          {/* Google Login */}
          {!isAdminMode && (
            <div className="space-y-4">
              <p className="text-sm text-slate-600 dark:text-slate-400 text-center">
                Login with your E-Cell email account
              </p>
              <div className="flex justify-center">
                <GoogleLogin
                  onSuccess={handleGoogleSuccess}
                  onError={() => setError('Google login failed')}
                  theme="filled_black"
                />
              </div>
              <p className="text-xs text-slate-500 dark:text-slate-500 text-center mt-4">
                Only emails from klecba.edu.in, kle.ac.in, and klecba.edu domains are allowed
              </p>
            </div>
          )}

          {/* Admin Login */}
          {isAdminMode && (
            <form onSubmit={handleAdminLogin} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Email
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 w-5 h-5 text-slate-400" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="admin@ecell.com"
                    className="input-field pl-10"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 w-5 h-5 text-slate-400" />
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="input-field pl-10"
                    required
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full btn-primary"
              >
                {isLoading ? 'Logging in...' : 'Login as Admin'}
              </button>
            </form>
          )}
        </div>

        {/* Footer */}
        <p className="text-center text-blue-100 text-sm mt-6">
          © 2026 E-Cell Task Portal. All rights reserved.
        </p>
      </div>
    </div>
  )
}
