export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export interface Database {
  public: {
    Tables: {
      perfiles: {
        Row: {
          id: string
          rol: 'admin' | 'director' | 'docente' | 'consulta'
          nombres: string
          apellidos: string
          dni: string | null
          telefono: string | null
          email: string | null
          activo: boolean
          created_at: string
          updated_at: string
        }
        Insert: Omit<Database['public']['Tables']['perfiles']['Row'], 'id' | 'created_at' | 'updated_at'>
        Update: Partial<Database['public']['Tables']['perfiles']['Insert']>
      }
      estudiantes: {
        Row: {
          id: string
          codigo: string
          nombres: string
          apellidos: string
          dni: string | null
          fecha_nacimiento: string | null
          genero: 'M' | 'F' | null
          grado: number
          seccion: string
          direccion: string | null
          telefono_contacto: string | null
          email_contacto: string | null
          nombre_apoderado: string | null
          telefono_apoderado: string | null
          activo: boolean
          created_at: string
          updated_at: string
        }
        Insert: Omit<Database['public']['Tables']['estudiantes']['Row'], 'id' | 'created_at' | 'updated_at'>
        Update: Partial<Database['public']['Tables']['estudiantes']['Insert']>
      }
      alertas: {
        Row: {
          id: string
          estudiante_id: string
          tipo: 'critica' | 'moderada' | 'preventiva'
          nivel_riesgo: number
          categoria: 'rendimiento' | 'asistencia' | 'conducta' | 'multiple'
          motivo: string
          detalles: Json | null
          estado: 'activa' | 'en_atencion' | 'resuelta' | 'descartada'
          prioridad: number
          docente_asignado: string | null
          fecha_atencion: string | null
          fecha_resolucion: string | null
          created_at: string
          updated_at: string
        }
        Insert: Omit<Database['public']['Tables']['alertas']['Row'], 'id' | 'created_at' | 'updated_at'>
        Update: Partial<Database['public']['Tables']['alertas']['Insert']>
      }
      notas: {
        Row: {
          id: string
          estudiante_id: string
          curso_id: string
          periodo_id: string
          nota: number
          tipo_evaluacion: 'continua' | 'parcial' | 'final' | null
          observaciones: string | null
          registrado_por: string | null
          created_at: string
          updated_at: string
        }
        Insert: Omit<Database['public']['Tables']['notas']['Row'], 'id' | 'created_at' | 'updated_at'>
        Update: Partial<Database['public']['Tables']['notas']['Insert']>
      }
    }
    Views: {
      vista_estudiantes_resumen: {
        Row: {
          id: string
          codigo: string
          nombres: string
          apellidos: string
          grado: number
          seccion: string
          total_notas: number
          promedio_general: number
          total_inasistencias: number
          alertas_activas: number
        }
      }
      vista_alertas_activas: {
        Row: {
          id: string
          tipo: string
          nivel_riesgo: number
          categoria: string
          motivo: string
          prioridad: number
          estado: string
          estudiante_codigo: string
          estudiante_nombre: string
          grado: number
          seccion: string
          docente_asignado_nombre: string | null
          created_at: string
          fecha_atencion: string | null
        }
      }
    }
    Functions: {}
    Enums: {}
  }
}
