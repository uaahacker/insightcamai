import React from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { authAPI, initializeAPI } from '../api/client'
import { Form, Input, Button } from '../components/FormComponents'
import toast from 'react-hot-toast'

export const Register: React.FC = () => {
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()

  const handleSubmit = async (data: any) => {
    try {
      if (data.password !== data.confirmPassword) {
        throw new Error('Passwords do not match')
      }

      await authAPI.register(
        data.email,
        data.password,
        data.firstName,
        data.lastName
      )

      // Login after registration
      const loginResponse = await authAPI.login(data.email, data.password)
      setAuth(loginResponse.data.user, loginResponse.data.access, loginResponse.data.refresh)
      initializeAPI()

      toast.success('Registration successful!')
      navigate('/dashboard')
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'Registration failed')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="card w-full max-w-md">
        <h1 className="text-2xl font-bold mb-6">Create Account</h1>
        <Form onSubmit={handleSubmit}>
          <Input name="email" type="email" label="Email" placeholder="your@email.com" required />
          <Input name="firstName" type="text" label="First Name" placeholder="John" required />
          <Input name="lastName" type="text" label="Last Name" placeholder="Doe" required />
          <Input name="password" type="password" label="Password" placeholder="••••••••" required />
          <Input name="confirmPassword" type="password" label="Confirm Password" placeholder="••••••••" required />
          <Button type="submit" className="w-full">Register</Button>
        </Form>
        <p className="text-center mt-4">
          Already have an account?{' '}
          <a href="/login" className="text-blue-600 hover:underline">
            Login here
          </a>
        </p>
      </div>
    </div>
  )
}
