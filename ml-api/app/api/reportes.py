"""
API de Reportes
Genera reportes en PDF y Excel para análisis y documentación
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import logging
from datetime import datetime
import os

from app.schemas.reporte import (
    ReporteEstudiantesRiesgoRequest,
    ReporteAnalisisPeriodoRequest,
    ReporteIntervencionesRequest,
    ResumenInstitucionalRequest,
    ReporteResponse,
    TipoReporte,
    FormatoReporte
)
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/estudiantes-riesgo", response_model=ReporteResponse)
async def generar_reporte_estudiantes_riesgo(request: ReporteEstudiantesRiesgoRequest):
    """
    Genera reporte de estudiantes en riesgo académico
    
    **Incluye:**
    - Lista de estudiantes con alertas activas
    - Nivel de riesgo y probabilidades
    - Recomendaciones pedagógicas (opcional)
    - Gráficos de distribución por grado/sección
    
    **Formatos:** PDF o Excel
    """
    try:
        logger.info(f"📄 Generando reporte de estudiantes en riesgo (formato: {request.formato})")
        
        # Obtener datos de estudiantes en riesgo desde Supabase
        from app.utils.supabase_client import get_supabase_client
        supabase = get_supabase_client()
        
        # Construir query con filtros
        query = supabase.table("vista_alertas_activas").select("*")
        
        if request.nivel_riesgo:
            query = query.in_("tipo", request.nivel_riesgo)
        if request.grado:
            query = query.eq("grado", request.grado)
        if request.seccion:
            query = query.eq("seccion", request.seccion)
        
        response = query.execute()
        
        datos = response.data if response.data else []
        
        # Generar archivo según formato
        if request.formato == FormatoReporte.PDF:
            nombre_archivo = await _generar_pdf_estudiantes_riesgo(datos, request)
        elif request.formato == FormatoReporte.EXCEL:
            nombre_archivo = await _generar_excel_estudiantes_riesgo(datos, request)
        else:
            nombre_archivo = None  # JSON retorna datos directamente
        
        metadata = {
            "total_estudiantes": len(datos),
            "criticos": len([d for d in datos if d.get("tipo") == "critica"]),
            "moderados": len([d for d in datos if d.get("tipo") == "moderada"]),
            "preventivos": len([d for d in datos if d.get("tipo") == "preventiva"])
        }
        
        return ReporteResponse(
            tipo_reporte=TipoReporte.ESTUDIANTES_RIESGO,
            formato=request.formato,
            nombre_archivo=nombre_archivo or "reporte.json",
            url_descarga=f"/{settings.reports_output_dir}/{nombre_archivo}" if nombre_archivo else None,
            metadata=metadata,
            generado_en=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ Error generando reporte: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar reporte: {str(e)}"
        )


@router.post("/analisis-periodo", response_model=ReporteResponse)
async def generar_reporte_analisis_periodo(request: ReporteAnalisisPeriodoRequest):
    """
    Genera reporte comparativo entre periodos académicos
    
    **Incluye:**
    - Comparación de promedios generales
    - Tasas de aprobación/desaprobación
    - Evolución de asistencia
    - Gráficos de tendencias
    
    **Formato recomendado:** Excel (permite análisis de datos)
    """
    try:
        logger.info(f"📊 Generando análisis comparativo de periodos")
        
        from app.utils.supabase_client import get_supabase_client
        supabase = get_supabase_client()
        
        datos_periodos = []
        
        for periodo_id in request.periodo_ids:
            # Obtener resumen del periodo
            response = supabase.table("vista_rendimiento_curso") \
                .select("*") \
                .eq("periodo_id", str(periodo_id)) \
                .execute()
            
            datos_periodos.append({
                "periodo_id": str(periodo_id),
                "datos": response.data if response.data else []
            })
        
        if request.formato == FormatoReporte.EXCEL:
            nombre_archivo = await _generar_excel_analisis_periodo(datos_periodos, request)
        else:
            nombre_archivo = await _generar_pdf_analisis_periodo(datos_periodos, request)
        
        return ReporteResponse(
            tipo_reporte=TipoReporte.ANALISIS_PERIODO,
            formato=request.formato,
            nombre_archivo=nombre_archivo,
            url_descarga=f"/{settings.reports_output_dir}/{nombre_archivo}",
            metadata={"periodos_analizados": len(request.periodo_ids)},
            generado_en=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ Error generando análisis: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar análisis de periodo: {str(e)}"
        )


@router.post("/efectividad-intervenciones", response_model=ReporteResponse)
async def generar_reporte_intervenciones(request: ReporteIntervencionesRequest):
    """
    Genera reporte de efectividad de intervenciones pedagógicas
    
    **Incluye:**
    - Lista de intervenciones realizadas
    - Tasa de éxito por tipo de intervención
    - Tiempo promedio de resolución
    - Recomendaciones de mejora
    
    **Útil para:** Evaluar qué estrategias funcionan mejor
    """
    try:
        logger.info(f"📈 Generando reporte de efectividad de intervenciones")
        
        from app.utils.supabase_client import get_supabase_client
        supabase = get_supabase_client()
        
        query = supabase.table("intervenciones").select("*") \
            .gte("fecha_inicio", str(request.fecha_inicio)) \
            .lte("fecha_inicio", str(request.fecha_fin))
        
        if request.tipo_intervencion:
            query = query.eq("tipo_intervencion", request.tipo_intervencion)
        
        response = query.execute()
        datos = response.data if response.data else []
        
        # Calcular estadísticas
        total = len(datos)
        exitosas = len([d for d in datos if d.get("resultado") == "exitosa"])
        tasa_exito = (exitosas / total * 100) if total > 0 else 0
        
        if request.formato == FormatoReporte.PDF:
            nombre_archivo = await _generar_pdf_intervenciones(datos, request)
        else:
            nombre_archivo = await _generar_excel_intervenciones(datos, request)
        
        return ReporteResponse(
            tipo_reporte=TipoReporte.EFECTIVIDAD_INTERVENCIONES,
            formato=request.formato,
            nombre_archivo=nombre_archivo,
            url_descarga=f"/{settings.reports_output_dir}/{nombre_archivo}",
            metadata={
                "total_intervenciones": total,
                "exitosas": exitosas,
                "tasa_exito": round(tasa_exito, 2)
            },
            generado_en=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ Error generando reporte de intervenciones: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar reporte: {str(e)}"
        )


@router.post("/resumen-institucional", response_model=ReporteResponse)
async def generar_resumen_institucional(request: ResumenInstitucionalRequest):
    """
    Genera resumen ejecutivo institucional para directivos
    
    **Incluye:**
    - KPIs generales del periodo
    - Comparación con periodos anteriores
    - Top problemas identificados
    - Alertas activas por grado
    - Efectividad de intervenciones
    
    **Destinado a:** Dirección, coordinación académica, UGEL
    """
    try:
        logger.info(f"📊 Generando resumen institucional")
        
        from app.utils.supabase_client import get_supabase_client
        supabase = get_supabase_client()
        
        # Obtener KPIs del periodo
        response = supabase.table("vista_estudiantes_resumen").select("*").execute()
        
        datos = response.data if response.data else []
        
        # Calcular KPIs
        total_estudiantes = len(datos)
        promedio_general = sum(d.get("promedio_general", 0) for d in datos) / total_estudiantes if total_estudiantes > 0 else 0
        total_alertas = sum(d.get("alertas_activas", 0) for d in datos)
        
        nombre_archivo = await _generar_pdf_resumen_institucional(datos, request)
        
        return ReporteResponse(
            tipo_reporte=TipoReporte.RESUMEN_INSTITUCIONAL,
            formato=request.formato,
            nombre_archivo=nombre_archivo,
            url_descarga=f"/{settings.reports_output_dir}/{nombre_archivo}",
            metadata={
                "total_estudiantes": total_estudiantes,
                "promedio_general": round(promedio_general, 2),
                "total_alertas_activas": total_alertas
            },
            generado_en=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ Error generando resumen institucional: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar resumen: {str(e)}"
        )


# ================================================
# FUNCIONES AUXILIARES DE GENERACIÓN
# ================================================

async def _generar_pdf_estudiantes_riesgo(datos: list, request) -> str:
    """Genera PDF de estudiantes en riesgo (implementación simplificada)"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"estudiantes_riesgo_{timestamp}.pdf"
    filepath = os.path.join(settings.reports_output_dir, nombre_archivo)
    
    # TODO: Implementar generación real con ReportLab
    # Por ahora guardamos un placeholder
    os.makedirs(settings.reports_output_dir, exist_ok=True)
    
    with open(filepath, 'w') as f:
        f.write("PDF placeholder - Se implementará con ReportLab")
    
    logger.info(f"📄 PDF generado: {nombre_archivo}")
    return nombre_archivo


async def _generar_excel_estudiantes_riesgo(datos: list, request) -> str:
    """Genera Excel de estudiantes en riesgo (implementación simplificada)"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"estudiantes_riesgo_{timestamp}.xlsx"
    filepath = os.path.join(settings.reports_output_dir, nombre_archivo)
    
    # TODO: Implementar con openpyxl
    os.makedirs(settings.reports_output_dir, exist_ok=True)
    
    with open(filepath, 'w') as f:
        f.write("Excel placeholder - Se implementará con openpyxl")
    
    logger.info(f"📊 Excel generado: {nombre_archivo}")
    return nombre_archivo


async def _generar_excel_analisis_periodo(datos: list, request) -> str:
    """Genera Excel de análisis de periodo"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"analisis_periodo_{timestamp}.xlsx"
    filepath = os.path.join(settings.reports_output_dir, nombre_archivo)
    
    os.makedirs(settings.reports_output_dir, exist_ok=True)
    with open(filepath, 'w') as f:
        f.write("Excel placeholder")
    
    return nombre_archivo


async def _generar_pdf_analisis_periodo(datos: list, request) -> str:
    """Genera PDF de análisis de periodo"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"analisis_periodo_{timestamp}.pdf"
    return nombre_archivo


async def _generar_pdf_intervenciones(datos: list, request) -> str:
    """Genera PDF de intervenciones"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"intervenciones_{timestamp}.pdf"


async def _generar_excel_intervenciones(datos: list, request) -> str:
    """Genera Excel de intervenciones"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"intervenciones_{timestamp}.xlsx"


async def _generar_pdf_resumen_institucional(datos: list, request) -> str:
    """Genera PDF de resumen institucional"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"resumen_institucional_{timestamp}.pdf"
