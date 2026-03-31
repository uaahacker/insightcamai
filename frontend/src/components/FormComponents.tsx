import React from 'react'
import toast from 'react-hot-toast'

interface FormProps {
  children: React.ReactNode
  onSubmit: (data: any) => Promise<void>
  className?: string
}

export const Form: React.FC<FormProps> = ({ children, onSubmit, className = '' }) => {
  const [isLoading, setIsLoading] = React.useState(false)

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      const formData = new FormData(e.currentTarget)
      const data = Object.fromEntries(formData.entries())
      await onSubmit(data)
    } catch (error: any) {
      toast.error(error.message || 'An error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className={className}>
      {React.Children.map(children, (child) => {
        if (React.isValidElement(child)) {
          return React.cloneElement(child as any, { isLoading })
        }
        return child
      })}
    </form>
  )
}

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  isLoading?: boolean
}

export const Input: React.FC<InputProps> = ({
  label,
  error,
  isLoading,
  disabled,
  ...props
}) => {
  return (
    <div className="mb-4">
      {label && <label className="block text-sm font-medium mb-2">{label}</label>}
      <input
        {...props}
        disabled={disabled || isLoading}
        className="input disabled:bg-gray-100 disabled:cursor-not-allowed"
      />
      {error && <p className="text-red-600 text-sm mt-1">{error}</p>}
    </div>
  )
}

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  isLoading?: boolean
  variant?: 'primary' | 'secondary'
}

export const Button: React.FC<ButtonProps> = ({
  isLoading,
  disabled,
  variant = 'primary',
  children,
  ...props
}) => {
  return (
    <button
      {...props}
      disabled={disabled || isLoading}
      className={`btn ${
        variant === 'primary' ? 'btn-primary' : 'btn-secondary'
      } disabled:opacity-50 disabled:cursor-not-allowed`}
    >
      {isLoading ? 'Loading...' : children}
    </button>
  )
}
