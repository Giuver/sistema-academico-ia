# 🎓 Sistema Inteligente para el Análisis del Rendimiento Académico

![Estado](https://img.shields.io/badge/estado-en%20desarrollo-yellow)
![Versión](https://img.shields.io/badge/versión-1.0.0-blue)
![Licencia](https://img.shields.io/badge/licencia-MIT-green)

Sistema de análisis predictivo del rendimiento académico usando Machine Learning para la IE Pública Dos de Mayo - Chincha, 2026.

## 🌟 Características Principales

- 🤖 **Predicción con IA**: Modelos de Machine Learning para predecir riesgo de desaprobación y deserción
- 📊 **Dashboard Interactivo**: Visualización en tiempo real del rendimiento académico
- ⚠️ **Sistema de Alertas**: Detección automática de estudiantes en riesgo
- 📈 **Análisis Histórico**: Seguimiento de tendencias y patrones
- 💡 **Recomendaciones Inteligentes**: Sugerencias pedagógicas personalizadas
- 🔐 **Seguridad RLS**: Control de acceso por roles con Row Level Security

## 🚀 Demo en Vivo

- **Frontend**: [https://tu-app.vercel.app](https://tu-app.vercel.app) _(próximamente)_
- **API Docs**: [https://tu-backend.railway.app/docs](https://tu-backend.railway.app/docs) _(próximamente)_

## 🛠️ Tecnologías

### Frontend
- React 18 + TypeScript
- TailwindCSS
- React Query
- Recharts
- Vite

### Backend
- FastAPI
- Python 3.13
- scikit-learn
- XGBoost
- PostgreSQL (Supabase)

### Machine Learning
- Random Forest Classifier
- XGBoost
- 22 características extraídas
- Validación cruzada

## 📋 Requisitos Previos

- Node.js 22+
- Python 3.13+
- Cuenta en Supabase
- Git

## ⚙️ Instalación Local

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/sistema-academico-ia.git
cd sistema-academico-ia
```

### 2. Configurar Base de Datos

1. Crea un proyecto en [Supabase](https://supabase.com)
2. Ejecuta las migraciones SQL en `supabase/migrations/`
3. Copia tus credenciales

### 3. Configurar Backend

```bash
cd ml-api
pip install -r requirements.txt
cp .env.example .env
# Edita .env con tus credenciales de Supabase
python -m uvicorn main:app --reload
```

### 4. Configurar Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
# Edita .env.local con tus credenciales
npm run dev
```

### 5. Acceder al Sistema

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Documentación API: http://localhost:8000/docs

## 📚 Documentación

- [Guía de Instalación Completa](INSTALACION_COMPLETA.md)
- [Configuración de Supabase](CONFIGURAR_SUPABASE.md)
- [Despliegue en Vercel](DESPLIEGUE_VERCEL.md)
- [Informe Técnico Completo](INFORME_ESTADO_ACTUAL.md)
- [Documentación del Proyecto](PROYECTO_COMPLETO.md)

## 🎯 Funcionalidades

### ✅ Implementadas
- [x] Autenticación y autorización por roles
- [x] Gestión de estudiantes (agregar, ver)
- [x] Dashboard con métricas clave
- [x] Sistema de alertas en tiempo real
- [x] Predicciones ML (backend)
- [x] Generación de reportes
- [x] Visualizaciones interactivas

### 🚧 En Desarrollo
- [ ] Gestión de notas
- [ ] Gestión de asistencia
- [ ] UI de predicciones ML
- [ ] Edición de estudiantes
- [ ] Sistema de intervenciones

## 📊 Arquitectura

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend   │────▶│  Supabase   │
│   (React)   │     │  (FastAPI)  │     │ (PostgreSQL)│
│   Vercel    │     │   Railway   │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
```

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add: Amazing Feature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es parte de una tesis académica para la IE Pública Dos de Mayo - Chincha, 2026.

## 👤 Autor

**Alexander** - Tesis de grado  
IE Pública Dos de Mayo - Chincha

## 🙏 Agradecimientos

- IE Pública Dos de Mayo
- Universidad [Nombre]
- Comunidad educativa de Chincha

---

**⭐ Si este proyecto te ayuda, considera darle una estrella en GitHub**
