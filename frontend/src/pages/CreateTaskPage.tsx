import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, AlertCircle, Loader } from 'lucide-react'
import { tasksAPI } from '../api/tasks'

const STAGES = ['Preliminary', 'Ignite Propel', 'Comprehensive']

export default function CreateTaskPage() {
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    guidelines: '',
    stage: STAGES[0],
    deadline: '',
    max_points: 100,
    file_required: true,
  })

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]:
        type === 'checkbox' ? (e.target as HTMLInputElement).checked : value,
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      // Validate form
      if (
        !formData.title ||
        !formData.description ||
        !formData.guidelines ||
        !formData.deadline
      ) {
        setError('Please fill in all required fields')
        setIsLoading(false)
        return
      }

      await tasksAPI.createTask({
        ...formData,
        deadline: new Date(formData.deadline).toISOString(),
      } as any)

      navigate('/admin')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create task')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 py-8 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Back Button */}
        <button
          onClick={() => navigate('/admin')}
          className="flex items-center space-x-2 text-blue-600 hover:text-blue-700 mb-6"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Back</span>
        </button>

        {/* Form Card */}
        <div className="card">
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-6">
            Create New Task
          </h1>

          {error && (
            <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start space-x-3">
              <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
              <p className="text-red-700 dark:text-red-300">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Title */}
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Task Title *
              </label>
              <input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleChange}
                placeholder="e.g., Brand Your E-Cell"
                className="input-field"
                required
              />
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Description *
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                placeholder="Brief description of the task"
                rows={3}
                className="input-field resize-none"
                required
              />
            </div>

            {/* Guidelines */}
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Guidelines *
              </label>
              <textarea
                name="guidelines"
                value={formData.guidelines}
                onChange={handleChange}
                placeholder="Detailed guidelines for the task"
                rows={5}
                className="input-field resize-none"
                required
              />
            </div>

            {/* Stage */}
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Workflow Stage *
              </label>
              <select
                name="stage"
                value={formData.stage}
                onChange={handleChange}
                className="input-field"
                required
              >
                {STAGES.map((stage) => (
                  <option key={stage} value={stage}>
                    {stage}
                  </option>
                ))}
              </select>
            </div>

            {/* Deadline */}
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Deadline *
              </label>
              <input
                type="datetime-local"
                name="deadline"
                value={formData.deadline}
                onChange={handleChange}
                className="input-field"
                required
              />
            </div>

            {/* Max Points */}
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Maximum Points *
              </label>
              <input
                type="number"
                name="max_points"
                value={formData.max_points}
                onChange={handleChange}
                min="1"
                className="input-field"
                required
              />
            </div>

            {/* File Required */}
            <div>
              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  name="file_required"
                  checked={formData.file_required}
                  onChange={handleChange}
                  className="w-4 h-4 text-blue-600 rounded"
                />
                <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                  File submission required
                </span>
              </label>
            </div>

            {/* Submit Button */}
            <div className="flex space-x-4 pt-6">
              <button
                type="submit"
                disabled={isLoading}
                className="flex-1 btn-primary text-lg font-medium py-3 flex items-center justify-center space-x-2"
              >
                {isLoading && <Loader className="w-5 h-5 animate-spin" />}
                <span>{isLoading ? 'Creating...' : 'Create Task'}</span>
              </button>
              <button
                type="button"
                onClick={() => navigate('/admin')}
                className="flex-1 btn-secondary text-lg font-medium py-3"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
