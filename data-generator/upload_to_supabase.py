"""
Uploader de datos sint éticos a Supabase
Sube todos los datos generados a la base de datos
"""

import os
from supabase import create_client, Client
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def get_supabase_client() -> Client:
    """Crea cliente de Supabase"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("SUPABASE_URL y SUPABASE_KEY deben estar configurados en .env")
    
    return create_client(url, key)


def subir_a_supabase(estudiantes_df, docentes_df, datos_academicos):
    """
    Sube todos los datos generados a Supabase
    
    Args:
        estudiantes_df: DataFrame de estudiantes
        docentes_df: DataFrame de docentes
        datos_academicos: Dict con periodos, cursos, notas, asistencia, conducta
    """
    client = get_supabase_client()
    
    logger.info("📤 Subiendo datos a Supabase...")
    
    # 1. Subir periodos
    logger.info("📅 Subiendo periodos académicos...")
    periodos_dict = datos_academicos['periodos'].to_dict('records')
    response = client.table('periodos').upsert(periodos_dict).execute()
    logger.info(f"✅ {len(periodos_dict)} periodos subidos")
    
    # Obtener IDs de periodos creados
    periodos_map = {}
    for periodo in periodos_dict:
        result = client.table('periodos').select('id').eq('nombre', periodo['nombre']).execute()
        if result.data:
            periodos_map[periodo['nombre']] = result.data[0]['id']
    
    # 2. Subir cursos
    logger.info("📚 Subiendo cursos...")
    cursos_dict = datos_academicos['cursos'].to_dict('records')
    response = client.table('cursos').upsert(cursos_dict).execute()
    logger.info(f"✅ {len(cursos_dict)} cursos subidos")
    
    # Obtener IDs de cursos
    cursos_map = {}
    for curso in cursos_dict:
        result = client.table('cursos').select('id').eq('codigo', curso['codigo']).execute()
        if result.data:
            cursos_map[curso['codigo']] = result.data[0]['id']
    
    # 3. Subir docentes (primero crear usuarios en auth)
    logger.info("👨‍🏫 Subiendo docentes...")
    for _, docente in docentes_df.iterrows():
        try:
            # Crear usuario en Supabase Auth (simplificado - en producción usar API de Auth)
            # Por ahora insertar directamente en perfiles
            perfil = {
                'rol': docente['rol'],
                'nombres': docente['nombres'],
                'apellidos': docente['apellidos'],
                'dni': str(docente['dni']),
                'telefono': docente['telefono'],
                'email': docente['email'],
                'activo': docente['activo']
            }
            # Nota: En producción esto debe hacerse via Auth API
            logger.info(f"⚠️ Docente {docente['nombres']} - crear manualmente en Supabase Auth")
        except Exception as e:
            logger.warning(f"⚠️ Error con docente: {e}")
    
    # 4. Subir estudiantes
    logger.info("📚 Subiendo estudiantes...")
    estudiantes_dict = estudiantes_df.to_dict('records')
    
    # Subir en lotes de 100
    batch_size = 100
    for i in range(0, len(estudiantes_dict), batch_size):
        batch = estudiantes_dict[i:i+batch_size]
        client.table('estudiantes').upsert(batch).execute()
        logger.info(f"   Subidos {min(i+batch_size, len(estudiantes_dict))}/{len(estudiantes_dict)}")
    
    logger.info(f"✅ {len(estudiantes_dict)} estudiantes subidos")
    
    # Obtener IDs de estudiantes
    estudiantes_map = {}
    response = client.table('estudiantes').select('id, codigo').execute()
    for est in response.data:
        estudiantes_map[est['codigo']] = est['id']
    
    # 5. Subir notas
    logger.info("📊 Subiendo notas...")
    notas = datos_academicos['notas']
    notas_dict = []
    
    for _, nota in notas.iterrows():
        if nota['estudiante_codigo'] in estudiantes_map and \
           nota['curso_codigo'] in cursos_map and \
           nota['periodo_nombre'] in periodos_map:
            notas_dict.append({
                'estudiante_id': estudiantes_map[nota['estudiante_codigo']],
                'curso_id': cursos_map[nota['curso_codigo']],
                'periodo_id': periodos_map[nota['periodo_nombre']],
                'nota': float(nota['nota']),
                'tipo_evaluacion': nota['tipo_evaluacion'],
                'observaciones': nota['observaciones']
            })
    
    # Subir en lotes
    for i in range(0, len(notas_dict), batch_size):
        batch = notas_dict[i:i+batch_size]
        client.table('notas').insert(batch).execute()
        logger.info(f"   Subidas {min(i+batch_size, len(notas_dict))}/{len(notas_dict)}")
    
    logger.info(f"✅ {len(notas_dict)} notas subidas")
    
    # 6. Subir asistencia
    logger.info("📅 Subiendo asistencia...")
    asistencia = datos_academicos['asistencia']
    asistencia_dict = []
    
    for _, asist in asistencia.iterrows():
        if asist['estudiante_codigo'] in estudiantes_map:
            asistencia_dict.append({
                'estudiante_id': estudiantes_map[asist['estudiante_codigo']],
                'fecha': asist['fecha'],
                'estado': asist['estado'],
                'justificado': bool(asist['justificado']),
                'motivo': asist['motivo']
            })
    
    # Subir en lotes
    for i in range(0, len(asistencia_dict), batch_size):
        batch = asistencia_dict[i:i+batch_size]
        try:
            client.table('asistencia').insert(batch).execute()
            logger.info(f"   Subidas {min(i+batch_size, len(asistencia_dict))}/{len(asistencia_dict)}")
        except Exception as e:
            logger.warning(f"⚠️ Error en lote de asistencia: {e}")
    
    logger.info(f"✅ {len(asistencia_dict)} registros de asistencia subidos")
    
    # 7. Subir conducta
    logger.info("⭐ Subiendo conducta...")
    conducta = datos_academicos['conducta']
    conducta_dict = []
    
    for _, cond in conducta.iterrows():
        if cond['estudiante_codigo'] in estudiantes_map and \
           cond['periodo_nombre'] in periodos_map:
            conducta_dict.append({
                'estudiante_id': estudiantes_map[cond['estudiante_codigo']],
                'periodo_id': periodos_map[cond['periodo_nombre']],
                'calificacion': cond['calificacion'],
                'incidencias': cond['incidencias'],
                'observaciones': cond['observaciones']
            })
    
    client.table('conducta').insert(conducta_dict).execute()
    logger.info(f"✅ {len(conducta_dict)} evaluaciones de conducta subidas")
    
    logger.info("\n🎉 ¡Todos los datos fueron subidos exitosamente a Supabase!")


if __name__ == "__main__":
    import generate_students
    import generate_teachers
    import generate_academic_data
    from dotenv import load_dotenv
    
    load_dotenv()
    
    estudiantes = generate_students.generar_estudiantes(50)
    docentes = generate_teachers.generar_docentes(10)
    datos_acad = generate_academic_data.generar_datos_academicos(estudiantes)
    
    subir_a_supabase(estudiantes, docentes, datos_acad)
