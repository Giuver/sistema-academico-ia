import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { supabase } from '@/services/supabase'

export function useAlertas() {
  const [alertasEnTiempoReal, setAlertasEnTiempoReal] = useState<any[]>([])

  // Query para obtener alertas
  const { data: alertas, isLoading, refetch } = useQuery({
    queryKey: ['alertas'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('vista_alertas_activas')
        .select('*')
        .order('prioridad', { ascending: false })
        .order('created_at', { ascending: false })

      if (error) throw error
      return data
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
