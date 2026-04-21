"""
Script de entrenamiento de modelos ML
Entrena Random Forest y XGBoost con datos históricos
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, classification_report, confusion_matrix
import xgboost as xgb
import joblib
from datetime import datetime
import os
import logging

from app.config import settings
from app.utils.supabase_client import get_supabase_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelTrainer:
    """Clase para entrenar modelos de Machine Learning"""
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self.models = {}
        self.metrics = {}
    
    def cargar_datos(self):
        """Carga datos desde Supabase para entrenamiento"""
        logger.info("📊 Cargando datos desde Supabase...")
        
        # Obtener estudiantes con historial completo
        response_estudiantes = self.supabase.table("estudiantes").select("*").execute()
        estudiantes_df = pd.DataFrame(response_estudiantes.data)
        
        # Obtener notas
        response_notas = self.supabase.table("notas").select("*").execute()
        notas_df = pd.DataFrame(response_notas.data)
        
        # Obtener asistencia
        response_asist = self.supabase.table("asistencia").select("*").execute()
        asist_df = pd.DataFrame(response_asist.data)
        
        # Obtener conducta
        response_cond = self.supabase.table("conducta").select("*").execute()
        conducta_df = pd.DataFrame(response_cond.data)
        
        logger.info(f"✅ Datos cargados: {len(estudiantes_df)} estudiantes")
        
        return estudiantes_df, notas_df, asist_df, conducta_df
    
    def preparar_features(self, estudiantes_df, notas_df, asist_df, conducta_df):
        """Prepara features para entrenamiento"""
        logger.info("🔧 Preparando features...")
        
        features_list = []
        
        for _, estudiante in estudiantes_df.iterrows():
            est_id = estudiante['id']
            
            # Notas del estudiante
            notas_est = notas_df[notas_df['estudiante_id'] == est_id]
            promedio = notas_est['nota'].mean() if len(notas_est) > 0 else 13
            std_notas = notas_est['nota'].std() if len(notas_est) > 1 else 0
            min_nota = notas_est['nota'].min() if len(notas_est) > 0 else 13
            max_nota = notas_est['nota'].max() if len(notas_est) > 0 else 13
            cursos_desaprobados = len(notas_est[notas_est['nota'] < 11])
            porcentaje_aprobacion = len(notas_est[notas_est['nota'] >= 11]) / len(notas_est) * 100 if len(notas_est) > 0 else 100
            
            # Asistencia
            asist_est = asist_df[asist_df['estudiante_id'] == est_id]
            total_dias = len(asist_est)
            ausencias = len(asist_est[asist_est['estado'] == 'ausente'])
            tardanzas = len(asist_est[asist_est['estado'] == 'tardanza'])
            tasa_asistencia = (total_dias - ausencias) / total_dias * 100 if total_dias > 0 else 100
            
            # Conducta
            cond_est = conducta_df[conducta_df['estudiante_id'] == est_id]
            if len(cond_est) > 0:
                calif_cond = cond_est.iloc[-1]['calificacion']
                score_map = {'AD': 1.0, 'A': 0.85, 'B': 0.70, 'C': 0.50}
                conducta_score = score_map.get(calif_cond, 0.75)
                tiene_incidencias = 1 if pd.notna(cond_est.iloc[-1].get('incidencias')) else 0
            else:
                conducta_score = 0.75
                tiene_incidencias = 0
            
            # Edad
            if pd.notna(estudiante.get('fecha_nacimiento')):
                from datetime import datetime
                nacimiento = pd.to_datetime(estudiante['fecha_nacimiento'])
                edad = (datetime.now() - nacimiento).days // 365
            else:
                edad = 12 + estudiante['grado']
            
            # Target: 1 si está en riesgo (promedio < 13), 0 si no
            en_riesgo = 1 if promedio < 13 else 0
            
            features = {
                'promedio_actual': promedio,
                'desviacion_std_notas': std_notas,
                'nota_min': min_nota,
                'nota_max': max_nota,
                'cursos_desaprobados': cursos_desaprobados,
                'porcentaje_aprobacion': porcentaje_aprobacion,
                'total_ausencias': ausencias,
                'total_tardanzas': tardanzas,
                'tasa_asistencia': tasa_asistencia,
                'conducta_score': conducta_score,
                'tiene_incidencias': tiene_incidencias,
                'grado': estudiante['grado'],
                'edad': edad,
                'genero_m': 1 if estudiante.get('genero') == 'M' else 0,
                'target': en_riesgo
            }
            
            features_list.append(features)
        
        df = pd.DataFrame(features_list)
        logger.info(f"✅ Features preparadas: {len(df)} muestras, {len(df.columns)-1} features")
        
        return df
    
    def entrenar_random_forest(self, X_train, X_test, y_train, y_test):
        """Entrena Random Forest Classifier"""
        logger.info("🌲 Entrenando Random Forest...")
        
        # Definir espacio de búsqueda
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [5, 10, 15, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }
        
        rf = RandomForestClassifier(random_state=42)
        
        # Grid search
        grid_search = GridSearchCV(rf, param_grid, cv=5, scoring='f1', n_jobs=-1, verbose=1)
        grid_search.fit(X_train, y_train)
        
        best_rf = grid_search.best_estimator_
        
        # Predicciones
        y_pred = best_rf.predict(X_test)
        y_pred_proba = best_rf.predict_proba(X_test)[:, 1]
        
        # Métricas
        metrics = {
            'modelo_nombre': 'RandomForestClassifier',
            'version': '1.0.0',
            'tipo_modelo': 'clasificacion',
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, zero_division=0),
            'recall': recall_score(y_test, y_pred, zero_division=0),
            'f1_score': f1_score(y_test, y_pred, zero_division=0),
            'roc_auc': roc_auc_score(y_test, y_pred_proba),
            'parametros': grid_search.best_params_,
            'dataset_size': len(X_train) + len(X_test),
            'fecha_entrenamiento': datetime.now().isoformat(),
            'activo': True
        }
        
        logger.info(f"✅ Random Forest - Accuracy: {metrics['accuracy']:.4f}, F1: {metrics['f1_score']:.4f}")
        
        # Guardar modelo
        model_path = os.path.join(settings.model_path, 'desaprobacion_classifier.pkl')
        joblib.dump(best_rf, model_path)
        logger.info(f"💾 Modelo guardado en: {model_path}")
        
        self.models['random_forest'] = best_rf
        self.metrics['random_forest'] = metrics
        
        return best_rf, metrics
    
    def entrenar_xgboost(self, X_train, X_test, y_train, y_test):
        """Entrena XGBoost Classifier"""
        logger.info("⚡ Entrenando XGBoost...")
        
        # Parámetros
        params = {
            'max_depth': 6,
            'learning_rate': 0.1,
            'n_estimators': 100,
            'objective': 'binary:logistic',
            'eval_metric': 'logloss',
            'random_state': 42
        }
        
        xgb_model = xgb.XGBClassifier(**params)
        xgb_model.fit(X_train, y_train)
        
        # Predicciones
        y_pred = xgb_model.predict(X_test)
        y_pred_proba = xgb_model.predict_proba(X_test)[:, 1]
        
        # Métricas
        metrics = {
            'modelo_nombre': 'XGBoostClassifier',
            'version': '1.0.0',
            'tipo_modelo': 'clasificacion',
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, zero_division=0),
            'recall': recall_score(y_test, y_pred, zero_division=0),
            'f1_score': f1_score(y_test, y_pred, zero_division=0),
            'roc_auc': roc_auc_score(y_test, y_pred_proba),
            'parametros': params,
            'dataset_size': len(X_train) + len(X_test),
            'fecha_entrenamiento': datetime.now().isoformat(),
            'activo': True
        }
        
        logger.info(f"✅ XGBoost - Accuracy: {metrics['accuracy']:.4f}, F1: {metrics['f1_score']:.4f}")
        
        # Guardar modelo
        model_path = os.path.join(settings.model_path, 'desercion_classifier.pkl')
        joblib.dump(xgb_model, model_path)
        logger.info(f"💾 Modelo guardado en: {model_path}")
        
        self.models['xgboost'] = xgb_model
        self.metrics['xgboost'] = metrics
        
        return xgb_model, metrics
    
    def guardar_metricas_en_bd(self):
        """Guarda métricas en Supabase"""
        logger.info("💾 Guardando métricas en base de datos...")
        
        for nombre, metrics in self.metrics.items():
            self.supabase.table('metricas_modelo').insert(metrics).execute()
        
        logger.info("✅ Métricas guardadas")
    
    def entrenar_todos(self):
        """Entrena todos los modelos"""
        logger.info("=" * 70)
        logger.info("🎓 INICIO DE ENTRENAMIENTO DE MODELOS ML")
        logger.info("=" * 70)
        
        # Cargar datos
        est_df, notas_df, asist_df, cond_df = self.cargar_datos()
        
        # Preparar features
        df = self.preparar_features(est_df, notas_df, asist_df, cond_df)
        
        # Separar features y target
        X = df.drop('target', axis=1)
        y = df['target']
        
        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        logger.info(f"📊 Train: {len(X_train)} muestras, Test: {len(X_test)} muestras")
        logger.info(f"📊 Distribución de clases - En riesgo: {y.sum()}, Sin riesgo: {len(y) - y.sum()}")
        
        # Entrenar modelos
        self.entrenar_random_forest(X_train, X_test, y_train, y_test)
        self.entrenar_xgboost(X_train, X_test, y_train, y_test)
        
        # Guardar métricas
        self.guardar_metricas_en_bd()
        
        logger.info("=" * 70)
        logger.info("✅ ENTRENAMIENTO COMPLETADO")
        logger.info("=" * 70)
        
        return self.models, self.metrics


if __name__ == "__main__":
    trainer = ModelTrainer()
    models, metrics = trainer.entrenar_todos()
    
    print("\n📊 RESUMEN DE MÉTRICAS:")
    for nombre, metricas in metrics.items():
        print(f"\n{nombre.upper()}:")
        print(f"  Accuracy:  {metricas['accuracy']:.4f}")
        print(f"  Precision: {metricas['precision']:.4f}")
        print(f"  Recall:    {metricas['recall']:.4f}")
        print(f"  F1-Score:  {metricas['f1_score']:.4f}")
        print(f"  ROC-AUC:   {metricas['roc_auc']:.4f}")
