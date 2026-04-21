import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { supabase } from '@/services/supabase'
import { mlApiService } from '@/services/mlApi'
import { ArrowLeft, AlertTriangle, TrendingUp, Calendar } from 'lucide-react'
import LoadingSpinner from '@/components/common/LoadingSpinner'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { formatDate, getNivelRiesgoColor } from '@/utils/helpers'
import { useState } from 'react'

export default function EstudianteDetailPage() {
  const { id } = useParams()
  const [loadingPrediccion, setLoadingPrediccion] = useState(false)
  const [prediccion, setPrediccion] = useState<any>(null)

  const { data: estudiante, isLoading } = useQuery({
    queryKey: ['estudiante', id],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('estudiantes')
        .select('*')
        .eq('id', id)
        .single()

      if (error) throw error
      return data
    },
    enabled: !!id
  })

  const { data: notas } = useQuery({
    queryKey: ['notas', id],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('notas')
        .select('*, curso:cursos(nombre), periodo:periodos(nombre)')
        .eq('estudiante_id', id)
        .order('created_at', { ascending: true })

      if (error) throw error
      return data
    },
    enabled: !!id
  })

  const { data: alertas } = useQuery({
    queryKey: ['alertas-estudiante', id],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('alertas')
        .select('*')
        .eq('estudiante_id', id)
        .order('created_at', { ascending: false })

      if (error) throw error
      return data
    },
    enabled: !!id
  })

  const handlePredecir = async () => {
    if (!id) return
    
    setLoadingPrediccion(true)
    try {
      const result = await mlApiService.predecir({
        estudiante_id: id,
        tipo_prediccion: 'desaprobacion'
      })
      setPrediccion(result)
    } catch (error) {
      console.error('Error en predicción:', error)
    } finally {
      setLoadingPrediccion(false)
    }
  }

  if (isLoading) {
    return <LoadingSpinner fullScreen message="Cargando información del estudiante..." />
  }

  if (!estudiante) {
    return <div>Estudiante no encontrado</div>
  }

  // Preparar datos para gráfico de evolución
  const datosGrafico = notas?.reduce((acc: any[], nota) => {
    const periodo = nota.periodo?.nombre || 'Sin periodo'
    const existing = acc.find(d => d.periodo === periodo)
    if (existing) {
      existing.notas.push(nota.nota)
    } else {
      acc.push({ periodo, notas: [nota.nota] })
    }
    return acc
  }, []).map(d => ({
    periodo: d.periodo,
    promedio: d.notas.reduce((a: number, b: number) => a + b, 0) / d.notas.length
  }))

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link to="/estudiantes" className="p-2 hover:bg-gray-100 rounded-lg">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {estudiante.nombres} {estudiante.apellidos}
          </h1>
          <p className="text-gray-600">Código: {estudiante.codigo} • {estudiante.grado}° {estudiante.seccion}</p>
        </div>
      </div>

      {/* Información básica y predicción */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card">
          <h3 className="font-semibold mb-4">Información Personal</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">DNI:</span>
              <span className="font-medium">{estudiante.dni || 'No registrado'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Género:</span>
              <span className="font-medium">{estudiante.genero === 'M' ? 'Masculino' : 'Femenino'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Fecha Nac.:</span>
              <span className="font-medium">{estudiante.fecha_nacimiento ? formatDate(estudiante.fecha_nacimiento) : 'No registrado'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Teléfono:</span>
              <span className="font-medium">{estudiante.telefono_contacto || 'No registrado'}</span>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 className="font-semibold mb-4">Apoderado</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Nombre:</span>
              <span className="font-medium">{estudiante.nombre_apoderado || 'No registrado'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Teléfono:</span>
              <span className="font-medium">{estudiante.telefono_apoderado || 'No registrado'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Email:</span>
              <span className="font-medium text-xs">{estudiante.email_contacto || 'No registrado'}</span>
            </div>
          </div>
        </div>

        <div className="card bg-gradient-to-br from-primary-50 to-primary-100">
          <h3 className="font-semibold mb-4">Predicción de Riesgo</h3>
          {prediccion ? (
            <div className="space-y-3">
              <div className={`p-3 rounded-lg ${getNivelRiesgoColor(prediccion.nivel_riesgo)}`}>
                <p className="text-sm font-medium">Nivel de Riesgo</p>
                <p className="text-2xl font-bold capitalize">{prediccion.nivel_riesgo}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Probabilidad de desaprobación</p>
                <p className="text-xl font-bold">{(prediccion.probabilidad * 100).toFixed(1)}%</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Confianza del modelo</p>
                <p className="text-xl font-bold">{(prediccion.confianza * 100).toFixed(1)}%</p>
              </div>
            </div>
          ) : (
            <button
              onClick={handlePredecir}
              disabled={loadingPrediccion}
              className="w-full btn-primary"
            >
              {loadingPrediccion ? <LoadingSpinner size="sm" /> : 'Generar Predicción'}
            </button>
          )}
        </div>
      </div>

      {/* Gráfico de evolución */}
      <div className="card">
        <h3 className="font-semibold mb-4">Evolución del Rendimiento</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={datosGrafico}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="periodo" />
            <YAxis domain={[0, 20]} />
            <Tooltip />
            <Line type="monotone" dataKey="promedio" stroke="#0ea5e9" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Alertas */}
      <div className="card">
        <h3 className="font-semibold mb-4 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5" />
          Alertas ({alertas?.length || 0})
        </h3>
        {alertas && alertas.length > 0 ? (
          <div className="space-y-2">
            {alertas.map(alerta => (
              <div key={alerta.id} className="p-4 border border-gray-200 rounded-lg">
                <div className="flex justify-between items-start">
                  <div>
                    <span className={`badge badge-${alerta.tipo === 'critica' ? 'critical' : alerta.tipo === 'moderada' ? 'moderate' : 'preventive'}`}>
                      {alerta.tipo}
                    </span>
                    <p className="mt-2 font-medium">{alerta.motivo}</p>
                    <p className="text-sm text-gray-600 mt-1">Estado: {alerta.estado}</p>
                  </div>
                  <span className="text-xs text-gray-500">{formatDate(alerta.created_at)}</span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-600 text-center py-4">No hay alertas registradas</p>
        )}
      </div>
    </div>
  )
}
