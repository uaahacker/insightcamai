import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useOrganizationStore } from '../store/organizationStore'
import { organizationAPI } from '../api/client'
import { Navbar } from '../components/Navbar'
import { Form, Input, Button } from '../components/FormComponents'
import toast from 'react-hot-toast'

export const OrganizationSetup: React.FC = () => {
  const navigate = useNavigate()
  const { setCurrentOrganization } = useOrganizationStore()

  const handleSubmit = async (data: any) => {
    try {
      const response = await organizationAPI.create({
        name: data.name,
        description: data.description,
        website: data.website,
        industry: data.industry,
        country: data.country,
        city: data.city,
        owns_cameras: data.ownsCameras === 'true',
        privacy_confirmed: data.privacyConfirmed === 'true',
      })

      if (!data.privacyConfirmed || data.privacyConfirmed !== 'true') {
        throw new Error('You must confirm privacy and legal terms')
      }

      setCurrentOrganization(response.data)
      toast.success('Organization created successfully!')
      navigate('/dashboard')
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to create organization')
    }
  }

  return (
    <div>
      <Navbar />
      <div className="max-w-2xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-2">Set Up Your Organization</h1>
        <p className="text-gray-600 mb-8">Let's get your CCTV analytics platform ready to use</p>

        <div className="card">
          <Form onSubmit={handleSubmit}>
            <Input
              name="name"
              type="text"
              label="Organization Name"
              placeholder="Your Company Name"
              required
            />
            <Input
              name="description"
              type="text"
              label="Description"
              placeholder="What does your organization do?"
            />
            <Input
              name="website"
              type="url"
              label="Website (Optional)"
              placeholder="https://example.com"
            />

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <Input
                name="industry"
                type="text"
                label="Industry"
                placeholder="Retail, Warehouse, etc."
              />
              <Input
                name="country"
                type="text"
                label="Country"
                placeholder="United States"
              />
            </div>

            <Input
              name="city"
              type="text"
              label="City"
              placeholder="New York"
            />

            <div className="mb-6 p-4 bg-blue-50 rounded-lg">
              <label className="flex items-start space-x-3">
                <input
                  type="checkbox"
                  name="ownsCameras"
                  value="true"
                  required
                  className="mt-1"
                />
                <span className="text-sm">
                  <strong>I confirm</strong> that I own or am authorized to use all CCTV cameras connected to this system.
                </span>
              </label>
            </div>

            <div className="mb-6 p-4 bg-blue-50 rounded-lg">
              <label className="flex items-start space-x-3">
                <input
                  type="checkbox"
                  name="privacyConfirmed"
                  value="true"
                  required
                  className="mt-1"
                />
                <span className="text-sm">
                  <strong>I agree</strong> that camera footage is processed only for analytics purposes. No facial recognition is enabled by default.
                </span>
              </label>
            </div>

            <Button type="submit" className="w-full">Create Organization</Button>
          </Form>
        </div>
      </div>
    </div>
  )
}
