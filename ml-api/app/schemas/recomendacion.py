"""
Schemas para recomendaciones pedagógicas
"""

from pydantic import BaseModel, Field, UUID4
from typing import List, Optional
from datetime import datetime


class RecomendacionRequest(BaseModel):
    """Request para generar recomendaciones"""
    estudiante_id: UUID4 = Field(..., description="ID del estudiante")
    alerta_id: Optional[UUID4] = Field(None, description="ID de la alerta asociada")
    categoria_deficiencia: str = Field(..., description="Categoría: rendimiento, asistencia, conducta, multiple")
    grado: int = Field(..., ge=1, le=5, description="Grado del estudiante")
    
    class Config:
        json_schema_extra = {
            "example": {
                "estudiante_id": "550e8400-e29b-41d4-a716-446655440000",
                "alerta_id": "550e8400-e29b-41d4-a716-446655440002",
                "categoria_deficiencia": "rendimiento",
                "grado": 3
            }
        }


class RecomendacionItem(BaseModel):
    """Una recomendación específica"""
    tipo: str = Field(..., description="Tipo de recomendación")
    descripcion: str = Field(..., description="Descripción de la recomendación")
    estrategia: str = Field(..., description="Estrategia a implementar")
    recursos: Optional[str] = Field(None, description="Recursos necesarios")
    prioridad: int = Field(..., ge=1, le=5, description="Prioridad (1=baja, 5=alta)")
    tiempo_estimado: Optional[str] = Field(None, description="Tiempo estimado de implementación")


class RecomendacionResponse(BaseModel):
    """Response con recomendaciones generadas"""
    estudiante_id: UUID4
    categoria_deficiencia: str
    recomendaciones: List[RecomendacionItem]
    total_recomendaciones: int
    prioridad_general: int
    observaciones: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "estudiante_id": "550e8400-e29b-41d4-a716-446655440000",
                "categoria_deficiencia": "rendimiento",
                "recomendaciones": [
                    {
                        "tipo": "reforzamiento_academico",
                        "descripcion": "Implementar sesiones de reforzamiento en matemática y comunicación",
                        "estrategia": "Clases de refuerzo 2 veces por semana (1 hora cada sesión)",
                        "recursos": "Material didáctico adicional, espacio para tutorías",
                        "prioridad": 5,
                        "tiempo_estimado": "2 meses"
                    }
                ],
                "total_recomendaciones": 3,
                "prioridad_general": 4,
                "observaciones": "Estudiante muestra dificultades en áreas de matemática",
                "timestamp": "2026-04-19T20:00:00"
            }
        }


class EstrategiaPedagogicaBase(BaseModel):
    """Estrategia pedagógica base"""
    nombre: str
    descripcion: str
    aplicable_a: List[str]  # ['rendimiento', 'asistencia', 'conducta']
    grados: List[int]  # [1, 2, 3, 4, 5]
    efectividad_esperada: float  # 0-1
