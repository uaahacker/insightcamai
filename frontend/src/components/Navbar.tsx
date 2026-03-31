import React from 'react'
import { Link } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { useOrganizationStore } from '../store/organizationStore'
import { FiLogOut, FiSettings } from 'react-icons/fi'

export const Navbar: React.FC = () => {
  const { user, logout } = useAuthStore()
  const { currentOrganization } = useOrganizationStore()

  return (
    <nav className="bg-white shadow">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="flex items-center">
            <span className="text-xl font-bold text-blue-600">CCTV Analytics</span>
          </Link>

          <div className="flex items-center space-x-4">
            {currentOrganization && (
              <span className="text-gray-600">{currentOrganization.name}</span>
            )}
            <span className="text-gray-600">{user?.email}</span>
            <button
              onClick={logout}
              className="p-2 rounded-lg hover:bg-gray-100 text-gray-600"
              title="Logout"
            >
              <FiLogOut size={20} />
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}
