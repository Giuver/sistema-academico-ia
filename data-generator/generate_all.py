"""
Script principal para generar todos los datos sintéticos
Genera estudiantes, docentes, notas, asistencia, conducta y alertas
"""

import os
import sys
from dotenv import load_dotenv
import logging

# Importar generadores
from generate_students import generar_estudiantes
from generate_teachers import generar_docentes
from generate_academic_data import generar_datos_academicos
from upload_to_supabase import subir_a_supabase

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Ejecuta todo el proceso de generación de datos"""
    
    logger.info("=" * 70)
    logger.info("🚀 INICIO DE GENERACIÓN DE DATOS SINTÉTICOS")
    logger.info("=" * 70)
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Verificar configuración
    if not os.getenv("SUPABASE_URL"):
        logger.error("❌ Variables de entorno no configuradas")
        logger.info("💡 Copia .env.example a .env y configura tus credenciales")
        sys.exit(1)
    
    try:
        # 1. Generar estudiantes
        logger.info("\n📚 Paso 1: Generando estudiantes...")
        estudiantes_df = generar_estudiantes()
        logger.info(f"✅ {len(estudiantes_df)} estudiantes generados")
        
        # 2. Generar docentes
        logger.info("\n👨‍🏫 Paso 2: Generando docentes...")
        docentes_df = generar_docentes()
        logger.info(f"✅ {len(docentes_df)} docentes generados")
        
        # 3. Generar datos académicos (notas, asistencia, conducta)
        logger.info("\n📊 Paso 3: Generando datos académicos...")
        datos_academicos = generar_datos_academicos(estudiantes_df)
        logger.info(f"✅ Datos académicos generados")
        logger.info(f"   - Notas: {len(datos_academicos['notas'])}")
        logger.info(f"   - Asistencia: {len(datos_academicos['asistencia'])}")
        logger.info(f"   - Conducta: {len(datos_academicos['conducta'])}")
        
        # 4. Subir a Supabase
        logger.info("\n☁️  Paso 4: Subiendo datos a Supabase...")
        subir_a_supabase(
            estudiantes_df,
            docentes_df,
            datos_academicos
        )
        
        logger.info("\n" + "=" * 70)
        logger.info("✅ PROCESO COMPLETADO EXITOSAMENTE")
        logger.info("=" * 70)
        logger.info("\n📊 Resumen:")
        logger.info(f"   - Estudiantes: {len(estudiantes_df)}")
        logger.info(f"   - Docentes: {len(docentes_df)}")
        logger.info(f"   - Notas: {len(datos_academicos['notas'])}")
        logger.info(f"   - Registros de asistencia: {len(datos_academicos['asistencia'])}")
        logger.info(f"   - Evaluaciones de conducta: {len(datos_academicos['conducta'])}")
        logger.info("\n🎉 Los datos están listos para usar en el sistema")
        
    except Exception as e:
        logger.error(f"\n❌ ERROR: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
