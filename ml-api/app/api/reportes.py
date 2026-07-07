"""
API de Reportes
Genera reportes en PDF y Excel para análisis y documentación
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import logging
from datetime import datetime
import os
from typing import Any, List
from datetime import date, timedelta
from collections import Counter

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

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


@router.get("/descargar/{nombre_archivo}")
async def descargar_reporte(nombre_archivo: str):
    """Descarga reportes generados desde el directorio configurado."""
    safe_name = os.path.basename(nombre_archivo)
    filepath = os.path.join(settings.reports_output_dir, safe_name)

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Reporte no encontrado")

    _, extension = os.path.splitext(safe_name.lower())
    media_type = (
        "application/pdf"
        if extension == ".pdf"
        else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        if extension == ".xlsx"
        else "application/octet-stream"
    )

    return FileResponse(filepath, media_type=media_type, filename=safe_name)


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
        logger.info(
            f"📄 Generando reporte de estudiantes en riesgo (formato: {request.formato})")

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
            url_descarga=f"/api/reportes/descargar/{nombre_archivo}" if nombre_archivo else None,
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
        periodo_ids = list(request.periodo_ids) if request.periodo_ids else []

        if not periodo_ids:
            periodos_resp = supabase.table("periodos").select("id").order("fecha_inicio", desc=True).limit(2).execute()
            periodo_ids = [p.get("id") for p in (periodos_resp.data or []) if p.get("id")]

        for periodo_id in periodo_ids:
            periodo_info = supabase.table("periodos").select("id, nombre, anio").eq("id", str(periodo_id)).limit(1).execute()
            periodo_row = (periodo_info.data or [{}])[0]

            # Obtener resumen del periodo filtrando por campos existentes en la vista
            query = supabase.table("vista_rendimiento_curso").select("*")
            if periodo_row.get("nombre"):
                query = query.eq("periodo", periodo_row.get("nombre"))
            if periodo_row.get("anio"):
                query = query.eq("anio", periodo_row.get("anio"))

            response = query.execute()

            datos_periodos.append({
                "periodo_id": str(periodo_id),
                "periodo_nombre": periodo_row.get("nombre", "Periodo"),
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
            url_descarga=f"/api/reportes/descargar/{nombre_archivo}",
            metadata={"periodos_analizados": len(periodo_ids)},
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

        fecha_fin = request.fecha_fin or date.today()
        fecha_inicio = request.fecha_inicio or (fecha_fin - timedelta(days=90))

        query = supabase.table("intervenciones").select("*") \
            .gte("fecha_inicio", str(fecha_inicio)) \
            .lte("fecha_inicio", str(fecha_fin))

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
            url_descarga=f"/api/reportes/descargar/{nombre_archivo}",
            metadata={
                "total_intervenciones": total,
                "exitosas": exitosas,
                "tasa_exito": round(tasa_exito, 2)
            },
            generado_en=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(
            f"❌ Error generando reporte de intervenciones: {e}", exc_info=True)
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

        # KPIs ligeros para evitar timeout de vistas pesadas
        estudiantes_resp = supabase.table("estudiantes").select("id", count="exact").eq("activo", True).limit(1).execute()
        alertas_resp = supabase.table("alertas").select("id", count="exact").in_("estado", ["activa", "en_atencion"]).limit(1).execute()
        notas_resp = supabase.table("notas").select("nota").limit(5000).execute()

        total_estudiantes = estudiantes_resp.count or 0
        total_alertas = alertas_resp.count or 0
        notas = [float(n.get("nota", 0)) for n in (notas_resp.data or []) if n.get("nota") is not None]
        promedio_general = (sum(notas) / len(notas)) if notas else 0

        datos = [{
            "total_estudiantes": total_estudiantes,
            "promedio_general": round(promedio_general, 2),
            "alertas_activas": total_alertas
        }]

        nombre_archivo = await _generar_pdf_resumen_institucional(datos, request)

        return ReporteResponse(
            tipo_reporte=TipoReporte.RESUMEN_INSTITUCIONAL,
            formato=request.formato,
            nombre_archivo=nombre_archivo,
            url_descarga=f"/api/reportes/descargar/{nombre_archivo}",
            metadata={
                "total_estudiantes": total_estudiantes,
                "promedio_general": round(promedio_general, 2),
                "total_alertas_activas": total_alertas
            },
            generado_en=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(
            f"❌ Error generando resumen institucional: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar resumen: {str(e)}"
        )


# ================================================
# FUNCIONES AUXILIARES DE GENERACIÓN
# ================================================

async def _generar_pdf_estudiantes_riesgo(datos: list, request) -> str:
    """Genera PDF de estudiantes en riesgo."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"estudiantes_riesgo_{timestamp}.pdf"
    filepath = os.path.join(settings.reports_output_dir, nombre_archivo)

    os.makedirs(settings.reports_output_dir, exist_ok=True)
    tipos_count = Counter(d.get("tipo", "sin_tipo") for d in datos)
    grados_count = Counter(f"{d.get('grado', '-')}{d.get('seccion', '')}" for d in datos)

    rows = [
        [
            d.get("estudiante_nombre", "Sin nombre"),
            f"{d.get('grado', '-')}{d.get('seccion', '')}",
            d.get("tipo", "-"),
            f"{float(d.get('nivel_riesgo', 0)) * 100:.1f}%" if d.get("nivel_riesgo") is not None else "-",
            d.get("motivo", "-"),
        ]
        for d in datos
    ]

    _crear_pdf(
        filepath,
        "Reporte Detallado de Estudiantes en Riesgo",
        [
            f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            f"Total de alertas activas: {len(datos)}",
            f"Criticas: {tipos_count.get('critica', 0)} | Moderadas: {tipos_count.get('moderada', 0)} | Preventivas: {tipos_count.get('preventiva', 0)}",
            "Este reporte resume estudiantes con riesgo academico detectado por el sistema y explica el motivo principal de cada alerta.",
            f"Grados con mayor carga de riesgo: {', '.join([f'{g}: {c}' for g, c in grados_count.most_common(5)]) or 'Sin datos'}",
        ],
        ["Estudiante", "Grado", "Tipo", "Nivel riesgo", "Motivo detallado"],
        rows,
    )

    logger.info(f"📄 PDF generado: {nombre_archivo}")
    return nombre_archivo


def _crear_pdf(filepath: str, titulo: str, resumen: List[str], headers: List[str], rows: List[List[Any]]) -> None:
    """Crea un PDF válido con una tabla básica."""
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    content = [Paragraph(titulo, styles["Title"]), Spacer(1, 12)]

    for item in resumen:
        content.append(Paragraph(str(item), styles["Normal"]))
    content.append(Spacer(1, 12))

    table_data = [headers] + [[str(value)[:90]
                               for value in row] for row in rows[:100]]
    if len(table_data) == 1:
        table_data.append(["Sin datos"] + [""] * (len(headers) - 1))

    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0ea5e9")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    content.append(table)
    doc.build(content)


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
    filepath = os.path.join(settings.reports_output_dir, nombre_archivo)
    os.makedirs(settings.reports_output_dir, exist_ok=True)

    filas = []
    for periodo in datos:
        filas.append([
            periodo.get("periodo_nombre", periodo.get("periodo_id", "-")),
            len(periodo.get("datos", []))
        ])

    _crear_pdf(
        filepath,
        "Reporte de Analisis de Periodo",
        [
            f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            f"Periodos analizados: {len(datos)}",
        ],
        ["Periodo", "Registros"],
        filas,
    )

    return nombre_archivo


async def _generar_pdf_intervenciones(datos: list, request) -> str:
    """Genera PDF de intervenciones"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"intervenciones_{timestamp}.pdf"
    filepath = os.path.join(settings.reports_output_dir, nombre_archivo)
    os.makedirs(settings.reports_output_dir, exist_ok=True)

    filas = [
        [
            d.get("tipo_intervencion", "-"),
            d.get("resultado", "-"),
            d.get("fecha_inicio", "-"),
        ]
        for d in datos
    ]

    _crear_pdf(
        filepath,
        "Reporte de Efectividad de Intervenciones",
        [
            f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            f"Total intervenciones: {len(datos)}",
        ],
        ["Tipo", "Resultado", "Fecha inicio"],
        filas,
    )

    return nombre_archivo


async def _generar_excel_intervenciones(datos: list, request) -> str:
    """Genera Excel de intervenciones"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"intervenciones_{timestamp}.xlsx"
    filepath = os.path.join(settings.reports_output_dir, nombre_archivo)
    os.makedirs(settings.reports_output_dir, exist_ok=True)
    with open(filepath, 'w') as f:
        f.write("Excel placeholder")
    return nombre_archivo


async def _generar_pdf_resumen_institucional(datos: list, request) -> str:
    """Genera PDF de resumen institucional"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"resumen_institucional_{timestamp}.pdf"
    filepath = os.path.join(settings.reports_output_dir, nombre_archivo)
    os.makedirs(settings.reports_output_dir, exist_ok=True)

    if len(datos) == 1 and "total_estudiantes" in datos[0]:
        total_estudiantes = int(datos[0].get("total_estudiantes", 0))
        promedio_general = float(datos[0].get("promedio_general", 0))
        total_alertas = int(datos[0].get("alertas_activas", 0))
    else:
        total_estudiantes = len(datos)
        promedio_general = (
            sum(d.get("promedio_general", 0) for d in datos) / len(datos)
            if datos else 0
        )
        total_alertas = sum(d.get("alertas_activas", 0) for d in datos)

    _crear_pdf(
        filepath,
        "Resumen Institucional",
        [
            f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            f"Total estudiantes: {total_estudiantes}",
            f"Promedio general: {round(promedio_general, 2)}",
            f"Alertas activas: {total_alertas}",
        ],
        ["Indicador", "Valor"],
        [
            ["Total estudiantes", total_estudiantes],
            ["Promedio general", round(promedio_general, 2)],
            ["Alertas activas", total_alertas],
        ],
    )

    return nombre_archivo
