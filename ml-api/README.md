# ML API - Sistema de Análisis Académico

API de Machine Learning para predicción de rendimiento académico y generación de alertas tempranas.

## Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus credenciales de Supabase
```

### 3. Ejecutar servidor de desarrollo

```bash
python main.py
```

O con uvicorn directamente:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Documentación de la API

Una vez iniciado el servidor, accede a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Endpoints Principales

### Predicciones ML

- `POST /api/prediccion/individual` - Predicción individual
- `POST /api/prediccion/batch` - Predicciones en lote
- `GET /api/prediccion/metricas-modelo` - Métricas de modelos
- `GET /api/prediccion/historial/{estudiante_id}` - Historial de predicciones

### Recomendaciones

- `POST /api/recomendaciones/generar` - Generar recomendaciones
- `GET /api/recomendaciones/estrategias` - Listar estrategias
- `GET /api/recomendaciones/por-alerta/{alerta_id}` - Recomendaciones de una alerta

### Reportes

- `POST /api/reportes/estudiantes-riesgo` - Reporte de estudiantes en riesgo
- `POST /api/reportes/analisis-periodo` - Análisis comparativo
- `POST /api/reportes/efectividad-intervenciones` - Efectividad de intervenciones
- `POST /api/reportes/resumen-institucional` - Resumen ejecutivo

## Estructura del Proyecto

```
ml-api/
├── app/
│   ├── api/              # Endpoints REST
│   ├── ml/               # Modelos de ML
│   ├── models/           # Modelos entrenados (.pkl)
│   ├── schemas/          # Pydantic schemas
│   └── utils/            # Utilidades
├── notebooks/            # Jupyter notebooks
├── requirements.txt      # Dependencias
└── main.py              # Punto de entrada
```

## Desarrollo

### Testing

```bash
pytest
```

### Linting

```bash
flake8 app/
black app/
```

## Despliegue

### Railway

```bash
railway init
railway up
```

### Render

Conecta tu repositorio Git y configura:
- Build Command: `pip install -r requirements.txt`
- Start Command: `python main.py`

## Licencia

Proyecto académico - IE Pública Dos de Mayo
