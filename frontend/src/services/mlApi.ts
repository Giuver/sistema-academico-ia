import axios from 'axios'

const ML_API_URL = import.meta.env.VITE_ML_API_URL || 'http://localhost:8000'

const mlApi = axios.create({
  baseURL: ML_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Tipos para las APIs
export interface PrediccionRequest {
  estudiante_id: string
  periodo_id?: string
  tipo_prediccion: 'desaprobacion' | 'desercion' | 'nota_estimada'
}

export interface PrediccionResponse {
  estudiante_id: string
  periodo_id: string
  tipo_prediccion: string
  probabilidad?: number
  valor_estimado?: number
  confianza: number
  modelo_usado: string
  version_modelo: string
  nivel_riesgo: string
  recomendacion_alerta: boolean
  features_usadas: Record<string, any>
}

export interface RecomendacionRequest {
  estudiante_id: string
  alerta_id?: string
  categoria_deficiencia: string
  grado: number
}

export interface RecomendacionResponse {
  estudiante_id: string
  categoria_deficiencia: string
  recomendaciones: Array<{
    tipo: string
    descripcion: string
    estrategia: string
    recursos?: string
    prioridad: number
  }>
  total_recomendaciones: number
  prioridad_general: number
  observaciones?: string
}

// Funciones de API
export const mlApiService = {
  async predecir(data: PrediccionRequest): Promise<PrediccionResponse> {
    const response = await mlApi.post('/api/prediccion/individual', data)
    return response.data
  },

  async generarRecomendaciones(data: RecomendacionRequest): Promise<RecomendacionResponse> {
    const response = await mlApi.post('/api/recomendaciones/generar', data)
    return response.data
  },

  async generarReporte(tipo: string, params: any): Promise<any> {
    const response = await mlApi.post(`/api/reportes/${tipo}`, params)
    return response.data
  },

  async obtenerMetricasModelo(): Promise<any[]> {
    const response = await mlApi.get('/api/prediccion/metricas-modelo')
    return response.data
  },

  async obtenerHistorialPredicciones(estudianteId: string): Promise<any> {
    const response = await mlApi.get(`/api/prediccion/historial/${estudianteId}`)
    return response.data
  },
}

export default mlApi
