import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { ProtectedRoute } from './components/ProtectedRoute'
import { Navbar } from './components/Navbar'

// Pages
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import TaskDetailPage from './pages/TaskDetailPage'
import AdminDashboardPage from './pages/AdminDashboardPage'
import CreateTaskPage from './pages/CreateTaskPage'
import GradeSubmissionsPage from './pages/GradeSubmissionsPage'

function AppContent() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <>
                <Navbar />
                <DashboardPage />
              </>
            </ProtectedRoute>
          }
        />

        <Route
          path="/tasks/:taskId"
          element={
            <ProtectedRoute>
              <>
                <Navbar />
                <TaskDetailPage />
              </>
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin"
          element={
            <ProtectedRoute requiredRole="admin">
              <>
                <Navbar />
                <AdminDashboardPage />
              </>
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/tasks/create"
          element={
            <ProtectedRoute requiredRole="admin">
              <>
                <Navbar />
                <CreateTaskPage />
              </>
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/tasks/:taskId/submissions"
          element={
            <ProtectedRoute requiredRole="admin">
              <>
                <Navbar />
                <GradeSubmissionsPage />
              </>
            </ProtectedRoute>
          }
        />

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  )
}

export default App
