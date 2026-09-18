import client from './client'
import { Task, Submission, Analytics } from '../types'

export const tasksAPI = {
  // Admin endpoints
  createTask: async (task: Omit<Task, 'id' | 'created_by' | 'created_at' | 'updated_at'>): Promise<{ id: string; message: string }> => {
    const response = await client.post('/api/tasks/', task)
    return response.data
  },

  getAllTasks: async (stage?: string): Promise<Task[]> => {
    const params = stage ? { stage } : {}
    const response = await client.get('/api/tasks/admin/all', { params })
    return response.data
  },

  updateTask: async (taskId: string, updates: Partial<Task>): Promise<{ message: string }> => {
    const response = await client.put(`/api/tasks/${taskId}`, updates)
    return response.data
  },

  deleteTask: async (taskId: string): Promise<{ message: string }> => {
    const response = await client.delete(`/api/tasks/${taskId}`)
    return response.data
  },

  getTaskSubmissions: async (taskId: string): Promise<Submission[]> => {
    const response = await client.get(`/api/tasks/admin/submissions/${taskId}`)
    return response.data
  },

  gradeSubmission: async (submissionId: string, points: number, feedback?: string): Promise<{ message: string }> => {
    const response = await client.post(`/api/tasks/submissions/${submissionId}/grade`, {
      points,
      feedback,
    })
    return response.data
  },

  getAnalytics: async (): Promise<Analytics> => {
    const response = await client.get('/api/tasks/admin/analytics')
    return response.data
  },

  // Participant endpoints
  getTasksByStage: async (stage: string): Promise<Task[]> => {
    const response = await client.get(`/api/tasks/participant/by-stage/${stage}`)
    return response.data
  },

  getAllParticipantTasks: async (): Promise<Task[]> => {
    const response = await client.get('/api/tasks/participant/all')
    return response.data
  },

  getTask: async (taskId: string): Promise<Task> => {
    const response = await client.get(`/api/tasks/${taskId}`)
    return response.data
  },

  // Submission endpoints
  createSubmission: async (taskId: string, fileName: string): Promise<{ id: string; message: string }> => {
    const response = await client.post(`/api/tasks/submissions/${taskId}`, {
      task_id: taskId,
      file_name: fileName,
    })
    return response.data
  },

  getSubmission: async (taskId: string): Promise<Submission | null> => {
    const response = await client.get(`/api/tasks/submissions/${taskId}`)
    return response.data
  },
}
