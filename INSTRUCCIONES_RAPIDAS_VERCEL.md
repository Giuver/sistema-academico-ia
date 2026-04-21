# 🚀 GUÍA RÁPIDA: SUBIR A VERCEL EN 5 PASOS

## ⚡ Para usuarios con prisa

### PASO 1: Crear cuenta en Vercel (2 minutos)
1. Ve a **https://vercel.com**
2. Haz clic en **"Sign Up"**
3. Selecciona **"Continue with GitHub"**
4. Autoriza Vercel

### PASO 2: Subir código a GitHub (5 minutos)

**Opción A: Con GitHub Desktop (MÁS FÁCIL)**

1. Descarga e instala: https://desktop.github.com
2. Abre GitHub Desktop
3. File > Add local repository
4. Selecciona la carpeta del proyecto
5. Si dice "not a git repository", haz clic en "Create Repository"
6. Haz clic en "Publish repository"
7. ¡Listo!

**Opción B: Con Terminal**

```powershell
cd C:\Users\Lenovo\OneDrive\Escritorio\Tesis-Alexander

# Inicializar git
git init
git add .
git commit -m "Initial commit"

# Crear repo en GitHub (ve a github.com/new primero)
git remote add origin https://github.com/TU-USUARIO/sistema-academico-ia.git
git push -u origin main
```

### PASO 3: Importar en Vercel (2 minutos)

1. En Vercel, haz clic en **"Add New..."** > **"Project"**
2. Selecciona tu repositorio **"sistema-academico-ia"**
3. Haz clic en **"Import"**

### PASO 4: Configurar (3 minutos)

En la página de configuración:

1. **Framework Preset**: Selecciona "Vite"
2. **Root Directory**: Cambia a `frontend` ← ⚠️ **MUY IMPORTANTE**
3. **Environment Variables**: Agrega estas 3 variables:

```
VITE_SUPABASE_URL=https://qqtzfdrhgyyicrrkowvi.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFxdHpmZHJoZ3l5aWNycmtvd3ZpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzY3MjMzMDgsImV4cCI6MjA5MjI5OTMwOH0.emihaOMb4-EunNyXwP6u73zBKiz7DUCLWDj4MaWUIQA
VITE_ML_API_URL=http://localhost:8000
```

### PASO 5: Deploy (1 minuto)

1. Haz clic en **"Deploy"**
2. Espera 2-3 minutos
3. ¡Listo! Tu app estará en: `https://tu-proyecto.vercel.app`

---

## ⚠️ NOTA IMPORTANTE

El **frontend** (interfaz) estará en Vercel, pero el **backend** (API con Python) necesita otro servicio como Railway o Render (también gratis).

Para la guía completa del backend, ve a: **DESPLIEGUE_VERCEL.md**

---

## 🐛 Si algo falla:

### Error: "Build failed"
→ Verifica que el Root Directory sea `frontend` (no vacío)

### Error: "Cannot find module"
→ Asegúrate de haber agregado las 3 variables de entorno

### Error: "Page not found"
→ Revisa que `vercel.json` esté en la carpeta `frontend`

---

## 📞 ¿Necesitas ayuda?

Revisa el archivo **DESPLIEGUE_VERCEL.md** para la guía detallada completa.

---

## ✅ CHECKLIST RÁPIDO

- [ ] Cuenta en Vercel creada
- [ ] Código subido a GitHub
- [ ] Proyecto importado en Vercel
- [ ] Root Directory = `frontend`
- [ ] 3 variables de entorno agregadas
- [ ] Deploy completado
- [ ] URL funcionando

¡Eso es todo! Tu sistema ya está en línea. 🎉
