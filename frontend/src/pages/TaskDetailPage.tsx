import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Calendar, Award, FileText, Upload, CheckCircle, AlertCircle, Loader, ArrowLeft } from 'lucide-react'
import { Task, Submission } from '../types'
import { tasksAPI } from '../api/tasks'

export default function TaskDetailPage() {
  const { taskId } = useParams<{ taskId: string }>()
  const navigate = useNavigate()
  const [task, setTask] = useState<Task | null>(null)
  const [submission, setSubmission] = useState<Submission | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [fileName, setFileName] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    fetchTaskAndSubmission()
  }, [taskId])

  const fetchTaskAndSubmission = async () => {
    setIsLoading(true)
    setError('')
    try {
      const taskData = await tasksAPI.getTask(taskId!)
      setTask(taskData)
      
      const submissionData = await tasksAPI.getSubmission(taskId!)
      setSubmission(submissionData)
    } catch (err: any) {
      setError('Failed to load task details')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      if (file.type === 'application/pdf' && file.size <= 10 * 1024 * 1024) {
        setFileName(file.name)
        setError('')
      } else {
        setError('Please select a PDF file (max 10MB)')
      }
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!fileName) {
      setError('Please select a file')
      return
    }

    setIsSubmitting(true)
    try {
      await tasksAPI.createSubmission(taskId!, fileName)
      setFileName('')
      await fetchTaskAndSubmission()
    } catch (err: any) {
      setError('Failed to submit file')
      console.error(err)
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center">
        <Loader className="w-8 h-8 text-blue-600 animate-spin" />
      </div>
    )
  }

  if (!task) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 p-4">
        <div className="max-w-3xl mx-auto">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center space-x-2 text-blue-600 hover:text-blue-700 mb-6"
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Back</span>
          </button>
          <p className="text-slate-600 dark:text-slate-400">Task not found</p>
        </div>
      </div>
    )
  }

  const isOverdue = new Date(task.deadline) < new Date()

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 py-8 px-4">
      <div className="max-w-3xl mx-auto">
        {/* Back Button */}
        <button
          onClick={() => navigate(-1)}
          className="flex items-center space-x-2 text-blue-600 hover:text-blue-700 mb-6"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Back</span>
        </button>

        {/* Task Status Card */}
        <div className="card mb-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">
                {task.title}
              </h1>
              <p className="text-slate-600 dark:text-slate-400">{task.description}</p>
            </div>
            <span className={`px-4 py-2 rounded-lg font-medium text-sm ${
              submission?.status === 'Graded'
                ? 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300'
                : submission?.status === 'Submitted'
                ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                : 'bg-yellow-100 dark:bg-yellow-900 text-yellow-700 dark:text-yellow-300'
            }`}>
              {submission?.status || 'Not Submitted'}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 py-4 border-t border-slate-200 dark:border-slate-700">
            <div>
              <p className="text-sm text-slate-600 dark:text-slate-400 mb-1">Deadline</p>
              <div className="flex items-center space-x-2 text-slate-900 dark:text-white">
                <Calendar className="w-5 h-5 text-blue-600" />
                <span className={isOverdue ? 'text-red-600 font-medium' : ''}>
                  {new Date(task.deadline).toLocaleDateString()}
                </span>
              </div>
              {isOverdue && (
                <p className="text-xs text-red-600 dark:text-red-400 mt-1">Overdue</p>
              )}
            </div>
            <div>
              <p className="text-sm text-slate-600 dark:text-slate-400 mb-1">Points</p>
              <div className="flex items-center space-x-2 text-slate-900 dark:text-white">
                <Award className="w-5 h-5 text-blue-600" />
                <span>-/{task.max_points}</span>
              </div>
              {submission?.points !== undefined && (
                <p className="text-xs text-green-600 dark:text-green-400 mt-1">
                  Graded: {submission.points}/{task.max_points}
                </p>
              )}
            </div>
            <div>
              <p className="text-sm text-slate-600 dark:text-slate-400 mb-1">Stage</p>
              <div className="text-slate-900 dark:text-white font-medium">{task.stage}</div>
            </div>
          </div>
        </div>

        {/* Guidelines */}
        <div className="card mb-6">
          <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-4 flex items-center space-x-2">
            <FileText className="w-6 h-6 text-blue-600" />
            <span>Guidelines</span>
          </h2>
          <div className="prose dark:prose-invert prose-sm max-w-none">
            <p className="text-slate-700 dark:text-slate-300 whitespace-pre-wrap">
              {task.guidelines}
            </p>
          </div>
        </div>

        {/* Current Submission */}
        {submission && (
          <div className="card mb-6">
            <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-4">
              Current Submission
            </h2>
            <div className="space-y-3">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-slate-600 dark:text-slate-400 mb-1">
                    File
                  </p>
                  <p className="text-slate-900 dark:text-white font-medium">
                    {submission.file_name}
                  </p>
                </div>
                {submission.file_url && (
                  <a
                    href={submission.file_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn-primary text-sm"
                  >
                    View PDF
                  </a>
                )}
              </div>
              {submission.submitted_at && (
                <div className="flex items-center space-x-2 text-sm text-slate-600 dark:text-slate-400">
                  <CheckCircle className="w-4 h-4 text-green-600" />
                  <span>Submitted {new Date(submission.submitted_at).toLocaleString()}</span>
                </div>
              )}
              {submission.feedback && (
                <div className="mt-4 p-4 bg-slate-100 dark:bg-slate-800 rounded-lg">
                  <p className="text-sm font-medium text-slate-900 dark:text-white mb-2">
                    Feedback
                  </p>
                  <p className="text-slate-700 dark:text-slate-300">
                    {submission.feedback}
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Submit Form */}
        {submission?.status !== 'Graded' && (
          <div className="card">
            <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-6 flex items-center space-x-2">
              <Upload className="w-6 h-6 text-blue-600" />
              <span>Submit Your Work</span>
            </h2>

            {error && (
              <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start space-x-3">
                <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                <p className="text-red-700 dark:text-red-300 text-sm">{error}</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="border-2 border-dashed border-slate-300 dark:border-slate-600 rounded-lg p-8 text-center hover:border-blue-600 transition-colors cursor-pointer group">
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handleFileChange}
                  className="hidden"
                  id="file-input"
                />
                <label htmlFor="file-input" className="cursor-pointer">
                  <Upload className="w-12 h-12 text-blue-600 mx-auto mb-3 group-hover:scale-110 transition-transform" />
                  <p className="text-slate-900 dark:text-white font-medium">
                    {fileName || 'Choose a file or drag it here'}
                  </p>
                  <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
                    PDF files only (max 10MB)
                  </p>
                </label>
              </div>

              <button
                type="submit"
                disabled={!fileName || isSubmitting}
                className="w-full btn-primary text-lg font-medium py-3"
              >
                {isSubmitting ? 'Submitting...' : 'Submit Task'}
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  )
}
