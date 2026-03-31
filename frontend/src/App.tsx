import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { Login } from './pages/Login'
import { Register } from './pages/Register'
import { Dashboard } from './pages/Dashboard'
import { AddCamera } from './pages/AddCamera'
import { OrganizationSetup } from './pages/OrganizationSetup'
import { ProtectedRoute } from './components/ProtectedRoute'
import { initializeAPI } from './api/client'
import { useAuthStore } from './store/authStore'
import { useEffect } from 'react'
import './index.css'

function App() {
  const { accessToken } = useAuthStore()

  useEffect(() => {
    if (accessToken) {
      initializeAPI()
    }
  }, [accessToken])

  return (
    <Router>
      <Toaster position="top-right" />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/setup" element={<OrganizationSetup />} />

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/cameras/new"
          element={
            <ProtectedRoute>
              <AddCamera />
            </ProtectedRoute>
          }
        />

        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </Router>
  )
}

export default App
