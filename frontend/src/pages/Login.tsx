import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { authAPI, initializeAPI } from '../api/client'
import { Form, Input, Button } from '../components/FormComponents'
import toast from 'react-hot-toast'

export const Login: React.FC = () => {
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()

  const handleSubmit = async (data: any) => {
    try {
      const response = await authAPI.login(data.email, data.password)
      setAuth(response.data.user, response.data.access, response.data.refresh)
      initializeAPI()
      toast.success('Logged in successfully!')
      navigate('/dashboard')
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Login failed')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="card w-full max-w-md">
        <h1 className="text-2xl font-bold mb-6">Login</h1>
        <Form onSubmit={handleSubmit}>
          <Input name="email" type="email" label="Email" placeholder="your@email.com" required />
          <Input name="password" type="password" label="Password" placeholder="••••••••" required />
          <Button type="submit" className="w-full">Login</Button>
        </Form>
        <p className="text-center mt-4">
          Don't have an account?{' '}
          <a href="/register" className="text-blue-600 hover:underline">
            Register here
          </a>
        </p>
      </div>
    </div>
  )
}
