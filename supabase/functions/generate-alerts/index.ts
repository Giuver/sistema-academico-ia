// Edge Function: Generar Alertas Automáticamente
// Se ejecuta cuando se insertan nuevas notas o asistencia

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    )

    const { estudiante_id, periodo_id } = await req.json()

    // 1. Obtener datos del estudiante
    const { data: estudiante } = await supabaseClient
      .from('estudiantes')
      .select('*')
      .eq('id', estudiante_id)
      .single()

    if (!estudiante) {
      throw new Error('Estudiante no encontrado')
    }

    // 2. Calcular métricas académicas
    const { data: notas } = await supabaseClient
      .from('notas')
      .select('nota')
      .eq('estudiante_id', estudiante_id)
      .eq('periodo_id', periodo_id)

    const promedio = notas && notas.length > 0 
      ? notas.reduce((sum, n) => sum + n.nota, 0) / notas.length 
      : 0

    const { data: asistencia } = await supabaseClient
      .from('asistencia')
      .select('estado')
      .eq('estudiante_id', estudiante_id)

    const totalDias = asistencia?.length || 0
    const ausencias = asistencia?.filter(a => a.estado === 'ausente').length || 0
    const tasaAsistencia = totalDias > 0 ? ((totalDias - ausencias) / totalDias) * 100 : 100

    // 3. Determinar nivel de riesgo
    let nivelRiesgo = 'bajo'
    let tipoAlerta = 'preventiva'
    let motivo = ''
    let categoria = 'multiple'

    if (promedio < 11 || tasaAsistencia < 70) {
      nivelRiesgo = 'alto'
      tipoAlerta = 'critica'
      
      if (promedio < 11 && tasaAsistencia < 70) {
        motivo = `Promedio bajo (${promedio.toFixed(2)}) y asistencia crítica (${tasaAsistencia.toFixed(1)}%)`
        categoria = 'multiple'
      } else if (promedio < 11) {
        motivo = `Promedio de ${promedio.toFixed(2)} indica riesgo de desaprobación`
        categoria = 'rendimiento'
      } else {
        motivo = `Tasa de asistencia de ${tasaAsistencia.toFixed(1)}% es crítica`
        categoria = 'asistencia'
      }
    } else if (promedio < 14 || tasaAsistencia < 85) {
      nivelRiesgo = 'medio'
      tipoAlerta = 'moderada'
      motivo = `Rendimiento en rango moderado (Promedio: ${promedio.toFixed(2)}, Asistencia: ${tasaAsistencia.toFixed(1)}%)`
      categoria = promedio < 14 ? 'rendimiento' : 'asistencia'
    }

    // 4. Verificar si ya existe alerta activa
    const { data: alertaExistente } = await supabaseClient
      .from('alertas')
      .select('id')
      .eq('estudiante_id', estudiante_id)
      .in('estado', ['activa', 'en_atencion'])
      .single()

    // 5. Crear o actualizar alerta
    if (nivelRiesgo !== 'bajo') {
      const alertaData = {
        estudiante_id,
        tipo: tipoAlerta,
        nivel_riesgo: nivelRiesgo === 'alto' ? 0.85 : 0.55,
        categoria,
        motivo,
        detalles: {
          promedio,
          tasa_asistencia: tasaAsistencia,
          total_notas: notas?.length || 0,
          ausencias
        },
        prioridad: nivelRiesgo === 'alto' ? 5 : 3
      }

      if (alertaExistente) {
        await supabaseClient
          .from('alertas')
          .update(alertaData)
          .eq('id', alertaExistente.id)
      } else {
        await supabaseClient
          .from('alertas')
          .insert(alertaData)
      }

      return new Response(
        JSON.stringify({ 
          success: true, 
          alerta_creada: true,
          tipo: tipoAlerta,
          nivel_riesgo: nivelRiesgo
        }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    return new Response(
      JSON.stringify({ 
        success: true, 
        alerta_creada: false,
        mensaje: 'Estudiante sin riesgo identificado'
      }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )

  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      { 
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      }
    )
  }
})
