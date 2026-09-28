/**
 * SmartERP Login Page — modern dark theme with glassmorphism.
 */
import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { Eye, EyeOff, Loader2, Zap } from 'lucide-react'
import toast from 'react-hot-toast'

import { authApi } from '@/api/auth'
import { useAuthStore } from '@/features/auth/authStore'
import type { LoginRequest, TokenResponse } from '@/types'

export default function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const { setTokens, setUser, isAuthenticated } = useAuthStore()
  const from = (location.state as { from?: string })?.from || '/dashboard'

  const [form, setForm] = useState<LoginRequest>({ email: '', password: '' })
  const [showPassword, setShowPassword] = useState(false)
  const [errors, setErrors] = useState<Partial<LoginRequest>>({})

  useEffect(() => {
    if (isAuthenticated) navigate(from, { replace: true })
  }, [isAuthenticated, navigate, from])

  const loginMutation = useMutation({
    mutationFn: authApi.login,
    onSuccess: async (tokens: TokenResponse) => {
      setTokens(tokens.access_token, tokens.refresh_token)
      try {
        const user = await authApi.me()
        setUser(user)
      } catch {
        // user info will load on next navigation
      }
      toast.success('Welcome back!')
      navigate(from, { replace: true })
    },
    onError: (error: any) => {
      const msg =
        error?.response?.data?.message || 'Invalid email or password'
      toast.error(msg)
    },
  })

  const validate = (): boolean => {
    const errs: Partial<LoginRequest> = {}
    if (!form.email) errs.email = 'Email is required'
    else if (!/\S+@\S+\.\S+/.test(form.email)) errs.email = 'Invalid email address'
    if (!form.password) errs.password = 'Password is required'
    setErrors(errs)
    return Object.keys(errs).length === 0
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!validate()) return
    loginMutation.mutate(form)
  }

  return (
    <div className="min-h-screen bg-dark-950 flex items-center justify-center relative overflow-hidden">
      {/* Background gradient orbs */}
      <div className="absolute top-1/4 -left-32 w-96 h-96 bg-primary-600/20 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 -right-32 w-96 h-96 bg-indigo-600/15 rounded-full blur-3xl pointer-events-none" />

      <div className="w-full max-w-md mx-4 relative z-10">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-primary-600 shadow-glow mb-4">
            <Zap className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white">SmartERP</h1>
          <p className="text-dark-400 mt-1 text-sm">AI-Powered Enterprise Platform</p>
        </div>

        {/* Card */}
        <div className="card border-dark-700/80 shadow-xl shadow-black/30">
          <h2 className="text-xl font-semibold text-dark-50 mb-6">Sign in to your account</h2>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Email */}
            <div>
              <label htmlFor="email" className="label">Email address</label>
              <input
                id="email"
                type="email"
                autoComplete="email"
                autoFocus
                className={`input ${errors.email ? 'input-error' : ''}`}
                placeholder="admin@smarterp.com"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
              />
              {errors.email && (
                <p className="mt-1.5 text-xs text-red-400">{errors.email}</p>
              )}
            </div>

            {/* Password */}
            <div>
              <label htmlFor="password" className="label">Password</label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  className={`input pr-11 ${errors.password ? 'input-error' : ''}`}
                  placeholder="••••••••"
                  value={form.password}
                  onChange={(e) => setForm({ ...form, password: e.target.value })}
                />
                <button
                  type="button"
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-dark-400 hover:text-dark-200 transition-colors"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {errors.password && (
                <p className="mt-1.5 text-xs text-red-400">{errors.password}</p>
              )}
            </div>

            {/* Submit */}
            <button
              type="submit"
              className="btn-primary w-full btn-lg mt-2"
              disabled={loginMutation.isPending}
            >
              {loginMutation.isPending ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Signing in...
                </>
              ) : (
                'Sign in'
              )}
            </button>
          </form>

          {/* Demo credentials */}
          <div className="mt-6 p-4 rounded-lg bg-dark-900/60 border border-dark-700">
            <p className="text-xs font-medium text-dark-400 mb-2">Demo credentials</p>
            <p className="text-xs text-dark-300">
              Email: <span className="text-primary-400 font-mono">admin@smarterp.com</span>
            </p>
            <p className="text-xs text-dark-300">
              Password: <span className="text-primary-400 font-mono">Admin@12345!</span>
            </p>
          </div>
        </div>

        <p className="text-center text-xs text-dark-500 mt-6">
          © {new Date().getFullYear()} SmartERP. All rights reserved.
        </p>
      </div>
    </div>
  )
}
