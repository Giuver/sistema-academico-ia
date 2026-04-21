"""
Configuración de logging para la aplicación
"""

import logging
import sys
from datetime import datetime
from pythonjsonlogger import jsonlogger
from app.config import settings


def setup_logging():
    """Configura el sistema de logging de la aplicación"""
    
    # Crear logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level)
    
    # Limpiar handlers existentes
    root_logger.handlers.clear()
    
    # Handler para consola con formato legible
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.log_level)
    
    # Formato para desarrollo
    console_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # Handler para archivo con formato JSON (producción)
    try:
        file_handler = logging.FileHandler(
            f'logs/app_{datetime.now().strftime("%Y%m%d")}.log'
        )
        file_handler.setLevel(logging.INFO)
        
        # Formato JSON para parsing fácil
        json_formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s'
        )
        file_handler.setFormatter(json_formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        root_logger.warning(f"No se pudo crear archivo de log: {e}")
    
    # Silenciar logs verbosos de librerías
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    root_logger.info("✅ Sistema de logging configurado correctamente")
