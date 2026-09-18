import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Loader, AlertCircle, CheckCircle, FileText } from 'lucide-react'
import { Task, Submission } from '../types'
import { tasksAPI } from '../api/tasks'

export default function GradeSubmissionsPage() {
  const { taskId } = useParams<{ taskId: string }>()
  const navigate = useNavigate()
  const [task, setTask] = useState<Task | null>(null)
  const [submissions, setSubmissions] = useState<Submission[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [gradingId, setGradingId] = useState<string | null>(null)
  const [gradingData, setGradingData] = useState({ points: 0, feedback: '' })
  const [isSubmittingGrade, setIsSubmittingGrade] = useState(false)

  useEffect(() => {
    fetchData()
  }, [taskId])

  const fetchData = async () => {
    setIsLoading(true)
    setError('')
    try {
      const taskData = await tasksAPI.getTask(taskId!)
      setTask(taskData)
      
      const submissionsData = await tasksAPI.getTaskSubmissions(taskId!)
      setSubmissions(submissionsData)
    } catch (err: any) {
      setError('Failed to load submissions')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  const handleGradeSubmit = async (submissionId: string) => {
    if (!gradingData.points || gradingData.points < 0) {
      setError('Please enter valid points')
      return
    }

    setIsSubmittingGrade(true)
    try {
      await tasksAPI.gradeSubmission(
        submissionId,
        gradingData.points,
        gradingData.feedback
      )
      setGradingId(null)
      setGradingData({ points: 0, feedback: '' })
      await fetchData()
    } catch (err: any) {
      setError('Failed to grade submission')
      console.error(err)
    } finally {
      setIsSubmittingGrade(false)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center">
        <Loader className="w-8 h-8 text-blue-600 animate-spin" />
      </div>
    )
  }

  const ungradedSubmissions = submissions.filter((s) => s.status !== 'Graded')
  const gradedSubmissions = submissions.filter((s) => s.status === 'Graded')

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Back Button */}
        <button
          onClick={() => navigate('/admin')}
          className="flex items-center space-x-2 text-blue-600 hover:text-blue-700 mb-6"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Back to Dashboard</span>
        </button>

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">
            Grade Submissions
          </h1>
          {task && (
            <p className="text-slate-600 dark:text-slate-400">
              {task.title} — {submissions.length} total submissions
            </p>
          )}
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
            <p className="text-red-700 dark:text-red-300">{error}</p>
          </div>
        )}

        {/* Ungraded Submissions */}
        <div className="mb-8">
          <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-4">
            Pending Review ({ungradedSubmissions.length})
          </h2>
          {ungradedSubmissions.length === 0 ? (
            <p className="text-slate-600 dark:text-slate-400">No pending submissions</p>
          ) : (
            <div className="space-y-4">
              {ungradedSubmissions.map((submission) => (
                <div key={submission.id} className="card">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <p className="font-medium text-slate-900 dark:text-white">
                        {submission.file_name}
                      </p>
                      <p className="text-sm text-slate-600 dark:text-slate-400">
                        Submitted{' '}
                        {submission.submitted_at &&
                          new Date(submission.submitted_at).toLocaleString()}
                      </p>
                    </div>
                    {submission.file_url && (
                      <a
                        href={submission.file_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center space-x-2 text-blue-600 hover:text-blue-700"
                      >
                        <FileText className="w-5 h-5" />
                        <span>View</span>
                      </a>
                    )}
                  </div>

                  {gradingId === submission.id ? (
                    <div className="space-y-4 pt-4 border-t border-slate-200 dark:border-slate-700">
                      <div>
                        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                          Points ({task?.max_points} max)
                        </label>
                        <input
                          type="number"
                          value={gradingData.points}
                          onChange={(e) =>
                            setGradingData((prev) => ({
                              ...prev,
                              points: parseInt(e.target.value) || 0,
                            }))
                          }
                          min="0"
                          max={task?.max_points}
                          className="input-field"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                          Feedback (optional)
                        </label>
                        <textarea
                          value={gradingData.feedback}
                          onChange={(e) =>
                            setGradingData((prev) => ({
                              ...prev,
                              feedback: e.target.value,
                            }))
                          }
                          placeholder="Enter feedback for the student"
                          rows={3}
                          className="input-field resize-none"
                        />
                      </div>
                      <div className="flex space-x-3">
                        <button
                          onClick={() =>
                            handleGradeSubmit(submission.id)
                          }
                          disabled={isSubmittingGrade}
                          className="flex-1 btn-primary"
                        >
                          {isSubmittingGrade ? 'Submitting...' : 'Submit Grade'}
                        </button>
                        <button
                          onClick={() => setGradingId(null)}
                          className="flex-1 btn-secondary"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <button
                      onClick={() => {
                        setGradingId(submission.id)
                        setGradingData({ points: 0, feedback: '' })
                      }}
                      className="w-full btn-primary py-2 text-sm mt-4"
                    >
                      Grade Submission
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Graded Submissions */}
        <div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-4">
            Completed ({gradedSubmissions.length})
          </h2>
          {gradedSubmissions.length === 0 ? (
            <p className="text-slate-600 dark:text-slate-400">No graded submissions yet</p>
          ) : (
            <div className="space-y-3">
              {gradedSubmissions.map((submission) => (
                <div
                  key={submission.id}
                  className="card flex items-start justify-between"
                >
                  <div>
                    <div className="flex items-center space-x-2 mb-2">
                      <CheckCircle className="w-5 h-5 text-green-600" />
                      <p className="font-medium text-slate-900 dark:text-white">
                        {submission.file_name}
                      </p>
                    </div>
                    <p className="text-sm text-slate-600 dark:text-slate-400">
                      Points: {submission.points}/{task?.max_points}
                    </p>
                    {submission.feedback && (
                      <p className="text-sm text-slate-600 dark:text-slate-400 mt-2">
                        Feedback: {submission.feedback}
                      </p>
                    )}
                  </div>
                  {submission.file_url && (
                    <a
                      href={submission.file_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center space-x-2 text-blue-600 hover:text-blue-700 flex-shrink-0 ml-4"
                    >
                      <FileText className="w-5 h-5" />
                      <span>View</span>
                    </a>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
