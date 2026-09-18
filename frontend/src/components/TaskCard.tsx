import { useNavigate } from 'react-router-dom'
import { Calendar, Award, ChevronRight, AlertCircle } from 'lucide-react'
import { Task } from '../types'

interface TaskCardProps {
  task: Task
  onClick?: () => void
}

export function TaskCard({ task, onClick }: TaskCardProps) {
  const navigate = useNavigate()
  const isOverdue = new Date(task.deadline) < new Date()
  const statusColor = {
    'Not Submitted': 'bg-yellow-100 dark:bg-yellow-900 text-yellow-700 dark:text-yellow-200',
    'Submitted': 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-200',
    'Graded': 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-200',
  }[task.submission_status || 'Not Submitted']

  const handleClick = () => {
    if (onClick) {
      onClick()
    } else {
      navigate(`/tasks/${task.id}`)
    }
  }

  return (
    <div
      onClick={handleClick}
      className="card cursor-pointer hover:shadow-md transition-shadow"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-1">
            {task.title}
          </h3>
          <p className="text-sm text-slate-600 dark:text-slate-400 line-clamp-2">
            {task.description}
          </p>
        </div>
        <span className={`ml-4 px-3 py-1 rounded-full text-xs font-medium whitespace-nowrap ${statusColor}`}>
          {task.submission_status || 'Not Submitted'}
        </span>
      </div>

      <div className="space-y-2 mb-4">
        <div className="flex items-center text-sm text-slate-600 dark:text-slate-400">
          <Calendar className="w-4 h-4 mr-2 flex-shrink-0" />
          <span>
            {isOverdue && <AlertCircle className="w-4 h-4 mr-1 inline text-red-500" />}
            {new Date(task.deadline).toLocaleDateString()}
          </span>
        </div>
        <div className="flex items-center text-sm text-slate-600 dark:text-slate-400">
          <Award className="w-4 h-4 mr-2 flex-shrink-0" />
          <span>Points: -{task.max_points}</span>
        </div>
      </div>

      <div className="flex items-center justify-between pt-4 border-t border-slate-200 dark:border-slate-700">
        <span className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
          {task.stage}
        </span>
        <ChevronRight className="w-5 h-5 text-blue-600" />
      </div>
    </div>
  )
}
