"""
Configuración de la aplicación FastAPI
Carga variables de entorno y configuraciones globales
"""

from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Configuración general del sistema"""
    
    # Supabase
    supabase_url: str
    supabase_key: str
    supabase_anon_key: str
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    api_workers: int = 1
    api_title: str = "Sistema de Análisis Académico - ML API"
    api_description: str = "API de Machine Learning para predicción de rendimiento académico"
    api_version: str = "1.0.0"
    
    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(',')]
    
    # ML Models
    model_path: str = "app/models/trained"
    model_retrain_schedule_days: int = 30
    
    # Logging
    log_level: str = "INFO"
    
    # Reportes
    reports_output_dir: str = "reports"
    reports_template_dir: str = "app/templates"
    
    # Email (opcional)
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    email_from: str = "Sistema Académico <noreply@sistema.com>"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Retorna una instancia cacheada de Settings"""
    return Settings()


settings = get_settings()
