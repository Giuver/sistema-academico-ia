# 🚀 GUÍA DE DESPLIEGUE EN VERCEL

## Sistema de Análisis Académico - IE Dos de Mayo

Esta guía te ayudará a desplegar el sistema completo en la nube.

---

## 📋 ARQUITECTURA DE DESPLIEGUE

```
┌─────────────────────────────────────────────────────┐
│                    USUARIO                          │
└─────────────────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────┐
│              FRONTEND (React)                       │
│              🌐 Vercel                              │
│              https://tu-app.vercel.app              │
└─────────────────────────────────────────────────────┘
                         │
                    ┌────┴────┐
                    ↓         ↓
┌──────────────────────┐  ┌──────────────────────┐
│   BASE DE DATOS      │  │   BACKEND ML API     │
│   🗄️ Supabase       │  │   🐍 Railway/Render  │
│   (Ya configurado)   │  │   FastAPI            │
└──────────────────────┘  └──────────────────────┘
```

---

## 🎯 PARTE 1: DESPLEGAR FRONTEND EN VERCEL

### Paso 1: Crear Cuenta en Vercel

1. Ve a **https://vercel.com**
2. Haz clic en **"Sign Up"**
3. Usa tu cuenta de **GitHub** (recomendado) o email
4. Confirma tu email si es necesario

### Paso 2: Preparar el Proyecto

Antes de subir, necesitas crear un repositorio en GitHub:

#### Opción A: Usando GitHub Desktop (Más Fácil)

1. Descarga **GitHub Desktop**: https://desktop.github.com
2. Instala y abre GitHub Desktop
3. Haz clic en **"Add"** > **"Add existing repository"**
4. Selecciona la carpeta: `C:\Users\Lenovo\OneDrive\Escritorio\Tesis-Alexander`
5. Si dice que no es un repositorio, haz clic en **"Create a repository"**
6. Completa:
   - **Name**: `sistema-academico-ia`
   - **Description**: "Sistema Inteligente para Análisis Académico"
   - **Git ignore**: `Node` y `Python`
7. Haz clic en **"Create Repository"**
8. Haz clic en **"Publish repository"**
9. Desmarca **"Keep this code private"** (o déjalo marcado si prefieres privado)
10. Haz clic en **"Publish Repository"**

#### Opción B: Usando Git en Terminal

```powershell
# Ir a la carpeta del proyecto
cd C:\Users\Lenovo\OneDrive\Escritorio\Tesis-Alexander

# Inicializar git (si no está inicializado)
git init

# Crear archivo .gitignore
echo "node_modules/
dist/
.env
.env.local
*.log
.DS_Store
__pycache__/
*.pyc
ml-api/app/models/trained/*.pkl
ml-api/reports/*.pdf
ml-api/logs/*.log" > .gitignore

# Agregar todos los archivos
git add .

# Hacer commit
git commit -m "Initial commit: Sistema de Análisis Académico"

# Crear repositorio en GitHub (ve a github.com/new)
# Luego conecta y sube:
git remote add origin https://github.com/TU-USUARIO/sistema-academico-ia.git
git branch -M main
git push -u origin main
```

### Paso 3: Importar en Vercel

1. En **Vercel Dashboard**, haz clic en **"Add New..."** > **"Project"**
2. Haz clic en **"Import Git Repository"**
3. Autoriza acceso a GitHub si te lo pide
4. Busca tu repositorio **"sistema-academico-ia"**
5. Haz clic en **"Import"**

### Paso 4: Configurar el Proyecto en Vercel

En la página de configuración:

#### Framework Preset
- Selecciona: **"Vite"**

#### Root Directory
- Cambia a: **"frontend"** (muy importante)
- Haz clic en **"Edit"** y escribe `frontend`

#### Build and Output Settings
- Build Command: `npm run build` (ya está)
- Output Directory: `dist` (ya está)
- Install Command: `npm install` (ya está)

#### Environment Variables (Variables de Entorno)

Haz clic en **"Environment Variables"** y agrega:

| Nombre | Valor |
|--------|-------|
| `VITE_SUPABASE_URL` | `https://qqtzfdrhgyyicrrkowvi.supabase.co` |
| `VITE_SUPABASE_ANON_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFxdHpmZHJoZ3l5aWNycmtvd3ZpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY3MjMzMDgsImV4cCI6MjA5MjI5OTMwOH0.emihaOMb4-EunNyXwP6u73zBKiz7DUCLWDj4MaWUIQA` |
| `VITE_ML_API_URL` | `https://tu-backend.railway.app` (lo configuraremos después) |
| `VITE_APP_NAME` | `Sistema de Análisis Académico` |
| `VITE_APP_VERSION` | `1.0.0` |

**IMPORTANTE**: Por ahora deja `VITE_ML_API_URL` como `http://localhost:8000`, lo cambiaremos después de desplegar el backend.

### Paso 5: Desplegar

1. Haz clic en **"Deploy"**
2. Espera 2-3 minutos mientras Vercel construye tu aplicación
3. ¡Listo! Tu frontend estará en: `https://tu-proyecto.vercel.app`

### Paso 6: Configurar CORS en Supabase

1. Ve a tu proyecto en **Supabase**
2. Ve a **Settings** > **API**
3. Baja a **"API Settings"** > **"CORS"**
4. Agrega la URL de tu Vercel: `https://tu-proyecto.vercel.app`

---

## 🐍 PARTE 2: DESPLEGAR BACKEND EN RAILWAY

El backend FastAPI no puede ir en Vercel, pero Railway es gratis y perfecto para Python.

### Paso 1: Crear Cuenta en Railway

1. Ve a **https://railway.app**
2. Haz clic en **"Login"** o **"Start a New Project"**
3. Inicia sesión con **GitHub**

### Paso 2: Crear Nuevo Proyecto

1. Haz clic en **"New Project"**
2. Selecciona **"Deploy from GitHub repo"**
3. Selecciona tu repositorio **"sistema-academico-ia"**

### Paso 3: Configurar el Servicio

1. Railway detectará que es Python
2. Haz clic en **"Settings"**
3. En **"Root Directory"**, escribe: `ml-api`
4. En **"Start Command"**, escribe:
   ```
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

### Paso 4: Agregar Variables de Entorno

En **"Variables"**, agrega:

```
SUPABASE_URL=https://qqtzfdrhgyyicrrkowvi.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFxdHpmZHJoZ3l5aWNycmtvd3ZpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjcyMzMwOCwiZXhwIjoyMDkyMjk5MzA4fQ.IOwzgOnZWOYOvRr_lcMhD_TWqpix7u76Lc2qgN70w58
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFxdHpmZHJoZ3l5aWNycmtvd3ZpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY3MjMzMDgsImV4cCI6MjA5MjI5OTMwOH0.emihaOMb4-EunNyXwP6u73zBKiz7DUCLWDj4MaWUIQA
API_HOST=0.0.0.0
API_PORT=$PORT
CORS_ORIGINS=https://tu-proyecto.vercel.app,http://localhost:5173
LOG_LEVEL=INFO
MODEL_PATH=app/models/trained
REPORTS_OUTPUT_DIR=reports
```

**IMPORTANTE**: Reemplaza `https://tu-proyecto.vercel.app` con tu URL real de Vercel.

### Paso 5: Desplegar

1. Railway desplegará automáticamente
2. Espera 3-5 minutos
3. Obtendrás una URL como: `https://tu-backend.railway.app`

### Paso 6: Actualizar Frontend con URL del Backend

1. Ve a tu proyecto en **Vercel**
2. Ve a **Settings** > **Environment Variables**
3. Edita `VITE_ML_API_URL`
4. Cambia a: `https://tu-backend.railway.app`
5. Haz clic en **"Save"**
6. Ve a **"Deployments"** y haz clic en los **"..."** del último deployment
7. Haz clic en **"Redeploy"** para aplicar los cambios

---

## 🔄 ACTUALIZAR EL CÓDIGO (Después del primer despliegue)

### Usando GitHub Desktop

1. Abre **GitHub Desktop**
2. Verás los archivos que has cambiado
3. Escribe un mensaje de commit: "Descripción de los cambios"
4. Haz clic en **"Commit to main"**
5. Haz clic en **"Push origin"**
6. Vercel y Railway desplegarán automáticamente los cambios

### Usando Git Terminal

```powershell
git add .
git commit -m "Descripción de los cambios"
git push
```

---

## 🎉 URLS FINALES

Después de completar todos los pasos, tendrás:

- **Frontend**: `https://tu-proyecto.vercel.app`
- **Backend API**: `https://tu-backend.railway.app`
- **API Docs**: `https://tu-backend.railway.app/docs`
- **Base de Datos**: Supabase (ya configurado)

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### Error: "Build failed"
- Verifica que el Root Directory sea `frontend`
- Asegúrate de que `package.json` esté en la carpeta frontend

### Error: "Module not found"
- Las variables de entorno no están configuradas
- Revisa que todas las variables `VITE_*` estén en Vercel

### Backend no responde
- Verifica que el Start Command sea correcto
- Revisa los logs en Railway

### CORS Error
- Agrega la URL de Vercel en las variables `CORS_ORIGINS` del backend
- Agrega la URL de Vercel en Supabase CORS settings

---

## 📞 ALTERNATIVAS AL DESPLIEGUE

### Si no quieres usar Railway para el Backend:

**Opción 1: Render** (Gratis)
- Ve a https://render.com
- Similar a Railway
- 750 horas gratis al mes

**Opción 2: Heroku** (Gratis con limitaciones)
- Ve a https://heroku.com
- Clásico y confiable
- Requiere tarjeta de crédito

**Opción 3: Fly.io** (Gratis)
- Ve a https://fly.io
- Muy rápido
- 3 máquinas pequeñas gratis

---

## ✅ CHECKLIST DE DESPLIEGUE

### Frontend (Vercel)
- [ ] Cuenta creada en Vercel
- [ ] Repositorio en GitHub
- [ ] Proyecto importado en Vercel
- [ ] Root Directory configurado a `frontend`
- [ ] Variables de entorno agregadas
- [ ] Despliegue exitoso
- [ ] URL funcional

### Backend (Railway)
- [ ] Cuenta creada en Railway
- [ ] Proyecto creado
- [ ] Root Directory configurado a `ml-api`
- [ ] Start Command configurado
- [ ] Variables de entorno agregadas
- [ ] Despliegue exitoso
- [ ] URL del backend obtenida

### Integración
- [ ] URL del backend actualizada en Vercel
- [ ] CORS configurado en backend
- [ ] CORS configurado en Supabase
- [ ] Frontend redeployado con nueva URL
- [ ] Sistema funcionando end-to-end

---

## 🎓 PARA TU TESIS

Incluye en tu documentación:

1. **Diagrama de arquitectura** de despliegue (arriba)
2. **URLs de producción** de tu sistema
3. **Capturas de pantalla** del sistema en producción
4. **Métricas de rendimiento** (tiempo de carga, etc.)

---

¡Listo! Si tienes algún problema durante el despliegue, avísame y te ayudo en tiempo real.
