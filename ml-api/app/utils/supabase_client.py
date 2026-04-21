"""
Cliente de Supabase para interacción con la base de datos
"""

from supabase import create_client, Client
from functools import lru_cache
import logging

from app.config import settings

logger = logging.getLogger(__name__)


@lru_cache()
def get_supabase_client() -> Client:
    """
    Retorna una instancia cacheada del cliente de Supabase
    Usa la service role key para operaciones sin restricciones RLS
    """
    try:
        client = create_client(
            supabase_url=settings.supabase_url,
            supabase_key=settings.supabase_key  # Service role key
        )
        logger.info("✅ Cliente Supabase inicializado correctamente")
        return client
    except Exception as e:
        logger.error(f"❌ Error al crear cliente Supabase: {e}")
        raise


def get_supabase_anon_client() -> Client:
    """
    Retorna cliente de Supabase con anon key (con RLS activo)
    Útil para operaciones que deben respetar permisos
    """
    try:
        client = create_client(
            supabase_url=settings.supabase_url,
            supabase_key=settings.supabase_anon_key
        )
        return client
    except Exception as e:
        logger.error(f"❌ Error al crear cliente Supabase anon: {e}")
        raise
