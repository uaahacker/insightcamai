import React, { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { cameraAPI } from '../api/client'
import { Navbar } from '../components/Navbar'
import { Form, Input, Button } from '../components/FormComponents'
import toast from 'react-hot-toast'

export const AddCamera: React.FC = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const orgSlug = searchParams.get('org')
  const [testResult, setTestResult] = useState<any>(null)

  const handleTestConnection = async (data: any) => {
    try {
      const response = await cameraAPI.testConnection({
        connection_type: data.connectionType,
        host: data.host,
        port: parseInt(data.port),
        username: data.username,
        password: data.password,
        stream_path: data.streamPath,
        stream_protocol: data.streamProtocol || 'rtsp',
      })
      setTestResult(response.data)
      if (response.data.success) {
        toast.success('Connection successful!')
      } else {
        toast.error(`Connection failed: ${response.data.message}`)
      }
    } catch (error: any) {
      toast.error('Error testing connection')
    }
  }

  const handleSubmit = async (data: any) => {
    try {
      await cameraAPI.create(orgSlug || '', {
        name: data.name,
        description: data.description,
        connection_type: data.connectionType,
        host: data.host,
        port: parseInt(data.port),
        username: data.username,
        password: data.password,
        stream_path: data.streamPath,
        stream_protocol: data.streamProtocol || 'rtsp',
        analytics_enabled: data.analyticsEnabled === 'true',
        people_counting: true,
      })
      toast.success('Camera added successfully!')
      navigate('/cameras')
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to add camera')
    }
  }

  return (
    <div>
      <Navbar />
      <div className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Add New Camera</h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Add Camera Form */}
          <div className="card">
            <Form onSubmit={handleSubmit}>
              <Input name="name" type="text" label="Camera Name" placeholder="Front Entrance" required />
              <Input name="description" type="text" label="Description" placeholder="Optional description" />

              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Connection Type</label>
                <select name="connectionType" className="input" defaultValue="rtsp" required>
                  <option value="rtsp">RTSP</option>
                  <option value="http_mjpeg">HTTP MJPEG</option>
                  <option value="dvr_nvr">DVR/NVR</option>
                </select>
              </div>

              <Input name="host" type="text" label="Host/IP Address" placeholder="192.168.1.100" required />
              <Input name="port" type="number" label="Port" placeholder="554" defaultValue="554" required />
              <Input name="username" type="text" label="Username (Optional)" placeholder="admin" />
              <Input name="password" type="password" label="Password (Optional)" placeholder="••••••••" />
              <Input name="streamPath" type="text" label="Stream Path" placeholder="/Streaming/channels/101" />

              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Analytics Enabled</label>
                <select name="analyticsEnabled" className="input" defaultValue="true">
                  <option value="true">Yes</option>
                  <option value="false">No</option>
                </select>
              </div>

              <Button type="submit" className="w-full">Add Camera</Button>
            </Form>
          </div>

          {/* Test Connection */}
          <div className="card">
            <h2 className="text-xl font-bold mb-4">Test Connection</h2>
            <Form onSubmit={handleTestConnection}>
              <Input name="connectionType" type="hidden" defaultValue="rtsp" />
              <Input name="host" type="text" label="Host" placeholder="192.168.1.100" required />
              <Input name="port" type="number" label="Port" defaultValue="554" required />
              <Input name="username" type="text" label="Username" placeholder="admin" />
              <Input name="password" type="password" label="Password" placeholder="••••••••" />
              <Input name="streamPath" type="text" label="Stream Path" placeholder="/Streaming/channels/101" />
              <Button type="submit" className="w-full">Test Connection</Button>
            </Form>

            {testResult && (
              <div className={`mt-4 p-4 rounded ${testResult.success ? 'bg-green-100' : 'bg-red-100'}`}>
                <p className={testResult.success ? 'text-green-800' : 'text-red-800'}>
                  {testResult.success ? '✓ ' : '✗ '}
                  {testResult.message}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
