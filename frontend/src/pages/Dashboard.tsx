import React, { useEffect, useState } from 'react'
import { Navbar } from '../components/Navbar'
import { useOrganizationStore } from '../store/organizationStore'
import { organizationAPI } from '../api/client'
import { Link } from 'react-router-dom'
import { FiPlus, FiBarChart3, FiAlertCircle, FiCamera } from 'react-icons/fi'
import toast from 'react-hot-toast'

export const Dashboard: React.FC = () => {
  const { currentOrganization } = useOrganizationStore()
  const [stats, setStats] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const loadStats = async () => {
      if (!currentOrganization) return

      try {
        // In a real app, we'd fetch actual stats
        setStats({
          totalCameras: 5,
          onlineCameras: 4,
          offlineCameras: 1,
          eventsToday: 23,
          alertsToday: 3,
          peopleCounted: 145,
        })
      } catch (error) {
        toast.error('Failed to load dashboard')
      } finally {
        setIsLoading(false)
      }
    }

    loadStats()
  }, [currentOrganization])

  if (!currentOrganization) {
    return (
      <div className="">
        <Navbar />
        <div className="max-w-7xl mx-auto px-4 py-8">
          <p className="text-center text-gray-600">Please select an organization</p>
        </div>
      </div>
    )
  }

  return (
    <div className="">
      <Navbar />
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
          <p className="text-gray-600">{currentOrganization.name}</p>
        </div>

        {isLoading ? (
          <div className="text-center py-12">
            <p className="text-gray-600">Loading...</p>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
              {/* Camera Stats */}
              <div className="card">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-600 text-sm">Total Cameras</p>
                    <p className="text-3xl font-bold">{stats?.totalCameras}</p>
                    <p className="text-green-600 text-sm">{stats?.onlineCameras} online</p>
                  </div>
                  <FiCamera size={40} className="text-blue-600" />
                </div>
              </div>

              {/* Events Stats */}
              <div className="card">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-600 text-sm">Events Today</p>
                    <p className="text-3xl font-bold">{stats?.eventsToday}</p>
                    <p className="text-gray-600 text-sm">Last 24 hours</p>
                  </div>
                  <FiBarChart3 size={40} className="text-purple-600" />
                </div>
              </div>

              {/* Alerts Stats */}
              <div className="card">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-600 text-sm">Alerts Today</p>
                    <p className="text-3xl font-bold">{stats?.alertsToday}</p>
                    <p className="text-red-600 text-sm">Requires attention</p>
                  </div>
                  <FiAlertCircle size={40} className="text-red-600" />
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="card">
              <h2 className="text-xl font-bold mb-4">Quick Actions</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <Link to={`/cameras/new?org=${currentOrganization.slug}`} className="btn btn-primary">
                  <FiPlus className="mr-2" />
                  Add Camera
                </Link>
                <Link to="/cameras" className="btn btn-secondary">
                  View Cameras
                </Link>
                <Link to="/alerts" className="btn btn-secondary">
                  View Alerts
                </Link>
                <Link to="/rules" className="btn btn-secondary">
                  Manage Rules
                </Link>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
