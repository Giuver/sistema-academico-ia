"""
API de Recomendaciones Pedagógicas
Genera sugerencias de estrategias educativas basadas en datos
"""

from fastapi import APIRouter, HTTPException
import logging
from typing import List, Dict

from app.schemas.recomendacion import (
    RecomendacionRequest,
    RecomendacionResponse,
    RecomendacionItem
)

router = APIRouter()
logger = logging.getLogger(__name__)


# Base de conocimiento de estrategias pedagógicas
ESTRATEGIAS_PEDAGOGICAS = {
    "rendimiento": {
        "bajo": [
            {
                "tipo": "reforzamiento_academico",
                "descripcion": "Implementar sesiones de reforzamiento en áreas críticas",
                "estrategia": "Clases de refuerzo 2-3 veces por semana (1 hora cada sesión) enfocadas en matemática y comunicación",
                "recursos": "Material didáctico adicional, espacio para tutorías, docente de apoyo",
                "prioridad": 5,
                "tiempo_estimado": "2-3 meses"
            },
            {
                "tipo": "tutoria_personalizada",
                "descripcion": "Asignar tutor académico individual",
                "estrategia": "Sesiones de tutoría 1:1 semanales para identificar y trabajar dificultades específicas",
                "recursos": "Tutor capacitado, materiales personalizados",
                "prioridad": 5,
                "tiempo_estimado": "Todo el periodo académico"
            },
            {
                "tipo": "metodologia_adaptada",
                "descripcion": "Adaptar metodología de enseñanza al estilo de aprendizaje del estudiante",
                "estrategia": "Identificar estilo de aprendizaje (visual, auditivo, kinestésico) y adaptar explicaciones",
                "recursos": "Evaluación de estilos de aprendizaje, materiales diversos",
                "prioridad": 4,
                "tiempo_estimado": "1 mes para diagnóstico, aplicación continua"
            }
        ],
        "medio": [
            {
                "tipo": "grupos_estudio",
                "descripcion": "Integrar en grupos de estudio colaborativo",
                "estrategia": "Formar grupos pequeños (4-5 estudiantes) con compañeros de rendimiento similar o superior",
                "recursos": "Espacio para reuniones, materiales de estudio",
                "prioridad": 3,
                "tiempo_estimado": "Durante todo el periodo"
            },
            {
                "tipo": "seguimiento_docente",
                "descripcion": "Monitoreo cercano del avance académico",
                "estrategia": "Reuniones quincenales con tutor de aula para revisar progreso y ajustar estrategias",
                "recursos": "Tiempo del docente tutor",
                "prioridad": 3,
                "tiempo_estimado": "Continuo"
            }
        ]
    },
    "asistencia": {
        "bajo": [
            {
                "tipo": "intervencion_familiar",
                "descripcion": "Coordinación directa con padres/apoderados",
                "estrategia": "Reunión presencial con apoderados para identificar causas de inasistencias y establecer compromiso",
                "recursos": "Citación formal, posible visita domiciliaria",
                "prioridad": 5,
                "tiempo_estimado": "Inmediato"
            },
            {
                "tipo": "seguimiento_asistencia",
                "descripcion": "Monitoreo diario de asistencia con reporte inmediato",
                "estrategia": "Llamada telefónica el mismo día de ausencia injustificada",
                "recursos": "Sistema de comunicación con familias",
                "prioridad": 4,
                "tiempo_estimado": "Diario"
            },
            {
                "tipo": "apoyo_social",
                "descripcion": "Derivación a trabajo social",
                "estrategia": "Evaluación de trabajadora social para identificar problemas socioeconómicos o familiares",
                "recursos": "Trabajadora social, posibles becas o apoyos",
                "prioridad": 5,
                "tiempo_estimado": "1-2 semanas para evaluación"
            }
        ]
    },
    "conducta": {
        "bajo": [
            {
                "tipo": "evaluacion_psicopedagogica",
                "descripcion": "Evaluación con psicólogo educativo",
                "estrategia": "Sesiones con psicólogo para identificar causas de problemas conductuales",
                "recursos": "Psicólogo educativo, evaluaciones especializadas",
                "prioridad": 5,
                "tiempo_estimado": "1 mes para evaluación inicial"
            },
            {
                "tipo": "plan_conducta",
                "descripcion": "Implementar plan de manejo conductual",
                "estrategia": "Plan personalizado con objetivos claros, refuerzos positivos y consecuencias consistentes",
                "recursos": "Coordinación docente-familia, seguimiento diario",
                "prioridad": 4,
                "tiempo_estimado": "2-3 meses"
            },
            {
                "tipo": "actividades_extracurriculares",
                "descripcion": "Integración en actividades extracurriculares positivas",
                "estrategia": "Participación en deportes, arte, música u otras actividades de interés",
                "recursos": "Talleres extracurriculares, materiales",
                "prioridad": 3,
                "tiempo_estimado": "Continuo"
            }
        ]
    },
    "multiple": {
        "bajo": [
            {
                "tipo": "intervencion_integral",
                "descripcion": "Plan de intervención multidisciplinario",
                "estrategia": "Coordinación entre docentes, psicólogo, trabajadora social y familia para abordaje integral",
                "recursos": "Equipo multidisciplinario, reuniones de coordinación",
                "prioridad": 5,
                "tiempo_estimado": "3-6 meses con evaluaciones mensuales"
            },
            {
                "tipo": "adaptacion_curricular",
                "descripcion": "Considerar adaptaciones curriculares individualizadas",
                "estrategia": "Evaluación para determinar si requiere adaptaciones en contenidos o metodologías",
                "recursos": "Evaluación especializada, materiales adaptados",
                "prioridad": 4,
                "tiempo_estimado": "1 mes para evaluación"
            },
            {
                "tipo": "red_apoyo",
                "descripcion": "Activar red de apoyo institucional completa",
                "estrategia": "Involucrar a dirección, tutoría, departamento psicopedagógico y todos los docentes",
                "recursos": "Compromiso institucional, reuniones de equipo",
                "prioridad": 5,
                "tiempo_estimado": "Inmediato y continuo"
            }
        ]
    }
}


@router.post("/generar", response_model=RecomendacionResponse)
async def generar_recomendaciones(request: RecomendacionRequest):
    """
    Genera recomendaciones pedagógicas personalizadas para un estudiante
    
    **Categorías de deficiencia:**
    - `rendimiento`: Problemas en notas/calificaciones
    - `asistencia`: Problemas de inasistencias/tardanzas
    - `conducta`: Problemas de comportamiento
    - `multiple`: Combinación de varios problemas
    
    Las recomendaciones se priorizan según la severidad y se basan en
    mejores prácticas pedagógicas y experiencia docente.
    """
    try:
        logger.info(f"💡 Generando recomendaciones para estudiante {request.estudiante_id}")
        
        # Obtener datos del estudiante desde Supabase para contexto adicional
        from app.utils.supabase_client import get_supabase_client
        supabase = get_supabase_client()
        
        estudiante_response = supabase.table("estudiantes") \
            .select("*") \
            .eq("id", str(request.estudiante_id)) \
            .execute()
        
        if not estudiante_response.data:
            raise HTTPException(status_code=404, detail="Estudiante no encontrado")
        
        # Seleccionar estrategias según categoría y gravedad
        categoria = request.categoria_deficiencia.lower()
        
        # Determinar gravedad (por ahora usamos "bajo" por defecto)
        # En producción, esto se calcularía basándose en métricas específicas
        gravedad = "bajo"  # TODO: Calcular basándose en datos reales
        
        # Obtener estrategias de la base de conocimiento
        estrategias_disponibles = ESTRATEGIAS_PEDAGOGICAS.get(categoria, {}).get(gravedad, [])
        
        if not estrategias_disponibles:
            # Fallback: estrategias generales
            estrategias_disponibles = ESTRATEGIAS_PEDAGOGICAS["multiple"]["bajo"]
        
        # Convertir a objetos RecomendacionItem
        recomendaciones = [RecomendacionItem(**estrategia) for estrategia in estrategias_disponibles]
        
        # Calcular prioridad general (promedio de prioridades)
        prioridad_general = sum(r.prioridad for r in recomendaciones) // len(recomendaciones)
        
        # Observaciones adicionales basadas en el grado
        observaciones = self._generar_observaciones(request.grado, categoria)
        
        # Si hay alerta asociada, guardar recomendaciones en BD
        if request.alerta_id:
            await self._guardar_recomendaciones(
                str(request.alerta_id),
                recomendaciones
            )
        
        return RecomendacionResponse(
            estudiante_id=request.estudiante_id,
            categoria_deficiencia=categoria,
            recomendaciones=recomendaciones,
            total_recomendaciones=len(recomendaciones),
            prioridad_general=prioridad_general,
            observaciones=observaciones
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error generando recomendaciones: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar recomendaciones: {str(e)}"
        )


def _generar_observaciones(grado: int, categoria: str) -> str:
    """Genera observaciones adicionales según grado y categoría"""
    observaciones = []
    
    if grado in [1, 2]:
        observaciones.append("Estudiante en primeros años de secundaria requiere especial atención en adaptación.")
    elif grado == 5:
        observaciones.append("Estudiante en último año requiere preparación para educación superior o técnica.")
    
    if categoria == "rendimiento":
        observaciones.append("Importante identificar áreas específicas con dificultades para intervención focalizada.")
    elif categoria == "asistencia":
        observaciones.append("Las inasistencias tienen impacto directo en el aprendizaje. Abordar causas de raíz.")
    elif categoria == "conducta":
        observaciones.append("Los problemas conductuales pueden reflejar dificultades emocionales o familiares.")
    elif categoria == "multiple":
        observaciones.append("Situación compleja requiere abordaje coordinado de toda la institución.")
    
    return " ".join(observaciones)


async def _guardar_recomendaciones(alerta_id: str, recomendaciones: List[RecomendacionItem]):
    """Guarda las recomendaciones en la base de datos"""
    try:
        from app.utils.supabase_client import get_supabase_client
        supabase = get_supabase_client()
        
        for recom in recomendaciones:
            data = {
                "alerta_id": alerta_id,
                "tipo": recom.tipo,
                "descripcion": recom.descripcion,
                "estrategia": recom.estrategia,
                "recursos": recom.recursos,
                "prioridad": recom.prioridad
            }
            supabase.table("recomendaciones").insert(data).execute()
        
        logger.info(f"💾 {len(recomendaciones)} recomendaciones guardadas en BD")
    except Exception as e:
        logger.warning(f"⚠️ No se pudieron guardar recomendaciones: {e}")


@router.get("/estrategias")
async def listar_estrategias():
    """
    Lista todas las estrategias pedagógicas disponibles en el sistema
    
    Útil para que los docentes conozcan el catálogo de estrategias
    que el sistema puede sugerir.
    """
    return {
        "total_categorias": len(ESTRATEGIAS_PEDAGOGICAS),
        "estrategias": ESTRATEGIAS_PEDAGOGICAS
    }


@router.get("/por-alerta/{alerta_id}")
async def obtener_recomendaciones_alerta(alerta_id: str):
    """
    Obtiene las recomendaciones asociadas a una alerta específica
    
    Útil para ver qué estrategias se sugirieron para una alerta anterior
    """
    try:
        from app.utils.supabase_client import get_supabase_client
        supabase = get_supabase_client()
        
        response = supabase.table("recomendaciones") \
            .select("*") \
            .eq("alerta_id", alerta_id) \
            .execute()
        
        return {
            "alerta_id": alerta_id,
            "total_recomendaciones": len(response.data) if response.data else 0,
            "recomendaciones": response.data or []
        }
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo recomendaciones: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener recomendaciones: {str(e)}"
        )
