"""
Schemas para generación de reportes
"""

from pydantic import BaseModel, Field, UUID4
from typing import List, Optional
from datetime import date
from enum import Enum


class FormatoReporte(str, Enum):
    """Formatos disponibles para reportes"""
    PDF = "pdf"
    EXCEL = "excel"
    JSON = "json"


class TipoReporte(str, Enum):
    """Tipos de reporte disponibles"""
    ESTUDIANTES_RIESGO = "estudiantes_riesgo"
    ANALISIS_PERIODO = "analisis_periodo"
    EFECTIVIDAD_INTERVENCIONES = "efectividad_intervenciones"
    METRICAS_MODELO = "metricas_modelo"
    RESUMEN_INSTITUCIONAL = "resumen_institucional"


class ReporteEstudiantesRiesgoRequest(BaseModel):
    """Request para reporte de estudiantes en riesgo"""
    nivel_riesgo: Optional[List[str]] = Field(None, description="Filtrar por nivel: ['critica', 'moderada', 'preventiva']")
    grado: Optional[int] = Field(None, ge=1, le=5, description="Filtrar por grado")
    seccion: Optional[str] = Field(None, description="Filtrar por sección")
    incluir_recomendaciones: bool = Field(True, description="Incluir recomendaciones en el reporte")
    formato: FormatoReporte = Field(FormatoReporte.PDF, description="Formato del reporte")
    
    class Config:
        json_schema_extra = {
            "example": {
                "nivel_riesgo": ["critica", "moderada"],
                "grado": 3,
                "seccion": "A",
                "incluir_recomendaciones": True,
                "formato": "pdf"
            }
        }


class ReporteAnalisisPeriodoRequest(BaseModel):
    """Request para análisis comparativo de periodos"""
    periodo_ids: List[UUID4] = Field(..., description="IDs de periodos a comparar")
    grado: Optional[int] = Field(None, ge=1, le=5)
    incluir_graficos: bool = Field(True, description="Incluir gráficos estadísticos")
    formato: FormatoReporte = Field(FormatoReporte.EXCEL)
    
    class Config:
        json_schema_extra = {
            "example": {
                "periodo_ids": [
                    "550e8400-e29b-41d4-a716-446655440001",
                    "550e8400-e29b-41d4-a716-446655440002"
                ],
                "grado": None,
                "incluir_graficos": True,
                "formato": "excel"
            }
        }


class ReporteIntervencionesRequest(BaseModel):
    """Request para reporte de efectividad de intervenciones"""
    fecha_inicio: date = Field(..., description="Fecha de inicio del periodo de análisis")
    fecha_fin: date = Field(..., description="Fecha de fin del periodo de análisis")
    tipo_intervencion: Optional[str] = Field(None, description="Filtrar por tipo de intervención")
    formato: FormatoReporte = Field(FormatoReporte.PDF)
    
    class Config:
        json_schema_extra = {
            "example": {
                "fecha_inicio": "2026-01-01",
                "fecha_fin": "2026-04-19",
                "tipo_intervencion": "reforzamiento_academico",
                "formato": "pdf"
            }
        }


class ReporteResponse(BaseModel):
    """Response genérica para reportes"""
    tipo_reporte: TipoReporte
    formato: FormatoReporte
    nombre_archivo: str
    url_descarga: Optional[str] = None
    contenido_base64: Optional[str] = None  # Para respuestas directas
    metadata: dict = Field(default_factory=dict)
    generado_en: str = Field(..., description="Timestamp de generación")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tipo_reporte": "estudiantes_riesgo",
                "formato": "pdf",
                "nombre_archivo": "reporte_estudiantes_riesgo_20260419.pdf",
                "url_descarga": "/reports/reporte_estudiantes_riesgo_20260419.pdf",
                "contenido_base64": None,
                "metadata": {
                    "total_estudiantes": 45,
                    "criticos": 12,
                    "moderados": 18,
                    "preventivos": 15
                },
                "generado_en": "2026-04-19T20:30:00"
            }
        }


class ResumenInstitucionalRequest(BaseModel):
    """Request para resumen institucional"""
    periodo_id: UUID4 = Field(..., description="ID del periodo a analizar")
    incluir_comparativas: bool = Field(True, description="Incluir comparativas con periodos anteriores")
    formato: FormatoReporte = Field(FormatoReporte.PDF)
