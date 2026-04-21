// Edge Function para generar alertas automáticamente
// Se ejecuta cuando se insertan nuevas notas

import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
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

    // Obtener datos del estudiante
    const { data: estudiante } = await supabaseClient
      .from('estudiantes')
      .select('*')
      .eq('id', estudiante_id)
      .single()

    if (!estudiante) {
      throw new Error('Estudiante no encontrado')
    }

    // Obtener notas del periodo actual
    const { data: notas } = await supabaseClient
      .from('notas')
      .select('nota')
      .eq('estudiante_id', estudiante_id)
      .eq('periodo_id', periodo_id)

    // Calcular promedio
    const promedio = notas && notas.length > 0
      ? notas.reduce((sum, n) => sum + n.nota, 0) / notas.length
      : 0

    // Obtener asistencia
    const { data: asistencias, count: totalDias } = await supabaseClient
      .from('asistencia')
      .select('estado', { count: 'exact' })
      .eq('estudiante_id', estudiante_id)

    const ausencias = asistencias?.filter(a => a.estado === 'ausente').length || 0
    const tasaAsistencia = totalDias ? ((totalDias - ausencias) / totalDias) * 100 : 100

    // Determinar si necesita alerta
    let necesitaAlerta = false
    let tipo: 'critica' | 'moderada' | 'preventiva' = 'preventiva'
    let motivo = ''
    let categoria: 'rendimiento' | 'asistencia' | 'multiple' = 'rendimiento'
    let nivelRiesgo = 0

    if (promedio < 11) {
      necesitaAlerta = true
      tipo = 'critica'
      motivo = `Promedio crítico: ${promedio.toFixed(2)}. Riesgo alto de desaprobación.`
      nivelRiesgo = 0.8
      categoria = 'rendimiento'
    } else if (promedio < 13) {
      necesitaAlerta = true
      tipo = 'moderada'
      motivo = `Promedio bajo: ${promedio.toFixed(2)}. Requiere reforzamiento.`
      nivelRiesgo = 0.5
      categoria = 'rendimiento'
    }

    if (tasaAsistencia < 70) {
      necesitaAlerta = true
      tipo = tipo === 'critica' ? 'critica' : 'moderada'
      motivo = tipo === 'critica' 
        ? `${motivo} Además, asistencia muy baja: ${tasaAsistencia.toFixed(1)}%.`
        : `Asistencia muy baja: ${tasaAsistencia.toFixed(1)}%.`
      nivelRiesgo = Math.max(nivelRiesgo, 0.7)
      categoria = 'multiple'
    } else if (tasaAsistencia < 85) {
      if (necesitaAlerta) {
        categoria = 'multiple'
        motivo = `${motivo} Asistencia irregular: ${tasaAsistencia.toFixed(1)}%.`
      } else {
        necesitaAlerta = true
        tipo = 'preventiva'
        motivo = `Asistencia irregular: ${tasaAsistencia.toFixed(1)}%.`
        nivelRiesgo = 0.3
        categoria = 'asistencia'
      }
    }

    // Verificar si ya existe una alerta activa
    const { data: alertaExistente } = await supabaseClient
      .from('alertas')
      .select('id')
      .eq('estudiante_id', estudiante_id)
      .in('estado', ['activa', 'en_atencion'])
      .single()

    if (necesitaAlerta) {
      if (alertaExistente) {
        // Actualizar alerta existente
        await supabaseClient
          .from('alertas')
          .update({
            tipo,
            motivo,
            categoria,
            nivel_riesgo: nivelRiesgo,
            prioridad: tipo === 'critica' ? 5 : tipo === 'moderada' ? 3 : 1,
            updated_at: new Date().toISOString()
          })
          .eq('id', alertaExistente.id)
      } else {
        // Crear nueva alerta
        await supabaseClient
          .from('alertas')
          .insert({
            estudiante_id,
            tipo,
            motivo,
            categoria,
            nivel_riesgo: nivelRiesgo,
            estado: 'activa',
            prioridad: tipo === 'critica' ? 5 : tipo === 'moderada' ? 3 : 1,
            detalles: {
              promedio,
              tasa_asistencia: tasaAsistencia,
              total_ausencias: ausencias
            }
          })

        // Llamar a API de ML para predicción (opcional)
        try {
          const mlApiUrl = Deno.env.get('ML_API_URL') || 'http://localhost:8000'
          const response = await fetch(`${mlApiUrl}/api/prediccion/individual`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              estudiante_id,
              periodo_id,
              tipo_prediccion: 'desaprobacion'
            })
          })

          const prediccion = await response.json()
          console.log('Predicción ML:', prediccion)
        } catch (error) {
          console.error('Error llamando a ML API:', error)
        }
      }

      return new Response(
        JSON.stringify({
          success: true,
          alerta_creada: !alertaExistente,
          tipo,
          motivo
        }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    return new Response(
      JSON.stringify({ success: true, alerta_creada: false, message: 'No se requiere alerta' }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )

  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }
})
