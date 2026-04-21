import { useState } from 'react'
import { useAlertas } from '@/hooks/useAlertas'
import { AlertTriangle, Filter, CheckCircle, Clock, XCircle } from 'lucide-react'
import LoadingSpinner from '@/components/common/LoadingSpinner'
import { formatDateTime, getNivelRiesgoColor, cn } from '@/utils/helpers'
import { supabase } from '@/services/supabase'
import { useMutation, useQueryClient } from '@tanstack/react-query'

export default function AlertasPage() {
  const { alertas, isLoading } = useAlertas()
  const [tipoFilter, setTipoFilter] = useState<string>('')
  const [estadoFilter, setEstadoFilter] = useState<string>('')
  const queryClient = useQueryClient()

  const alertasFiltradas = alertas?.filter(alerta => {
    if (tipoFilter && alerta.tipo !== tipoFilter) return false
    if (estadoFilter && alerta.estado !== estadoFilter) return false
    return true
  })

  const cambiarEstadoMutation = useMutation({
    mutationFn: async ({ alertaId, nuevoEstado }: { alertaId: string, nuevoEstado: string }) => {
      const { error } = await supabase
        .from('alertas')
        .update({ 
          estado: nuevoEstado,
          fecha_atencion: nuevoEstado === 'en_atencion' ? new Date().toISOString() : undefined,
          fecha_resolucion: nuevoEstado === 'resuelta' ? new Date().toISOString() : undefined
        })
        .eq('id', alertaId)

      if (error) throw error
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alertas'] })
    }
  })

  const handleCambiarEstado = async (alertaId: string, nuevoEstado: string) => {
    if (window.confirm(`¿Cambiar estado de la alerta a "${nuevoEstado}"?`)) {
      cambiarEstadoMutation.mutate({ alertaId, nuevoEstado })
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <AlertTriangle className="w-7 h-7" />
          Sistema de Alertas Tempranas
        </h1>
        <p className="text-gray-600">Monitoreo en tiempo real de estudiantes en riesgo</p>
      </div>

      {/* Estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card bg-gradient-to-br from-red-50 to-red-100">
          <p className="text-sm text-red-700 font-medium">Alertas Críticas</p>
          <p className="text-3xl font-bold text-red-800">
            {alertas?.filter(a => a.tipo === 'critica').length || 0}
          </p>
        </div>
        <div className="card bg-gradient-to-br from-yellow-50 to-yellow-100">
          <p className="text-sm text-yellow-700 font-medium">Alertas Moderadas</p>
          <p className="text-3xl font-bold text-yellow-800">
            {alertas?.filter(a => a.tipo === 'moderada').length || 0}
          </p>
        </div>
        <div className="card bg-gradient-to-br from-blue-50 to-blue-100">
          <p className="text-sm text-blue-700 font-medium">Alertas Preventivas</p>
          <p className="text-3xl font-bold text-blue-800">
            {alertas?.filter(a => a.tipo === 'preventiva').length || 0}
          </p>
        </div>
        <div className="card bg-gradient-to-br from-green-50 to-green-100">
          <p className="text-sm text-green-700 font-medium">Resueltas (Hoy)</p>
          <p className="text-3xl font-bold text-green-800">
            {alertas?.filter(a => a.estado === 'resuelta').length || 0}
          </p>
        </div>
      </div>

      {/* Filtros */}
      <div className="card">
        <div className="flex items-center gap-4">
          <Filter className="w-5 h-5 text-gray-400" />
          <select
            value={tipoFilter}
            onChange={(e) => setTipoFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
          >
            <option value="">Todos los tipos</option>
            <option value="critica">Críticas</option>
            <option value="moderada">Moderadas</option>
            <option value="preventiva">Preventivas</option>
          </select>
          <select
            value={estadoFilter}
            onChange={(e) => setEstadoFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
          >
            <option value="">Todos los estados</option>
            <option value="activa">Activas</option>
            <option value="en_atencion">En Atención</option>
            <option value="resuelta">Resueltas</option>
            <option value="descartada">Descartadas</option>
          </select>
          <span className="text-sm text-gray-600 ml-auto">
            {alertasFiltradas?.length || 0} alertas
          </span>
        </div>
      </div>

      {/* Lista de alertas */}
      <div className="space-y-4">
        {isLoading ? (
          <div className="card">
            <LoadingSpinner />
          </div>
        ) : alertasFiltradas && alertasFiltradas.length > 0 ? (
          alertasFiltradas.map(alerta => (
            <div key={alerta.id} className="card hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className={cn(
                      'badge',
                      alerta.tipo === 'critica' ? 'badge-critical' : 
                      alerta.tipo === 'moderada' ? 'badge-moderate' : 
                      'badge-preventive'
                    )}>
                      {alerta.tipo.toUpperCase()}
                    </span>
                    <span className="text-sm text-gray-500">
                      Prioridad {alerta.prioridad}
                    </span>
                  </div>

                  <h3 className="font-semibold text-lg text-gray-900 mb-1">
                    {alerta.estudiante_nombre}
                  </h3>
                  <p className="text-sm text-gray-600 mb-2">
                    {alerta.grado}° {alerta.seccion} • {alerta.categoria}
                  </p>
                  <p className="text-gray-700">{alerta.motivo}</p>

                  <div className="mt-3 flex items-center gap-4 text-sm text-gray-500">
                    <span className="flex items-center gap-1">
                      <Clock className="w-4 h-4" />
                      {formatDateTime(alerta.created_at)}
                    </span>
                    {alerta.docente_asignado_nombre && (
                      <span>Asignado a: {alerta.docente_asignado_nombre}</span>
                    )}
                  </div>
                </div>

                <div className="flex flex-col gap-2">
                  <div className="flex items-center gap-2">
                    {alerta.estado === 'activa' && (
                      <button
                        onClick={() => handleCambiarEstado(alerta.id, 'en_atencion')}
                        className="btn-primary text-sm flex items-center gap-1"
                      >
                        <Clock className="w-4 h-4" />
                        Atender
                      </button>
                    )}
                    {alerta.estado === 'en_atencion' && (
                      <button
                        onClick={() => handleCambiarEstado(alerta.id, 'resuelta')}
                        className="btn-primary text-sm flex items-center gap-1 bg-green-600 hover:bg-green-700"
                      >
                        <CheckCircle className="w-4 h-4" />
                        Resolver
                      </button>
                    )}
                    {(alerta.estado === 'activa' || alerta.estado === 'en_atencion') && (
                      <button
                        onClick={() => handleCambiarEstado(alerta.id, 'descartada')}
                        className="btn-secondary text-sm flex items-center gap-1"
                      >
                        <XCircle className="w-4 h-4" />
                        Descartar
                      </button>
                    )}
                  </div>
                  <span className={cn(
                    'text-xs px-2 py-1 rounded text-center font-medium',
                    alerta.estado === 'activa' ? 'bg-orange-100 text-orange-800' :
                    alerta.estado === 'en_atencion' ? 'bg-blue-100 text-blue-800' :
                    alerta.estado === 'resuelta' ? 'bg-green-100 text-green-800' :
                    'bg-gray-100 text-gray-800'
                  )}>
                    {alerta.estado.replace('_', ' ').toUpperCase()}
                  </span>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="card text-center py-12">
            <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              ¡No hay alertas con los filtros seleccionados!
            </h3>
            <p className="text-gray-600">
              Todos los estudiantes están en buen estado académico.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
