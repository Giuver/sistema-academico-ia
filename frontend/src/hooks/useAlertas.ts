import { useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { supabase } from '@/services/supabase'

const STUDENT_CHUNK_SIZE = 50

function chunkArray<T>(items: T[], size: number): T[][] {
  const chunks: T[][] = []
  for (let index = 0; index < items.length; index += size) {
    chunks.push(items.slice(index, index + size))
  }
  return chunks
}

async function fetchResumenPorEstudiantes(
  studentIds: string[]
): Promise<Array<{ id: string; promedio_general: number | null; total_inasistencias: number }>> {
  const chunks = chunkArray(studentIds, STUDENT_CHUNK_SIZE)
  const rows = await Promise.all(
    chunks.map(async (ids) => {
      const { data, error } = await supabase
        .from('vista_estudiantes_resumen')
        .select('id, promedio_general, total_inasistencias')
        .in('id', ids)

      if (error) throw error
      return data || []
    })
  )

  return rows.flat() as Array<{ id: string; promedio_general: number | null; total_inasistencias: number }>
}

export function useAlertas() {
  // Query para obtener alertas
  const { data: alertas, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['alertas'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('alertas')
        .select(`
          id,
          estudiante_id,
          tipo,
          nivel_riesgo,
          categoria,
          motivo,
          prioridad,
          estado,
          created_at,
          fecha_atencion,
          estudiantes!inner(id, codigo, nombres, apellidos, grado, seccion),
          docente:perfiles!alertas_docente_asignado_fkey(id, nombres, apellidos)
        `)
        .order('prioridad', { ascending: false })
        .order('created_at', { ascending: false })

      if (error) throw error

      const alertasBase = data || []
      if (alertasBase.length === 0) {
        const { data: alertasVista, error: errorVista } = await supabase
          .from('vista_alertas_activas')
          .select('*')
          .order('prioridad', { ascending: false })
          .order('created_at', { ascending: false })

        if (errorVista) throw errorVista
        return (alertasVista || []).map((alerta: any) => ({
          ...alerta,
          motivo_actualizado: alerta.motivo,
        }))
      }

      const studentIds = Array.from(new Set(alertasBase.map((alerta: any) => alerta.estudiante_id)))

      if (studentIds.length === 0) {
        return []
      }

      const resumen = await fetchResumenPorEstudiantes(studentIds)
      const resumenMap = new Map(
        resumen.map((item) => [item.id, item])
      )

      return alertasBase.map((alerta: any) => {
        const infoEstudiante = Array.isArray(alerta.estudiantes)
          ? alerta.estudiantes[0]
          : alerta.estudiantes
        const infoDocente = Array.isArray(alerta.docente)
          ? alerta.docente[0]
          : alerta.docente
        const resumenEstudiante = resumenMap.get(alerta.estudiante_id)
        const promedioActual = resumenEstudiante?.promedio_general ?? null
        const inasistenciasActuales = resumenEstudiante?.total_inasistencias ?? 0

        return {
          ...alerta,
          estudiante_codigo: infoEstudiante?.codigo,
          estudiante_nombre: `${infoEstudiante?.nombres || ''} ${infoEstudiante?.apellidos || ''}`.trim(),
          grado: infoEstudiante?.grado,
          seccion: infoEstudiante?.seccion,
          docente_asignado_nombre: infoDocente
            ? `${infoDocente.nombres || ''} ${infoDocente.apellidos || ''}`.trim()
            : null,
          promedio_actual: promedioActual,
          inasistencias_actuales: inasistenciasActuales,
          motivo_actualizado:
            promedioActual !== null
              ? `Riesgo actual: promedio ${promedioActual.toFixed(2)} e inasistencias ${inasistenciasActuales}`
              : `Riesgo actual: sin notas registradas e inasistencias ${inasistenciasActuales}`,
        }
      })
    },
  })

  // Suscripción en tiempo real
  useEffect(() => {
    const channel = supabase
      .channel('alertas-changes')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'alertas',
        },
        (payload) => {
          console.log('Cambio en alertas:', payload)
          refetch() // Refrescar datos cuando hay cambios
        }
      )
      .subscribe()

    return () => {
      supabase.removeChannel(channel)
    }
  }, [refetch])

  return {
    alertas: alertas || [],
    isLoading,
    isError,
    error,
    refetch,
  }
}

export function useAlertasPorEstudiante(estudianteId: string) {
  return useQuery({
    queryKey: ['alertas', estudianteId],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('alertas')
        .select('*')
        .eq('estudiante_id', estudianteId)
        .order('created_at', { ascending: false })

      if (error) throw error
      return data
    },
    enabled: !!estudianteId,
  })
}
