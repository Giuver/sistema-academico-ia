"""
Schemas para predicciones ML
"""

from pydantic import BaseModel, Field, UUID4
from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum


class TipoPrediccion(str, Enum):
    """Tipos de predicción disponibles"""
    DESAPROBACION = "desaprobacion"
    DESERCION = "desercion"
    NOTA_ESTIMADA = "nota_estimada"


class PrediccionRequest(BaseModel):
    """Request para realizar una predicción"""
    estudiante_id: UUID4 = Field(..., description="ID del estudiante")
    periodo_id: Optional[UUID4] = Field(None, description="ID del periodo (opcional, usa actual si no se especifica)")
    tipo_prediccion: TipoPrediccion = Field(..., description="Tipo de predicción a realizar")
    
    class Config:
        json_schema_extra = {
            "example": {
                "estudiante_id": "550e8400-e29b-41d4-a716-446655440000",
                "periodo_id": "550e8400-e29b-41d4-a716-446655440001",
                "tipo_prediccion": "desaprobacion"
            }
        }


class PrediccionBatchRequest(BaseModel):
    """Request para predicciones en lote"""
    estudiantes_ids: List[UUID4] = Field(..., description="Lista de IDs de estudiantes")
    periodo_id: Optional[UUID4] = Field(None, description="ID del periodo")
    tipo_prediccion: TipoPrediccion = Field(..., description="Tipo de predicción")


class PrediccionResponse(BaseModel):
    """Response de una predicción"""
    estudiante_id: UUID4
    periodo_id: UUID4
    tipo_prediccion: TipoPrediccion
    probabilidad: Optional[float] = Field(None, ge=0.0, le=1.0, description="Probabilidad (0-1)")
    valor_estimado: Optional[float] = Field(None, description="Valor estimado (para nota_estimada)")
    confianza: float = Field(..., ge=0.0, le=1.0, description="Nivel de confianza del modelo")
    modelo_usado: str = Field(..., description="Nombre del modelo utilizado")
    version_modelo: str = Field(..., description="Versión del modelo")
    features_usadas: Dict = Field(..., description="Features utilizadas en la predicción")
    nivel_riesgo: str = Field(..., description="Clasificación del riesgo: bajo, medio, alto")
    recomendacion_alerta: bool = Field(..., description="Si se recomienda crear una alerta")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "estudiante_id": "550e8400-e29b-41d4-a716-446655440000",
                "periodo_id": "550e8400-e29b-41d4-a716-446655440001",
                "tipo_prediccion": "desaprobacion",
                "probabilidad": 0.75,
                "valor_estimado": None,
                "confianza": 0.87,
                "modelo_usado": "RandomForestClassifier",
                "version_modelo": "1.0.0",
                "features_usadas": {
                    "promedio_anterior": 12.5,
                    "tasa_asistencia": 0.82,
                    "conducta_score": 0.85
                },
                "nivel_riesgo": "alto",
                "recomendacion_alerta": True,
                "timestamp": "2026-04-19T20:00:00"
            }
        }


class PrediccionBatchResponse(BaseModel):
    """Response para predicciones en lote"""
    total_predicciones: int
    exitosas: int
    fallidas: int
    predicciones: List[PrediccionResponse]
    errores: Optional[List[Dict]] = None


class MetricasModeloResponse(BaseModel):
    """Métricas de evaluación de un modelo"""
    modelo_nombre: str
    version: str
    tipo_modelo: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: Optional[float] = None
    fecha_entrenamiento: datetime
    dataset_size: int
    activo: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "modelo_nombre": "RandomForestClassifier",
                "version": "1.0.0",
                "tipo_modelo": "clasificacion",
                "accuracy": 0.87,
                "precision": 0.85,
                "recall": 0.82,
                "f1_score": 0.835,
                "roc_auc": 0.91,
                "fecha_entrenamiento": "2026-04-01T10:00:00",
                "dataset_size": 500,
                "activo": True
            }
        }


class EntrenarModeloRequest(BaseModel):
    """Request para entrenar un modelo"""
    tipo_modelo: str = Field(..., description="Tipo de modelo: random_forest, xgboost, gradient_boosting")
    hiperparametros: Optional[Dict] = Field(None, description="Hiperparámetros personalizados")
    usar_grid_search: bool = Field(False, description="Usar GridSearchCV para optimizar")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tipo_modelo": "random_forest",
                "hiperparametros": {
                    "n_estimators": 100,
                    "max_depth": 10
                },
                "usar_grid_search": False
            }
        }
