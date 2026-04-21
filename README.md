# Sistema Inteligente para el Análisis del Rendimiento Académico

**Institución Educativa Pública Dos de Mayo - Chincha, 2026**

## Descripción

Sistema web inteligente que utiliza Machine Learning para analizar y predecir el rendimiento académico de estudiantes, permitiendo la identificación temprana de alumnos en riesgo y facilitando intervenciones pedagógicas oportunas.

## Objetivos

- Identificar de manera oportuna estudiantes con bajo rendimiento académico
- Integrar datos históricos (notas, asistencia, conducta) para fortalecer decisiones pedagógicas
- Optimizar el tiempo de respuesta en intervenciones educativas
- Mejorar la satisfacción de docentes y directivos en la gestión académica
- Reducir los índices de desaprobación y deserción escolar

## Arquitectura Tecnológica

### Stack Principal

- **Backend ML**: Python + FastAPI (API de Machine Learning)
- **Base de Datos**: Supabase (PostgreSQL + Auth + Realtime + Edge Functions)
- **Frontend**: React + TypeScript + TailwindCSS
- **Machine Learning**: scikit-learn, XGBoost, pandas, numpy

### Componentes del Sistema

```
sistema-academico-ia/
├── supabase/           # Esquemas BD, migraciones, Edge Functions
├── ml-api/             # API FastAPI para ML y reportes
├── frontend/           # Aplicación React
├── data-generator/     # Scripts de datos sintéticos
└── docs/               # Documentación para tesis
```

## Características Principales

### 1. Predicción de Rendimiento Académico

- Modelos ML: Random Forest, Gradient Boosting, XGBoost
- Predicción de probabilidad de desaprobación
- Predicción de riesgo de deserción
- Estimación de notas futuras

### 2. Sistema de Alertas Tempranas

- **Alertas Críticas**: >70% probabilidad de desaprobación
- **Alertas Moderadas**: 40-70% de riesgo
- **Alertas Preventivas**: Tendencia negativa detectada
- Notificaciones en tiempo real vía Supabase Realtime

### 3. Recomendaciones Pedagógicas

- Estrategias personalizadas según tipo de deficiencia
- Sugerencias basadas en datos históricos
- Historial de intervenciones y su efectividad

### 4. Dashboards Interactivos

- Panel para directivos con KPIs institucionales
- Panel para docentes con estudiantes asignados
- Gráficos de evolución temporal
- Análisis comparativos por grado, sección y curso

### 5. Reportes Automáticos

- Informes de estudiantes en riesgo (PDF)
- Análisis comparativo por periodos (Excel)
- Efectividad de intervenciones
- Métricas de modelos ML

## Requisitos del Sistema

### Backend (ml-api)

- Python 3.11 o superior
- pip o Poetry para gestión de dependencias

### Frontend

- Node.js 18 o superior
- npm o yarn

### Servicios Externos

- Cuenta en Supabase (tier gratuito disponible)
- Cuenta en Railway/Render para despliegue de FastAPI (opcional)

## Instalación

### 1. Configurar Supabase

```bash
cd supabase
# Crear proyecto en https://supabase.com
# Ejecutar migraciones desde el dashboard de Supabase
```

### 2. Configurar Backend ML

```bash
cd ml-api
pip install -r requirements.txt
cp .env.example .env
# Configurar variables de entorno
python -m uvicorn app.main:app --reload
```

### 3. Configurar Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
# Configurar variables de entorno
npm run dev
```

### 4. Generar Datos Sintéticos (para pruebas)

```bash
cd data-generator
pip install -r requirements.txt
python generate_all.py
```

## Variables de Entorno

### ml-api/.env

```
SUPABASE_URL=tu_url_supabase
SUPABASE_KEY=tu_service_role_key
PORT=8000
```

### frontend/.env.local

```
VITE_SUPABASE_URL=tu_url_supabase
VITE_SUPABASE_ANON_KEY=tu_anon_key
VITE_ML_API_URL=http://localhost:8000
```

## Uso del Sistema

### Roles de Usuario

1. **Administrador**: Acceso completo al sistema
2. **Director/Coordinador**: Vista institucional completa
3. **Docente**: Vista de estudiantes asignados
4. **Consulta**: Solo lectura

### Flujo Típico

1. Docente ingresa notas/asistencia en el sistema
2. Sistema procesa datos automáticamente
3. Modelos ML generan predicciones
4. Se crean alertas si hay estudiantes en riesgo
5. Docente recibe notificación en tiempo real
6. Sistema sugiere recomendaciones pedagógicas
7. Docente implementa intervención y registra en sistema
8. Sistema monitorea efectividad de intervención

## Modelos de Machine Learning

### Preprocesamiento

- Limpieza y normalización de datos
- Ingeniería de características (features derivadas)
- Manejo de valores faltantes
- Codificación de variables categóricas

### Entrenamiento

- División train/test: 80/20
- Validación cruzada: 5-fold
- Optimización de hiperparámetros con GridSearchCV
- Métricas: Accuracy, Precision, Recall, F1-Score, ROC-AUC

### Producción

- Modelos serializados con joblib
- API REST para inferencia
- Reentrenamiento mensual programado

## Seguridad

- Autenticación JWT vía Supabase Auth
- Row Level Security (RLS) a nivel de base de datos
- HTTPS por defecto en Supabase
- Validación de datos en frontend y backend
- Rate limiting incluido en Supabase

## Despliegue en Producción

### Supabase

- Proyecto configurado en Supabase Cloud
- Base de datos PostgreSQL gestionada
- Edge Functions desplegadas

### Backend ML

```bash
# Despliegue en Railway/Render
git push railway main
# o
render deploy
```

### Frontend

```bash
# Despliegue en Vercel
vercel deploy --prod
```

## Documentación Adicional

- [Manual de Usuario](docs/manual-usuario.md)
- [Manual Técnico](docs/manual-tecnico.md)
- [Esquema de Base de Datos](docs/database-schema.md)
- [API Documentation](http://localhost:8000/docs) (Swagger automático)
- [Análisis de Modelos ML](docs/ml-analysis.md)

## Estructura de Datos

### Entidades Principales

- **Estudiantes**: Datos personales y académicos
- **Periodos**: Bimestres/Trimestres académicos
- **Notas**: Calificaciones por curso
- **Asistencia**: Registro diario de asistencia
- **Conducta**: Evaluación de comportamiento
- **Alertas**: Sistema de alertas tempranas
- **Intervenciones**: Registro de acciones pedagógicas

## Contribución

Este es un proyecto de tesis. Para consultas o colaboración:

- Autor: Alexander
- Institución: IE Pública Dos de Mayo - Chincha
- Año: 2026

## Licencia

Este proyecto es desarrollado con fines académicos para mejorar la calidad educativa en instituciones públicas del Perú.

## Agradecimientos

- IE Pública Dos de Mayo - Chincha
- Docentes y directivos participantes
- Estudiantes del piloto

## Roadmap

- [x] Diseño de arquitectura
- [x] Esquema de base de datos
- [ ] Implementación de modelos ML
- [ ] Desarrollo de API FastAPI
- [ ] Desarrollo de frontend React
- [ ] Integración completa
- [ ] Pruebas con datos reales
- [ ] Despliegue en producción
- [ ] Capacitación a docentes
- [ ] Documentación final de tesis
