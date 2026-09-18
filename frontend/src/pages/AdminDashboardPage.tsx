import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Loader, AlertCircle } from 'lucide-react'
import { TaskCard } from '../components/TaskCard'
import { tasksAPI } from '../api/tasks'
import { Task, Analytics } from '../types'

const STAGES = ['Preliminary', 'Ignite Propel', 'Comprehensive']

export default function AdminDashboardPage() {
  const navigate = useNavigate()
  const [tasks, setTasks] = useState<Task[]>([])
  const [analytics, setAnalytics] = useState<Analytics | null>(null)
  const [selectedStage, setSelectedStage] = useState<string>(STAGES[0])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    setIsLoading(true)
    setError('')
    try {
      const [tasksData, analyticsData] = await Promise.all([
        tasksAPI.getAllTasks(),
        tasksAPI.getAnalytics(),
      ])
      setTasks(tasksData)
      setAnalytics(analyticsData)
    } catch (err: any) {
      setError('Failed to load admin dashboard')
      console.error(err)
    } finally {
      setIsLoading(false)
    }
  }

  const filteredTasks = tasks.filter((task) => task.stage === selectedStage)

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">
              Admin Dashboard
            </h1>
            <p className="text-slate-600 dark:text-slate-400">
              Manage tasks and track submissions
            </p>
          </div>
          <button
            onClick={() => navigate('/admin/tasks/create')}
            className="btn-primary flex items-center space-x-2"
          >
            <Plus className="w-5 h-5" />
            <span>Create Task</span>
          </button>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
            <p className="text-red-700 dark:text-red-300">{error}</p>
          </div>
        )}

        {/* Analytics Cards */}
        {analytics && !isLoading && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="card">
              <p className="text-sm text-slate-600 dark:text-slate-400 mb-1">
                Total Tasks
              </p>
              <p className="text-3xl font-bold text-slate-900 dark:text-white">
                {analytics.total_tasks}
              </p>
            </div>
            <div className="card">
              <p className="text-sm text-slate-600 dark:text-slate-400 mb-1">
                Total Submissions
              </p>
              <p className="text-3xl font-bold text-slate-900 dark:text-white">
                {analytics.total_submissions}
              </p>
            </div>
            <div className="card">
              <p className="text-sm text-slate-600 dark:text-slate-400 mb-1">
                Graded
              </p>
              <p className="text-3xl font-bold text-green-600">
                {analytics.graded_submissions}
              </p>
            </div>
            <div className="card">
              <p className="text-sm text-slate-600 dark:text-slate-400 mb-1">
                Pending Grading
              </p>
              <p className="text-3xl font-bold text-yellow-600">
                {analytics.pending_grading}
              </p>
            </div>
          </div>
        )}

        {/* Stage Selector */}
        <div className="mb-8 flex flex-wrap gap-3">
          {STAGES.map((stage) => (
            <button
              key={stage}
              onClick={() => setSelectedStage(stage)}
              className={`px-6 py-3 rounded-full font-medium transition-colors ${
                selectedStage === stage
                  ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg'
                  : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700 hover:border-blue-600 dark:hover:border-blue-600'
              }`}
            >
              {stage}
            </button>
          ))}
        </div>

        {/* Tasks Grid */}
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader className="w-8 h-8 text-blue-600 animate-spin" />
          </div>
        ) : filteredTasks.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-slate-600 dark:text-slate-400">
              No tasks in this stage
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredTasks.map((task) => (
              <div
                key={task.id}
                onClick={() => navigate(`/admin/tasks/${task.id}/submissions`)}
              >
                <TaskCard task={task} />
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
