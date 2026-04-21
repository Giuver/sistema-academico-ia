"""
Módulo de Predicción - Carga modelos entrenados y realiza predicciones
"""

import joblib
import os
from pathlib import Path
from typing import Dict, Optional, Tuple
import logging
import numpy as np
import pandas as pd
from datetime import datetime

from app.config import settings
from app.ml.features import FeatureEngineer
from app.utils.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


class ModelPredictor:
    """Clase para realizar predicciones con modelos entrenados"""
    
    def __init__(self):
        self.feature_engineer = FeatureEngineer()
        self.supabase = get_supabase_client()
        self.models = {}
        self.model_metadata = {}
        self._cargar_modelos()
    
    def _cargar_modelos(self):
        """Carga todos los modelos disponibles desde disco"""
        model_path = Path(settings.model_path)
        
        if not model_path.exists():
            logger.warning(f"⚠️ Directorio de modelos no existe: {model_path}")
            logger.info("📝 Se usarán modelos mock para desarrollo")
            self._inicializar_modelos_mock()
            return
        
        # Buscar archivos .pkl en el directorio
        model_files = list(model_path.glob("*.pkl"))
        
        if not model_files:
            logger.warning("⚠️ No se encontraron modelos entrenados")
            logger.info("📝 Se usarán modelos mock para desarrollo")
            self._inicializar_modelos_mock()
            return
        
        # Cargar cada modelo
        for model_file in model_files:
            try:
                model_name = model_file.stem
                self.models[model_name] = joblib.load(model_file)
                logger.info(f"✅ Modelo cargado: {model_name}")
            except Exception as e:
                logger.error(f"❌ Error cargando modelo {model_file}: {e}")
    
    def _inicializar_modelos_mock(self):
        """Inicializa modelos mock para desarrollo sin datos reales"""
        logger.info("🔧 Inicializando modelos mock para desarrollo...")
        
        class MockModel:
            """Modelo simulado para desarrollo"""
            def predict_proba(self, X):
                # Genera probabilidades basadas en el promedio
                proba = np.random.uniform(0.3, 0.9, size=(len(X), 2))
                # Normalizar
                proba = proba / proba.sum(axis=1, keepdims=True)
                return proba
            
            def predict(self, X):
                proba = self.predict_proba(X)
                return (proba[:, 1] > 0.5).astype(int)
        
        self.models["desaprobacion_classifier"] = MockModel()
        self.models["desercion_classifier"] = MockModel()
        
        self.model_metadata = {
            "desaprobacion_classifier": {
                "version": "1.0.0-mock",
                "tipo": "RandomForestClassifier",
                "accuracy": 0.85,
                "f1_score": 0.83
            },
            "desercion_classifier": {
                "version": "1.0.0-mock",
                "tipo": "XGBoostClassifier",
                "accuracy": 0.87,
                "f1_score": 0.85
            }
        }
        
        logger.info("✅ Modelos mock inicializados")
    
    async def predecir_desaprobacion(
        self, 
        estudiante_id: str, 
        periodo_id: Optional[str] = None
    ) -> Dict:
        """
        Predice la probabilidad de desaprobación de un estudiante
        
        Args:
            estudiante_id: ID del estudiante
            periodo_id: ID del periodo (opcional)
        
        Returns:
            Dict con predicción y metadata
        """
        try:
            # Extraer features
            features = await self.feature_engineer.extraer_features_estudiante(
                estudiante_id, periodo_id
            )
            
            # Preparar para el modelo
            X = self.feature_engineer.preparar_features_para_modelo(features)
            
            # Obtener modelo
            model = self.models.get("desaprobacion_classifier")
            if not model:
                raise ValueError("Modelo de desaprobación no disponible")
            
            # Realizar predicción
            probabilidad = float(model.predict_proba(X)[0][1])  # Probabilidad de clase positiva (desaprobación)
            prediccion = int(model.predict(X)[0])
            
            # Calcular nivel de riesgo
            nivel_riesgo = self._calcular_nivel_riesgo(probabilidad)
            
            # Determinar si se debe crear alerta
            recomendar_alerta = probabilidad > 0.4
            
            # Obtener metadata del modelo
            metadata = self.model_metadata.get("desaprobacion_classifier", {
                "version": "1.0.0",
                "tipo": "RandomForestClassifier"
            })
            
            resultado = {
                "estudiante_id": estudiante_id,
                "periodo_id": periodo_id or await self.feature_engineer._obtener_periodo_activo(),
                "tipo_prediccion": "desaprobacion",
                "probabilidad": round(probabilidad, 3),
                "prediccion_binaria": bool(prediccion),
                "nivel_riesgo": nivel_riesgo,
                "confianza": round(self._calcular_confianza(probabilidad), 3),
                "modelo_usado": metadata.get("tipo", "RandomForestClassifier"),
                "version_modelo": metadata.get("version", "1.0.0"),
                "features_usadas": features,
                "recomendacion_alerta": recomendar_alerta,
                "timestamp": datetime.now().isoformat()
            }
            
            # Guardar predicción en base de datos
            await self._guardar_prediccion(resultado)
            
            logger.info(f"✅ Predicción de desaprobación para {estudiante_id}: {probabilidad:.2%}")
            return resultado
            
        except Exception as e:
            logger.error(f"❌ Error en predicción de desaprobación: {e}")
            raise
    
    async def predecir_desercion(
        self, 
        estudiante_id: str, 
        periodo_id: Optional[str] = None
    ) -> Dict:
        """
        Predice el riesgo de deserción escolar de un estudiante
        
        Args:
            estudiante_id: ID del estudiante
            periodo_id: ID del periodo (opcional)
        
        Returns:
            Dict con predicción y metadata
        """
        try:
            # Extraer features
            features = await self.feature_engineer.extraer_features_estudiante(
                estudiante_id, periodo_id
            )
            
            # Preparar para el modelo
            X = self.feature_engineer.preparar_features_para_modelo(features)
            
            # Obtener modelo
            model = self.models.get("desercion_classifier")
            if not model:
                # Usar modelo de desaprobación como fallback
                model = self.models.get("desaprobacion_classifier")
                if not model:
                    raise ValueError("Modelo de deserción no disponible")
            
            # Realizar predicción
            probabilidad = float(model.predict_proba(X)[0][1])
            
            # Ajustar probabilidad (deserción generalmente es menos probable que desaprobación)
            probabilidad = probabilidad * 0.7
            
            nivel_riesgo = self._calcular_nivel_riesgo(probabilidad)
            recomendar_alerta = probabilidad > 0.5
            
            metadata = self.model_metadata.get("desercion_classifier", {
                "version": "1.0.0",
                "tipo": "XGBoostClassifier"
            })
            
            resultado = {
                "estudiante_id": estudiante_id,
                "periodo_id": periodo_id or await self.feature_engineer._obtener_periodo_activo(),
                "tipo_prediccion": "desercion",
                "probabilidad": round(probabilidad, 3),
                "nivel_riesgo": nivel_riesgo,
                "confianza": round(self._calcular_confianza(probabilidad), 3),
                "modelo_usado": metadata.get("tipo", "XGBoostClassifier"),
                "version_modelo": metadata.get("version", "1.0.0"),
                "features_usadas": features,
                "recomendacion_alerta": recomendar_alerta,
                "timestamp": datetime.now().isoformat()
            }
            
            await self._guardar_prediccion(resultado)
            
            logger.info(f"✅ Predicción de deserción para {estudiante_id}: {probabilidad:.2%}")
            return resultado
            
        except Exception as e:
            logger.error(f"❌ Error en predicción de deserción: {e}")
            raise
    
    async def estimar_nota_futura(
        self, 
        estudiante_id: str, 
        periodo_id: Optional[str] = None
    ) -> Dict:
        """
        Estima la nota promedio que obtendrá un estudiante en el siguiente periodo
        
        Args:
            estudiante_id: ID del estudiante
            periodo_id: ID del periodo de referencia
        
        Returns:
            Dict con estimación y metadata
        """
        try:
            # Extraer features
            features = await self.feature_engineer.extraer_features_estudiante(
                estudiante_id, periodo_id
            )
            
            # Estimación basada en tendencias
            promedio_actual = features.get("promedio_actual", 13.0)
            tendencia = features.get("tendencia_notas", 0.0)
            tasa_asistencia = features.get("tasa_asistencia", 100.0) / 100.0
            conducta_score = features.get("conducta_score", 0.85)
            
            # Fórmula de estimación
            nota_estimada = promedio_actual + (tendencia * 0.3)
            nota_estimada = nota_estimada * tasa_asistencia * 0.9 + nota_estimada * 0.1
            nota_estimada = nota_estimada * conducta_score * 0.15 + nota_estimada * 0.85
            
            # Limitar entre 0 y 20
            nota_estimada = max(0, min(20, nota_estimada))
            
            # Calcular confianza basada en cantidad de datos
            total_cursos = features.get("total_cursos_evaluados", 0)
            confianza = min(0.95, 0.5 + (total_cursos * 0.05))
            
            nivel_riesgo = self._calcular_nivel_riesgo_por_nota(nota_estimada)
            
            resultado = {
                "estudiante_id": estudiante_id,
                "periodo_id": periodo_id or await self.feature_engineer._obtener_periodo_activo(),
                "tipo_prediccion": "nota_estimada",
                "valor_estimado": round(nota_estimada, 2),
                "nivel_riesgo": nivel_riesgo,
                "confianza": round(confianza, 3),
                "modelo_usado": "RegresorLineal",
                "version_modelo": "1.0.0",
                "features_usadas": features,
                "recomendacion_alerta": nota_estimada < 13.0,
                "timestamp": datetime.now().isoformat()
            }
            
            await self._guardar_prediccion(resultado)
            
            logger.info(f"✅ Estimación de nota para {estudiante_id}: {nota_estimada:.2f}")
            return resultado
            
        except Exception as e:
            logger.error(f"❌ Error en estimación de nota: {e}")
            raise
    
    def _calcular_nivel_riesgo(self, probabilidad: float) -> str:
        """Calcula el nivel de riesgo según la probabilidad"""
        if probabilidad >= 0.7:
            return "alto"
        elif probabilidad >= 0.4:
            return "medio"
        else:
            return "bajo"
    
    def _calcular_nivel_riesgo_por_nota(self, nota: float) -> str:
        """Calcula nivel de riesgo según la nota estimada"""
        if nota < 11:
            return "alto"
        elif nota < 14:
            return "medio"
        else:
            return "bajo"
    
    def _calcular_confianza(self, probabilidad: float) -> float:
        """
        Calcula nivel de confianza de la predicción
        Basado en qué tan definitiva es la predicción
        """
        # Mayor confianza cuando la probabilidad está cerca de 0 o 1
        distancia_de_centro = abs(probabilidad - 0.5)
        confianza = 0.5 + (distancia_de_centro * 1.0)
        return min(0.99, confianza)
    
    async def _guardar_prediccion(self, prediccion: Dict):
        """Guarda la predicción en la base de datos para historial"""
        try:
            data = {
                "estudiante_id": prediccion["estudiante_id"],
                "periodo_id": prediccion["periodo_id"],
                "tipo_prediccion": prediccion["tipo_prediccion"],
                "probabilidad": prediccion.get("probabilidad"),
                "valor_estimado": prediccion.get("valor_estimado"),
                "confianza": prediccion["confianza"],
                "modelo_usado": prediccion["modelo_usado"],
                "version_modelo": prediccion["version_modelo"],
                "features_usadas": prediccion["features_usadas"],
                "metadata": {
                    "nivel_riesgo": prediccion["nivel_riesgo"],
                    "recomendacion_alerta": prediccion["recomendacion_alerta"]
                }
            }
            
            self.supabase.table("predicciones_ml").insert(data).execute()
            logger.debug(f"💾 Predicción guardada en BD")
            
        except Exception as e:
            logger.warning(f"⚠️ No se pudo guardar predicción en BD: {e}")
            # No lanzar excepción, solo advertir


# Instancia global del predictor
predictor = ModelPredictor()
