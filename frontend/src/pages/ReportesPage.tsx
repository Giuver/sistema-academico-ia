import { useState } from 'react'
import { FileText, Download, TrendingUp, Users, AlertTriangle, CheckSquare } from 'lucide-react'
import { mlApiService } from '@/services/mlApi'
import LoadingSpinner from '@/components/common/LoadingSpinner'

export default function ReportesPage() {
  const [generando, setGenerando] = useState(false)
  const [reporteGenerado, setReporteGenerado] = useState<any>(null)

  const tiposReporte = [
    {
      id: 'estudiantes-riesgo',
      nombre: 'Estudiantes en Riesgo',
      descripcion: 'Lista completa de estudiantes con alertas activas y niveles de riesgo',
      icon: AlertTriangle,
      color: 'from-red-500 to-red-600'
    },
    {
      id: 'analisis-periodo',
      nombre: 'Análisis de Periodo',
      descripcion: 'Comparación de rendimiento entre periodos académicos',
      icon: TrendingUp,
      color: 'from-blue-500 to-blue-600'
    },
    {
      id: 'efectividad-intervenciones',
      nombre: 'Efectividad de Intervenciones',
      descripcion: 'Evaluación de estrategias pedagógicas implementadas',
      icon: CheckSquare,
      color: 'from-green-500 to-green-600'
    },
    {
      id: 'resumen-institucional',
      nombre: 'Resumen Institucional',
      descripcion: 'Reporte ejecutivo para dirección y UGEL',
      icon: FileText,
      color: 'from-purple-500 to-purple-600'
    }
  ]

  const handleGenerarReporte = async (tipo: string) => {
    setGenerando(true)
    setReporteGenerado(null)

    try {
      const params = {
        formato: 'pdf',
        incluir_recomendaciones: true
      }

      const resultado = await mlApiService.generarReporte(tipo, params)
      setReporteGenerado(resultado)
    } catch (error) {
      console.error('Error generando reporte:', error)
      alert('Error al generar el reporte')
    } finally {
      setGenerando(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <FileText className="w-7 h-7" />
          Generación de Reportes
        </h1>
        <p className="text-gray-600">Descarga reportes automáticos en PDF o Excel</p>
      </div>

      {/* Grid de tipos de reporte */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {tiposReporte.map(reporte => {
          const Icon = reporte.icon
          return (
            <div key={reporte.id} className="card hover:shadow-lg transition-shadow">
              <div className={`w-full h-2 rounded-t-lg bg-gradient-to-r ${reporte.color} -mt-6 mb-4`} />
              
              <div className="flex items-start gap-4">
                <div className={`p-3 rounded-lg bg-gradient-to-br ${reporte.color}`}>
                  <Icon className="w-8 h-8 text-white" />
                </div>
                
                <div className="flex-1">
                  <h3 className="font-semibold text-lg text-gray-900 mb-1">
                    {reporte.nombre}
                  </h3>
                  <p className="text-sm text-gray-600 mb-4">
                    {reporte.descripcion}
                  </p>
                  
                  <button
                    onClick={() => handleGenerarReporte(reporte.id)}
                    disabled={generando}
                    className="btn-primary flex items-center gap-2"
                  >
                    {generando ? (
                      <>
                        <LoadingSpinner size="sm" />
                        <span>Generando...</span>
                      </>
                    ) : (
                      <>
                        <Download className="w-4 h-4" />
                        <span>Generar Reporte</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Resultado del reporte */}
      {reporteGenerado && (
        <div className="card bg-green-50 border-green-200">
          <div className="flex items-start gap-4">
            <CheckSquare className="w-6 h-6 text-green-600 flex-shrink-0 mt-1" />
            <div className="flex-1">
              <h3 className="font-semibold text-green-900 mb-2">
                ¡Reporte generado exitosamente!
              </h3>
              <p className="text-sm text-green-800 mb-3">
                Archivo: {reporteGenerado.nombre_archivo}
              </p>
              {reporteGenerado.url_descarga && (
                <a
                  href={reporteGenerado.url_descarga}
                  download
                  className="btn-primary bg-green-600 hover:bg-green-700 inline-flex items-center gap-2"
                >
                  <Download className="w-4 h-4" />
                  Descargar Reporte
                </a>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Información adicional */}
      <div className="card bg-blue-50 border-blue-200">
        <h3 className="font-semibold text-blue-900 mb-2">Información sobre Reportes</h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Los reportes se generan en formato PDF o Excel según el tipo</li>
          <li>• La generación puede tardar de 10-30 segundos dependiendo de la cantidad de datos</li>
          <li>• Los reportes incluyen gráficos estadísticos y recomendaciones</li>
          <li>• Puedes programar reportes automáticos semanales o mensuales</li>
        </ul>
      </div>
    </div>
  )
}
