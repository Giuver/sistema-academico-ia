import { useState } from 'react'
import { supabase } from '@/services/supabase'

interface EstudianteFormProps {
  onSuccess: () => void;
  onCancel: () => void;
  estudiante?: any;
}

export const EstudianteForm: React.FC<EstudianteFormProps> = ({ onSuccess, onCancel, estudiante }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    codigo: estudiante?.codigo || '',
    nombres: estudiante?.nombres || '',
    apellidos: estudiante?.apellidos || '',
    dni: estudiante?.dni || '',
    fecha_nacimiento: estudiante?.fecha_nacimiento || '',
    genero: estudiante?.genero || 'M',
    grado: estudiante?.grado || 1,
    seccion: estudiante?.seccion || 'A',
    direccion: estudiante?.direccion || '',
    telefono_contacto: estudiante?.telefono_contacto || '',
    email_contacto: estudiante?.email_contacto || '',
    nombre_apoderado: estudiante?.nombre_apoderado || '',
    telefono_apoderado: estudiante?.telefono_apoderado || '',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'grado' ? parseInt(value) : value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (estudiante) {
        // Actualizar estudiante existente
        const { error: updateError } = await supabase
          .from('estudiantes')
          .update(formData)
          .eq('id', estudiante.id);

        if (updateError) throw updateError;
      } else {
        // Crear nuevo estudiante
        const { error: insertError } = await supabase
          .from('estudiantes')
          .insert([formData]);

        if (insertError) throw insertError;
      }

      onSuccess();
    } catch (err: any) {
      console.error('Error al guardar estudiante:', err);
      setError(err.message || 'Error al guardar el estudiante');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <h2 className="text-2xl font-bold mb-6">
            {estudiante ? 'Editar Estudiante' : 'Agregar Nuevo Estudiante'}
          </h2>

          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Información Básica */}
            <div>
              <h3 className="text-lg font-semibold mb-3 text-gray-700">Información Básica</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Código *
                  </label>
                  <input
                    type="text"
                    name="codigo"
                    value={formData.codigo}
                    onChange={handleChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="EST001"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    DNI
                  </label>
                  <input
                    type="text"
                    name="dni"
                    value={formData.dni}
                    onChange={handleChange}
                    maxLength={8}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="12345678"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nombres *
                  </label>
                  <input
                    type="text"
                    name="nombres"
                    value={formData.nombres}
                    onChange={handleChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Apellidos *
                  </label>
                  <input
                    type="text"
                    name="apellidos"
                    value={formData.apellidos}
                    onChange={handleChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Fecha de Nacimiento *
                  </label>
                  <input
                    type="date"
                    name="fecha_nacimiento"
                    value={formData.fecha_nacimiento}
                    onChange={handleChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Género *
                  </label>
                  <select
                    name="genero"
                    value={formData.genero}
                    onChange={handleChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="M">Masculino</option>
                    <option value="F">Femenino</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Grado *
                  </label>
                  <select
                    name="grado"
                    value={formData.grado}
                    onChange={handleChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value={1}>1° Secundaria</option>
                    <option value={2}>2° Secundaria</option>
                    <option value={3}>3° Secundaria</option>
                    <option value={4}>4° Secundaria</option>
                    <option value={5}>5° Secundaria</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Sección *
                  </label>
                  <input
                    type="text"
                    name="seccion"
                    value={formData.seccion}
                    onChange={handleChange}
                    required
                    maxLength={2}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="A"
                  />
                </div>
              </div>
            </div>

            {/* Información de Contacto */}
            <div>
              <h3 className="text-lg font-semibold mb-3 text-gray-700">Información de Contacto</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Dirección
                  </label>
                  <textarea
                    name="direccion"
                    value={formData.direccion}
                    onChange={handleChange}
                    rows={2}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Teléfono de Contacto
                  </label>
                  <input
                    type="tel"
                    name="telefono_contacto"
                    value={formData.telefono_contacto}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="999888777"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email de Contacto
                  </label>
                  <input
                    type="email"
                    name="email_contacto"
                    value={formData.email_contacto}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="contacto@email.com"
                  />
                </div>
              </div>
            </div>

            {/* Información del Apoderado */}
            <div>
              <h3 className="text-lg font-semibold mb-3 text-gray-700">Información del Apoderado</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nombre del Apoderado *
                  </label>
                  <input
                    type="text"
                    name="nombre_apoderado"
                    value={formData.nombre_apoderado}
                    onChange={handleChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Teléfono del Apoderado
                  </label>
                  <input
                    type="tel"
                    name="telefono_apoderado"
                    value={formData.telefono_apoderado}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="999888777"
                  />
                </div>
              </div>
            </div>

            {/* Botones */}
            <div className="flex justify-end gap-3 pt-4 border-t">
              <button
                type="button"
                onClick={onCancel}
                disabled={loading}
                className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={loading}
                className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Guardando...' : (estudiante ? 'Actualizar' : 'Guardar')}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};
