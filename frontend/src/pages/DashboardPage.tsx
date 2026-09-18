import React, { useState, useEffect } from 'react'
import { Task } from '../types'
import { TaskCard } from '../components/TaskCard'
import { tasksAPI } from '../api/tasks'
import { Loader } from 'lucide-react'

const STAGES = ['Preliminary', 'Ignite Propel', 'Comprehensive']

export default function DashboardPage() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [selectedStage, setSelectedStage] = useState<string>(STAGES[0])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchTasks()
  }, [])

  const fetchTasks = async () => {
    setIsLoading(true)
    setError('')
    try {
      const data = await tasksAPI.getAllParticipantTasks()
      setTasks(data)
    } catch (err: any) {
      setError('Failed to load tasks')
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
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">
            Tasks
          </h1>
          <p className="text-slate-600 dark:text-slate-400">
            Manage your E-Cell tasks and submissions
          </p>
        </div>

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

        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-300">
            {error}
          </div>
        )}

        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader className="w-8 h-8 text-blue-600 animate-spin" />
          </div>
        ) : filteredTasks.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-slate-600 dark:text-slate-400">
              No tasks available for this stage
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredTasks.map((task) => (
              <TaskCard key={task.id} task={task} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
