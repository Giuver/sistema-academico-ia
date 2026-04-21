"""
API de Predicciones ML
Endpoints para realizar predicciones de rendimiento académico
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
import logging

from app.schemas.prediccion import (
    PrediccionRequest,
    PrediccionResponse,
    PrediccionBatchRequest,
    PrediccionBatchResponse,
    TipoPrediccion,
    MetricasModeloResponse,
    EntrenarModeloRequest
)
from app.ml.predict import predictor

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/individual", response_model=PrediccionResponse)
async def predecir_individual(request: PrediccionRequest):
    """
    Realiza una predicción individual para un estudiante
    
    **Tipos de predicción disponibles:**
    - `desaprobacion`: Probabilidad de desaprobar el periodo
    - `desercion`: Riesgo de deserción escolar
    - `nota_estimada`: Estimación de nota promedio futura
    
    **Nivel de riesgo:**
    - `bajo`: < 40% probabilidad
    - `medio`: 40-70% probabilidad
    - `alto`: > 70% probabilidad
    """
    try:
        logger.info(f"📊 Solicitud de predicción: {request.tipo_prediccion} para estudiante {request.estudiante_id}")
        
        # Ejecutar predicción según el tipo
        if request.tipo_prediccion == TipoPrediccion.DESAPROBACION:
            resultado = await predictor.predecir_desaprobacion(
                str(request.estudiante_id),
                str(request.periodo_id) if request.periodo_id else None
            )
        elif request.tipo_prediccion == TipoPrediccion.DESERCION:
            resultado = await predictor.predecir_desercion(
                str(request.estudiante_id),
                str(request.periodo_id) if request.periodo_id else None
            )
        elif request.tipo_prediccion == TipoPrediccion.NOTA_ESTIMADA:
            resultado = await predictor.estimar_nota_futura(
                str(request.estudiante_id),
                str(request.periodo_id) if request.periodo_id else None
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de predicción no soportado: {request.tipo_prediccion}"
            )
        
        return PrediccionResponse(**resultado)
        
    except ValueError as e:
        logger.error(f"❌ Error de validación: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Error en predicción: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error al realizar predicción: {str(e)}"
        )


@router.post("/batch", response_model=PrediccionBatchResponse)
async def predecir_batch(request: PrediccionBatchRequest):
    """
    Realiza predicciones en lote para múltiples estudiantes
    
    Útil para generar predicciones masivas al inicio de un periodo
    o para actualizar el estado de riesgo de todos los estudiantes.
    """
    try:
        logger.info(f"📊 Predicción en lote: {len(request.estudiantes_ids)} estudiantes")
        
        predicciones = []
        errores = []
        
        for estudiante_id in request.estudiantes_ids:
            try:
                # Ejecutar predicción según tipo
                if request.tipo_prediccion == TipoPrediccion.DESAPROBACION:
                    resultado = await predictor.predecir_desaprobacion(
                        str(estudiante_id),
                        str(request.periodo_id) if request.periodo_id else None
                    )
                elif request.tipo_prediccion == TipoPrediccion.DESERCION:
                    resultado = await predictor.predecir_desercion(
                        str(estudiante_id),
                        str(request.periodo_id) if request.periodo_id else None
                    )
                elif request.tipo_prediccion == TipoPrediccion.NOTA_ESTIMADA:
                    resultado = await predictor.estimar_nota_futura(
                        str(estudiante_id),
                        str(request.periodo_id) if request.periodo_id else None
                    )
                
                predicciones.append(PrediccionResponse(**resultado))
                
            except Exception as e:
                logger.warning(f"⚠️ Error en predicción de {estudiante_id}: {e}")
                errores.append({
                    "estudiante_id": str(estudiante_id),
                    "error": str(e)
                })
        
        return PrediccionBatchResponse(
            total_predicciones=len(request.estudiantes_ids),
            exitosas=len(predicciones),
            fallidas=len(errores),
            predicciones=predicciones,
            errores=errores if errores else None
        )
        
    except Exception as e:
        logger.error(f"❌ Error en predicción batch: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error en predicción batch: {str(e)}"
        )


@router.get("/metricas-modelo", response_model=List[MetricasModeloResponse])
async def obtener_metricas_modelos():
    """
    Obtiene las métricas de evaluación de los modelos ML activos
    
    Incluye:
    - Accuracy, Precision, Recall, F1-Score
    - ROC-AUC (para clasificadores)
    - Fecha de último entrenamiento
    - Tamaño del dataset usado
    """
    try:
        from app.utils.supabase_client import get_supabase_client
        
        supabase = get_supabase_client()
        response = supabase.table("metricas_modelo") \
            .select("*") \
            .order("fecha_entrenamiento", desc=True) \
            .limit(10) \
            .execute()
        
        if not response.data:
            return []
        
        return [MetricasModeloResponse(**item) for item in response.data]
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo métricas: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo métricas de modelos: {str(e)}"
        )


@router.post("/entrenar")
async def entrenar_modelo(
    request: EntrenarModeloRequest,
    background_tasks: BackgroundTasks
):
    """
    Inicia el proceso de entrenamiento de un nuevo modelo
    
    **Nota:** El entrenamiento se ejecuta en segundo plano y puede tardar varios minutos.
    
    **Tipos de modelo disponibles:**
    - `random_forest`: Random Forest Classifier
    - `xgboost`: XGBoost Classifier
    - `gradient_boosting`: Gradient Boosting Classifier
    """
    try:
        logger.info(f"🎓 Iniciando entrenamiento de modelo: {request.tipo_modelo}")
        
        # TODO: Implementar entrenamiento real cuando haya datos
        # Por ahora retornamos respuesta de éxito simulada
        
        return {
            "message": "Entrenamiento iniciado en segundo plano",
            "tipo_modelo": request.tipo_modelo,
            "status": "in_progress",
            "nota": "Esta funcionalidad estará disponible cuando existan datos históricos suficientes"
        }
        
    except Exception as e:
        logger.error(f"❌ Error iniciando entrenamiento: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al iniciar entrenamiento: {str(e)}"
        )


@router.get("/historial/{estudiante_id}")
async def obtener_historial_predicciones(estudiante_id: str, limit: int = 10):
    """
    Obtiene el historial de predicciones de un estudiante
    
    Útil para ver la evolución del riesgo académico a lo largo del tiempo
    """
    try:
        from app.utils.supabase_client import get_supabase_client
        
        supabase = get_supabase_client()
        response = supabase.table("predicciones_ml") \
            .select("*") \
            .eq("estudiante_id", estudiante_id) \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()
        
        return {
            "estudiante_id": estudiante_id,
            "total_predicciones": len(response.data) if response.data else 0,
            "predicciones": response.data or []
        }
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo historial: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo historial de predicciones: {str(e)}"
        )
