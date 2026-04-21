"""
Feature Engineering - Extracción y transformación de características
para modelos de Machine Learning
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime, timedelta

from app.utils.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Clase para ingeniería de características académicas"""
    
    def __init__(self):
        self.supabase = get_supabase_client()
    
    async def extraer_features_estudiante(
        self, 
        estudiante_id: str, 
        periodo_id: Optional[str] = None
    ) -> Dict:
        """
        Extrae todas las características relevantes de un estudiante
        para predicción de rendimiento académico
        
        Args:
            estudiante_id: ID del estudiante
            periodo_id: ID del periodo (opcional, usa el actual si no se especifica)
        
        Returns:
            Diccionario con todas las features calculadas
        """
        try:
            # Obtener datos del estudiante
            estudiante = await self._obtener_datos_estudiante(estudiante_id)
            
            # Obtener periodo actual si no se especifica
            if not periodo_id:
                periodo_id = await self._obtener_periodo_activo()
            
            # Extraer features por categoría
            features_notas = await self._features_notas(estudiante_id, periodo_id)
            features_asistencia = await self._features_asistencia(estudiante_id, periodo_id)
            features_conducta = await self._features_conducta(estudiante_id, periodo_id)
            features_demograficas = self._features_demograficas(estudiante)
            features_historicas = await self._features_historicas(estudiante_id, periodo_id)
            
            # Combinar todas las features
            features = {
                **features_notas,
                **features_asistencia,
                **features_conducta,
                **features_demograficas,
                **features_historicas
            }
            
            logger.info(f"✅ Features extraídas para estudiante {estudiante_id}: {len(features)} características")
            return features
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo features para estudiante {estudiante_id}: {e}")
            raise
    
    async def _obtener_datos_estudiante(self, estudiante_id: str) -> Dict:
        """Obtiene datos básicos del estudiante"""
        response = self.supabase.table("estudiantes").select("*").eq("id", estudiante_id).execute()
        if not response.data:
            raise ValueError(f"Estudiante {estudiante_id} no encontrado")
        return response.data[0]
    
    async def _obtener_periodo_activo(self) -> str:
        """Obtiene el ID del periodo activo actual"""
        response = self.supabase.table("periodos").select("id").eq("activo", True).execute()
        if not response.data:
            raise ValueError("No hay periodo activo configurado")
        return response.data[0]["id"]
    
    async def _features_notas(self, estudiante_id: str, periodo_id: str) -> Dict:
        """Extrae features relacionadas con notas"""
        # Obtener todas las notas del estudiante
        response = self.supabase.table("notas") \
            .select("nota, curso_id, periodo_id") \
            .eq("estudiante_id", estudiante_id) \
            .execute()
        
        if not response.data:
            return {
                "promedio_actual": 0.0,
                "promedio_anterior": 0.0,
                "tendencia_notas": 0.0,
                "desviacion_std_notas": 0.0,
                "nota_min": 0.0,
                "nota_max": 0.0,
                "total_cursos_evaluados": 0,
                "cursos_desaprobados": 0,
                "porcentaje_aprobacion": 0.0
            }
        
        df_notas = pd.DataFrame(response.data)
        
        # Notas del periodo actual
        notas_actuales = df_notas[df_notas["periodo_id"] == periodo_id]["nota"]
        
        # Notas de periodos anteriores
        notas_anteriores = df_notas[df_notas["periodo_id"] != periodo_id]["nota"]
        
        promedio_actual = float(notas_actuales.mean()) if len(notas_actuales) > 0 else 0.0
        promedio_anterior = float(notas_anteriores.mean()) if len(notas_anteriores) > 0 else 0.0
        
        return {
            "promedio_actual": round(promedio_actual, 2),
            "promedio_anterior": round(promedio_anterior, 2),
            "tendencia_notas": round(promedio_actual - promedio_anterior, 2),
            "desviacion_std_notas": round(float(notas_actuales.std()), 2) if len(notas_actuales) > 1 else 0.0,
            "nota_min": round(float(notas_actuales.min()), 2) if len(notas_actuales) > 0 else 0.0,
            "nota_max": round(float(notas_actuales.max()), 2) if len(notas_actuales) > 0 else 0.0,
            "total_cursos_evaluados": len(notas_actuales),
            "cursos_desaprobados": int((notas_actuales < 11).sum()) if len(notas_actuales) > 0 else 0,
            "porcentaje_aprobacion": round(float((notas_actuales >= 11).sum() / len(notas_actuales) * 100), 2) if len(notas_actuales) > 0 else 0.0
        }
    
    async def _features_asistencia(self, estudiante_id: str, periodo_id: str) -> Dict:
        """Extrae features relacionadas con asistencia"""
        # Obtener periodo para calcular fechas
        response_periodo = self.supabase.table("periodos") \
            .select("fecha_inicio, fecha_fin") \
            .eq("id", periodo_id) \
            .execute()
        
        if not response_periodo.data:
            return self._features_asistencia_default()
        
        fecha_inicio = response_periodo.data[0]["fecha_inicio"]
        fecha_fin = response_periodo.data[0]["fecha_fin"]
        
        # Obtener registros de asistencia
        response = self.supabase.table("asistencia") \
            .select("*") \
            .eq("estudiante_id", estudiante_id) \
            .gte("fecha", fecha_inicio) \
            .lte("fecha", fecha_fin) \
            .execute()
        
        if not response.data:
            return self._features_asistencia_default()
        
        df_asistencia = pd.DataFrame(response.data)
        
        total_registros = len(df_asistencia)
        ausencias = len(df_asistencia[df_asistencia["estado"] == "ausente"])
        tardanzas = len(df_asistencia[df_asistencia["estado"] == "tardanza"])
        ausencias_injustificadas = len(df_asistencia[
            (df_asistencia["estado"] == "ausente") & 
            (df_asistencia["justificado"] == False)
        ])
        
        tasa_asistencia = round((total_registros - ausencias) / total_registros * 100, 2) if total_registros > 0 else 100.0
        
        return {
            "total_dias_registrados": total_registros,
            "total_ausencias": ausencias,
            "total_tardanzas": tardanzas,
            "ausencias_injustificadas": ausencias_injustificadas,
            "tasa_asistencia": tasa_asistencia,
            "porcentaje_tardanzas": round(tardanzas / total_registros * 100, 2) if total_registros > 0 else 0.0
        }
    
    def _features_asistencia_default(self) -> Dict:
        """Valores por defecto cuando no hay datos de asistencia"""
        return {
            "total_dias_registrados": 0,
            "total_ausencias": 0,
            "total_tardanzas": 0,
            "ausencias_injustificadas": 0,
            "tasa_asistencia": 100.0,
            "porcentaje_tardanzas": 0.0
        }
    
    async def _features_conducta(self, estudiante_id: str, periodo_id: str) -> Dict:
        """Extrae features relacionadas con conducta"""
        response = self.supabase.table("conducta") \
            .select("*") \
            .eq("estudiante_id", estudiante_id) \
            .eq("periodo_id", periodo_id) \
            .execute()
        
        if not response.data:
            return {
                "conducta_score": 0.75,  # Valor neutral por defecto
                "tiene_incidencias": False
            }
        
        conducta_data = response.data[0]
        
        # Mapear calificación a score numérico
        score_map = {"AD": 1.0, "A": 0.85, "B": 0.70, "C": 0.50}
        score = score_map.get(conducta_data["calificacion"], 0.75)
        
        return {
            "conducta_score": score,
            "tiene_incidencias": bool(conducta_data.get("incidencias"))
        }
    
    def _features_demograficas(self, estudiante: Dict) -> Dict:
        """Extrae features demográficas del estudiante"""
        edad = self._calcular_edad(estudiante.get("fecha_nacimiento"))
        
        return {
            "grado": estudiante["grado"],
            "edad": edad,
            "genero_m": 1 if estudiante.get("genero") == "M" else 0,
            "genero_f": 1 if estudiante.get("genero") == "F" else 0
        }
    
    def _calcular_edad(self, fecha_nacimiento: Optional[str]) -> int:
        """Calcula edad del estudiante"""
        if not fecha_nacimiento:
            return 15  # Edad promedio por defecto
        
        from datetime import datetime
        nacimiento = datetime.fromisoformat(fecha_nacimiento.replace('Z', '+00:00'))
        hoy = datetime.now()
        edad = hoy.year - nacimiento.year - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))
        return edad
    
    async def _features_historicas(self, estudiante_id: str, periodo_id: str) -> Dict:
        """Features basadas en el historial académico completo"""
        # Contar alertas previas
        response_alertas = self.supabase.table("alertas") \
            .select("tipo, estado") \
            .eq("estudiante_id", estudiante_id) \
            .execute()
        
        total_alertas_previas = len(response_alertas.data) if response_alertas.data else 0
        alertas_resueltas = len([a for a in response_alertas.data if a["estado"] == "resuelta"]) if response_alertas.data else 0
        
        # Contar intervenciones
        response_intervenciones = self.supabase.table("intervenciones") \
            .select("resultado") \
            .eq("estudiante_id", estudiante_id) \
            .execute()
        
        total_intervenciones = len(response_intervenciones.data) if response_intervenciones.data else 0
        intervenciones_exitosas = len([i for i in response_intervenciones.data if i["resultado"] == "exitosa"]) if response_intervenciones.data else 0
        
        return {
            "total_alertas_previas": total_alertas_previas,
            "alertas_resueltas": alertas_resueltas,
            "total_intervenciones": total_intervenciones,
            "intervenciones_exitosas": intervenciones_exitosas,
            "tiene_historial_riesgo": total_alertas_previas > 0
        }
    
    def preparar_features_para_modelo(self, features: Dict) -> pd.DataFrame:
        """
        Prepara las features en el formato requerido por el modelo
        
        Args:
            features: Diccionario con features extraídas
        
        Returns:
            DataFrame con features preparadas
        """
        # Lista de features que usa el modelo (debe coincidir con las del entrenamiento)
        feature_columns = [
            "promedio_actual",
            "promedio_anterior",
            "tendencia_notas",
            "desviacion_std_notas",
            "porcentaje_aprobacion",
            "tasa_asistencia",
            "total_ausencias",
            "ausencias_injustificadas",
            "conducta_score",
            "tiene_incidencias",
            "grado",
            "edad",
            "total_alertas_previas",
            "tiene_historial_riesgo"
        ]
        
        # Crear DataFrame con las features en el orden correcto
        df = pd.DataFrame([features])
        
        # Asegurar que todas las columnas existen
        for col in feature_columns:
            if col not in df.columns:
                df[col] = 0
        
        # Seleccionar solo las columnas necesarias en el orden correcto
        df = df[feature_columns]
        
        # Convertir booleanos a int
        bool_cols = ["tiene_incidencias", "tiene_historial_riesgo"]
        for col in bool_cols:
            if col in df.columns:
                df[col] = df[col].astype(int)
        
        return df
