import { useQuery } from '@tanstack/react-query'
import { supabase } from '@/services/supabase'
import { useAuth } from '@/hooks/useAuth'
import { 
  Users, 
  AlertTriangle, 
  TrendingUp, 
  TrendingDown,
  CheckCircle,
  XCircle
} from 'lucide-react'
import LoadingSpinner from '@/components/common/LoadingSpinner'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

export default function DashboardPage() {
  const { perfil } = useAuth()

  // Obtener estadísticas generales
  const { data: stats, isLoading: loadingStats } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const [estudiantesRes, alertasRes, notasRes] = await Promise.all([
        supabase.from('estudiantes').select('id', { count: 'exact', head: true }),
        supabase.from('alertas').select('*').in('estado', ['activa', 'en_atencion']),
        supabase.from('vista_estudiantes_resumen').select('promedio_general')
      ])

      const promedioGeneral = notasRes.data?.reduce((sum, e) => sum + e.promedio_general, 0) / (notasRes.data?.length || 1)

      return {
        totalEstudiantes: estudiantesRes.count || 0,
        totalAlertas: alertasRes.data?.length || 0,
        alertasCriticas: alertasRes.data?.filter(a => a.tipo === 'critica').length || 0,
        promedioGeneral: promedioGeneral || 0
      }
    }
  })

  // Alertas por tipo
  const { data: alertasPorTipo } = useQuery({
    queryKey: ['alertas-por-tipo'],
    queryFn: async () => {
      const { data } = await supabase
        .from('alertas')
        .select('tipo')
        .in('estado', ['activa', 'en_atencion'])

      const counts = { critica: 0, moderada: 0, preventiva: 0 }
      data?.forEach(a => {
        counts[a.tipo as keyof typeof counts]++
      })

      return [
        { name: 'Críticas', value: counts.critica, color: '#ef4444' },
        { name: 'Moderadas', value: counts.moderada, color: '#f59e0b' },
        { name: 'Preventivas', value: counts.preventiva, color: '#3b82f6' }
      ]
    }
  })

  // Rendimiento por grado
  const { data: rendimientoPorGrado } = useQuery({
    queryKey: ['rendimiento-por-grado'],
    queryFn: async () => {
      const { data } = await supabase
        .from('vista_estudiantes_resumen')
        .select('grado, promedio_general')

      const porGrado: Record<number, number[]> = {}
      data?.forEach(e => {
        if (!porGrado[e.grado]) porGrado[e.grado] = []
        porGrado[e.grado].push(e.promedio_general)
      })

      return Object.entries(porGrado).map(([grado, promedios]) => ({
        grado: `${grado}° Grado`,
        promedio: promedios.reduce((a, b) => a + b, 0) / promedios.length
      }))
    }
  })

  if (loadingStats) {
    return <LoadingSpinner fullScreen message="Cargando dashboard..." />
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Bienvenido, {perfil?.nombres}</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Estudiantes</p>
              <p className="text-3xl font-bold text-gray-900">{stats?.totalEstudiantes}</p>
            </div>
            <div className="p-3 bg-blue-50 rounded-lg">
              <Users className="w-8 h-8 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Alertas Activas</p>
              <p className="text-3xl font-bold text-orange-600">{stats?.totalAlertas}</p>
            </div>
            <div className="p-3 bg-orange-50 rounded-lg">
              <AlertTriangle className="w-8 h-8 text-orange-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Alertas Críticas</p>
              <p className="text-3xl font-bold text-red-600">{stats?.alertasCriticas}</p>
            </div>
            <div className="p-3 bg-red-50 rounded-lg">
              <XCircle className="w-8 h-8 text-red-600" />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Promedio General</p>
              <p className="text-3xl font-bold text-green-600">
                {stats?.promedioGeneral.toFixed(2)}
              </p>
            </div>
            <div className="p-3 bg-green-50 rounded-lg">
              <TrendingUp className="w-8 h-8 text-green-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Rendimiento por Grado */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Rendimiento por Grado</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={rendimientoPorGrado}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="grado" />
              <YAxis domain={[0, 20]} />
              <Tooltip />
              <Bar dataKey="promedio" fill="#0ea5e9" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Distribución de Alertas */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Distribución de Alertas</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={alertasPorTipo}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={(entry) => `${entry.name}: ${entry.value}`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {alertasPorTipo?.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Alertas Recientes */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Alertas Recientes</h3>
        <AlertasRecientes />
      </div>
    </div>
  )
}

function AlertasRecientes() {
  const { data: alertas, isLoading } = useQuery({
    queryKey: ['alertas-recientes'],
    queryFn: async () => {
      const { data } = await supabase
        .from('vista_alertas_activas')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(5)

      return data
    }
  })

  if (isLoading) return <LoadingSpinner />

  if (!alertas || alertas.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <CheckCircle className="w-12 h-12 mx-auto mb-2 text-green-500" />
        <p>No hay alertas activas</p>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {alertas.map((alerta) => (
        <div
          key={alerta.id}
          className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
        >
          <div className="flex items-center gap-4">
            <span className={`badge badge-${alerta.tipo === 'critica' ? 'critical' : alerta.tipo === 'moderada' ? 'moderate' : 'preventive'}`}>
              {alerta.tipo}
            </span>
            <div>
              <p className="font-medium">{alerta.estudiante_nombre}</p>
              <p className="text-sm text-gray-600">{alerta.grado}° {alerta.seccion} - {alerta.motivo}</p>
            </div>
          </div>
          <button className="btn-primary text-sm">Ver detalles</button>
        </div>
      ))}
    </div>
  )
}
