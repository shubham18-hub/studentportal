export interface User {
  id: string
  email: string
  name: string
  role: 'student' | 'faculty' | 'admin'
  theme_preference?: 'light' | 'dark'
}

export interface Task {
  id: string
  title: string
  description: string
  guidelines: string
  stage: 'Preliminary' | 'Ignite Propel' | 'Comprehensive'
  deadline: string
  max_points: number
  file_required: boolean
  created_by: string
  created_at: string
  updated_at: string
  submission_status?: 'Not Submitted' | 'Submitted' | 'Graded'
  submission_id?: string
}

export interface Submission {
  id: string
  task_id: string
  user_id: string
  file_url?: string
  file_name?: string
  status: 'Not Submitted' | 'Submitted' | 'Graded'
  submitted_at?: string
  points?: number
  feedback?: string
  graded_at?: string
  graded_by?: string
  created_at: string
  updated_at: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  user: User
}

export interface Analytics {
  total_tasks: number
  total_submissions: number
  graded_submissions: number
  pending_grading: number
  submission_status_breakdown: Record<string, number>
}
