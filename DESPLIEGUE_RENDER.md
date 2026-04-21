# 🚀 GUÍA RÁPIDA: DESPLEGAR BACKEND EN RENDER

## Backend FastAPI - ML API

Render es perfecto para Python y es **completamente GRATIS**.

---

## ⚡ PASO 1: Crear Cuenta en Render (2 minutos)

1. Ve a: **https://render.com**
2. Haz clic en **"Get Started"** o **"Sign Up"**
3. Selecciona **"Sign in with GitHub"**
4. Autoriza Render para acceder a tus repositorios

---

## 📦 PASO 2: Crear Nuevo Web Service (1 minuto)

1. En el Dashboard de Render, haz clic en **"New +"**
2. Selecciona **"Web Service"**
3. Busca y selecciona tu repositorio: **"sistema-academico-ia"**
4. Haz clic en **"Connect"**

---

## 🔧 PASO 3: Configurar el Servicio (3 minutos)

En la página de configuración, completa los siguientes campos:

### Información Básica

**Name:**
```
sistema-academico-ml-api
```

**Region:**
```
Oregon (US West)
```
(O la más cercana a tu ubicación)

**Branch:**
```
main
```

**Root Directory:**
```
ml-api
```
⚠️ **MUY IMPORTANTE**: Debe ser `ml-api`

### Build & Deploy

**Runtime:**
```
Python 3
```
(Render lo detectará automáticamente)

**Build Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

## 🔐 PASO 4: Variables de Entorno (2 minutos)

Desplázate hacia abajo hasta la sección **"Environment Variables"** y agrega:

### Variables a Agregar:

**Variable 1:**
```
Key: SUPABASE_URL
Value: https://qqtzfdrhgyyicrrkowvi.supabase.co
```

**Variable 2:**
```
Key: SUPABASE_KEY
Value: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFxdHpmZHJoZ3l5aWNycmtvd3ZpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjcyMzMwOCwiZXhwIjoyMDkyMjk5MzA4fQ.IOwzgOnZWOYOvRr_lcMhD_TWqpix7u76Lc2qgN70w58
```

**Variable 3:**
```
Key: SUPABASE_ANON_KEY
Value: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFxdHpmZHJoZ3l5aWNycmtvd3ZpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY3MjMzMDgsImV4cCI6MjA5MjI5OTMwOH0.emihaOMb4-EunNyXwP6u73zBKiz7DUCLWDj4MaWUIQA
```

**Variable 4:**
```
Key: API_HOST
Value: 0.0.0.0
```

**Variable 5:**
```
Key: CORS_ORIGINS
Value: https://sistema-academico-ia.vercel.app,http://localhost:5173
```

⚠️ **IMPORTANTE**: Reemplaza `sistema-academico-ia.vercel.app` con tu URL real de Vercel cuando la tengas.

**Variable 6:**
```
Key: LOG_LEVEL
Value: INFO
```

**Variable 7:**
```
Key: MODEL_PATH
Value: app/models/trained
```

**Variable 8:**
```
Key: REPORTS_OUTPUT_DIR
Value: reports
```

---

## ✅ PASO 5: Desplegar (5 minutos)

1. **Selecciona el plan**: Elige **"Free"** (0 USD)
2. Haz clic en **"Create Web Service"**
3. Render comenzará a construir tu aplicación
4. Espera 5-7 minutos (primera vez tarda más)
5. Verás logs en tiempo real del proceso

### Durante el despliegue verás:

```
==> Building...
==> Installing dependencies...
==> Starting server...
==> Your service is live!
```

---

## 🎉 PASO 6: Obtener tu URL (1 minuto)

Una vez desplegado, Render te dará una URL como:

```
https://sistema-academico-ml-api.onrender.com
```

**COPIA ESTA URL** - la necesitarás para actualizar Vercel.

### Verificar que funciona:

Abre en tu navegador:
```
https://tu-url.onrender.com/docs
```

Deberías ver la documentación Swagger de tu API 🎊

---

## 🔄 PASO 7: Actualizar Frontend en Vercel (2 minutos)

Ahora que tienes la URL del backend, actualiza tu frontend:

1. Ve a tu proyecto en **Vercel**
2. Ve a **Settings** > **Environment Variables**
3. Busca la variable `VITE_ML_API_URL`
4. Haz clic en los **"..."** > **"Edit"**
5. Cambia el valor a: `https://tu-url.onrender.com` (tu URL de Render)
6. Guarda
7. Ve a **Deployments**
8. Haz clic en los **"..."** del último deployment
9. Selecciona **"Redeploy"**

---

## 📊 COMPARACIÓN RENDER VS OTROS

| Característica | Render | Railway | Heroku |
|----------------|--------|---------|--------|
| **Precio** | Gratis | Gratis | Gratis (limitado) |
| **Python** | ✅ Nativo | ✅ Nativo | ✅ Nativo |
| **Tiempo Activo** | 750 hrs/mes | 500 hrs/mes | Dynos limitados |
| **Build Time** | Rápido | Muy rápido | Medio |
| **SSL** | Gratis | Gratis | Gratis |
| **Logs** | 7 días | Ilimitado | Limitado |

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### Error: "Build failed"
**Causa**: Python no encuentra las dependencias  
**Solución**: Verifica que Root Directory sea `ml-api`

### Error: "Module not found"
**Causa**: Faltan variables de entorno  
**Solución**: Revisa que todas las 8 variables estén agregadas

### Error: "Application Error"
**Causa**: Start Command incorrecto  
**Solución**: Debe ser `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Backend muy lento
**Causa**: Plan gratuito "hiberna" después de 15 minutos  
**Solución**: Primera petición tarda ~30 segundos (es normal)

### CORS Error
**Causa**: URL de Vercel no está en CORS_ORIGINS  
**Solución**: Actualiza la variable con tu URL real de Vercel

---

## ⚠️ LIMITACIONES DEL PLAN GRATUITO

- **Hibernación**: Después de 15 minutos de inactividad, el servicio "duerme"
- **Primera carga**: Tarda ~30 segundos en despertar
- **750 horas/mes**: Suficiente para desarrollo y pruebas
- **Sin persistencia**: Los archivos generados (reportes, modelos) se borran al reiniciar

### Para tu Tesis:
- ✅ Perfecto para demos y presentaciones
- ✅ Suficiente para pruebas durante desarrollo
- ⚠️ Para producción real, considera upgrade a plan pagado

---

## 🎯 CHECKLIST DE DESPLIEGUE

### Backend (Render)
- [ ] Cuenta creada en Render
- [ ] Web Service creado
- [ ] Root Directory = `ml-api`
- [ ] Start Command correcto
- [ ] 8 variables de entorno agregadas
- [ ] Plan Free seleccionado
- [ ] Despliegue exitoso
- [ ] URL copiada
- [ ] Docs accesibles en `/docs`

### Integración
- [ ] URL del backend actualizada en Vercel
- [ ] CORS configurado correctamente
- [ ] Frontend redeployado
- [ ] Sistema funcionando end-to-end

---

## 📈 MONITOREO

### Ver Logs en Tiempo Real:
1. En Render Dashboard, selecciona tu servicio
2. Ve a la pestaña **"Logs"**
3. Verás logs en vivo de tu aplicación

### Métricas:
- **CPU Usage**: Monitor de uso de CPU
- **Memory**: Uso de RAM
- **Bandwidth**: Transferencia de datos

---

## 🔄 ACTUALIZAR CÓDIGO

Cada vez que hagas `git push` a GitHub:
1. Render detectará los cambios automáticamente
2. Construirá y desplegará la nueva versión
3. Sin downtime (despliegue sin interrupciones)

---

## 🎊 ¡LISTO!

Tu arquitectura completa:

```
┌─────────────────┐
│    Usuario      │
└────────┬────────┘
         │
         ↓
┌─────────────────┐     ┌──────────────────┐
│   Frontend      │────▶│   Backend ML     │
│   (Vercel)      │     │   (Render)       │
│   React + TS    │     │   FastAPI        │
└─────────────────┘     └────────┬─────────┘
                                 │
                                 ↓
                        ┌─────────────────┐
                        │   Supabase      │
                        │   PostgreSQL    │
                        └─────────────────┘
```

### URLs Finales:
- **Frontend**: https://sistema-academico-ia.vercel.app
- **Backend**: https://sistema-academico-ml-api.onrender.com
- **API Docs**: https://sistema-academico-ml-api.onrender.com/docs
- **Base de Datos**: Supabase (ya configurado)

---

**⭐ Tu sistema completo está en la nube y funcionando 24/7**
