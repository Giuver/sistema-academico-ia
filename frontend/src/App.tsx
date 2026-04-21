import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import Layout from '@/components/Layout'
import LoginPage from '@/pages/LoginPage'
import DashboardPage from '@/pages/DashboardPage'
import EstudiantesPage from '@/pages/EstudiantesPage'
import EstudianteDetailPage from '@/pages/EstudianteDetailPage'
import AlertasPage from '@/pages/AlertasPage'
import ReportesPage from '@/pages/ReportesPage'
import LoadingSpinner from '@/components/common/LoadingSpinner'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()

  if (loading) {
    return <LoadingSpinner fullScreen />
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

function App() {
  const { user, loading } = useAuth()

  if (loading) {
    return <LoadingSpinner fullScreen />
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/login"
          element={user ? <Navigate to="/dashboard" replace /> : <LoginPage />}
        />
        
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="estudiantes" element={<EstudiantesPage />} />
          <Route path="estudiantes/:id" element={<EstudianteDetailPage />} />
          <Route path="alertas" element={<AlertasPage />} />
          <Route path="reportes" element={<ReportesPage />} />
        </Route>

        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
