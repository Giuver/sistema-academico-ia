import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { supabase } from '@/services/supabase'
import { Search, Filter, Download, Eye, Plus } from 'lucide-react'
import LoadingSpinner from '@/components/common/LoadingSpinner'
import { EstudianteForm } from '@/components/forms/EstudianteForm'
import { getNotaColor, cn } from '@/utils/helpers'

export default function EstudiantesPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [gradoFilter, setGradoFilter] = useState<number | ''>('')
  const [showForm, setShowForm] = useState(false)

  const { data: estudiantes, isLoading, refetch } = useQuery({
    queryKey: ['estudiantes', gradoFilter],
    queryFn: async () => {
      let query = supabase
        .from('vista_estudiantes_resumen')
        .select('*')
        .order('apellidos', { ascending: true })

      if (gradoFilter) {
        query = query.eq('grado', gradoFilter)
      }

      const { data, error } = await query

      if (error) throw error
      return data
    }
  })

  const filteredEstudiantes = estudiantes?.filter(e =>
    `${e.nombres} ${e.apellidos} ${e.codigo}`.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const handleFormSuccess = () => {
    setShowForm(false)
    refetch()
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Estudiantes</h1>
          <p className="text-gray-600">Gestión de estudiantes y rendimiento académico</p>
        </div>
        <div className="flex gap-2">
          <button 
            onClick={() => setShowForm(true)}
            className="btn-primary flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Agregar Estudiante
          </button>
          <button className="btn-secondary flex items-center gap-2">
            <Download className="w-4 h-4" />
            Exportar
          </button>
        </div>
      </div>

      {/* Filtros y búsqueda */}
      <div className="card">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar por nombre o código..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
          <select
            value={gradoFilter}
            onChange={(e) => setGradoFilter(e.target.value ? Number(e.target.value) : '')}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="">Todos los grados</option>
            <option value="1">1° Grado</option>
            <option value="2">2° Grado</option>
            <option value="3">3° Grado</option>
            <option value="4">4° Grado</option>
            <option value="5">5° Grado</option>
          </select>
        </div>

        <div className="mt-4 flex items-center gap-4 text-sm text-gray-600">
          <span>Total: {filteredEstudiantes?.length || 0} estudiantes</span>
          {gradoFilter && <span>•</span>}
          {gradoFilter && <span>Grado {gradoFilter}</span>}
        </div>
      </div>

      {/* Tabla de estudiantes */}
      <div className="card overflow-hidden p-0">
        {isLoading ? (
          <div className="p-8">
            <LoadingSpinner />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Código
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Estudiante
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Grado
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Promedio
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Inasistencias
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Alertas
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredEstudiantes?.map((estudiante) => (
                  <tr key={estudiante.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-mono">
                      {estudiante.codigo}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {estudiante.nombres} {estudiante.apellidos}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {estudiante.grado}° {estudiante.seccion}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {estudiante.promedio_general !== null ? (
                        <span className={cn('text-sm font-semibold', getNotaColor(estudiante.promedio_general))}>
                          {estudiante.promedio_general.toFixed(2)}
                        </span>
                      ) : (
                        <span className="text-sm text-gray-400 italic">Sin notas</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {estudiante.total_inasistencias || 0}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {(estudiante.alertas_activas || 0) > 0 ? (
                        <span className="badge badge-critical">
                          {estudiante.alertas_activas} activa(s)
                        </span>
                      ) : (
                        <span className="badge badge-success">Sin alertas</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <Link
                        to={`/estudiantes/${estudiante.id}`}
                        className="text-primary-600 hover:text-primary-800 flex items-center gap-1"
                      >
                        <Eye className="w-4 h-4" />
                        Ver detalle
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal de formulario */}
      {showForm && (
        <EstudianteForm
          onSuccess={handleFormSuccess}
          onCancel={() => setShowForm(false)}
        />
      )}
    </div>
  )
}
