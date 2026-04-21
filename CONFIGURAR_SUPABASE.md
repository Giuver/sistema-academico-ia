# 🚀 Guía Rápida: Configurar Supabase

Esta guía te ayudará a configurar Supabase para que el sistema funcione correctamente.

## 📋 Paso 1: Crear Proyecto en Supabase

1. **Accede a Supabase**
   - Ve a: https://supabase.com
   - Haz clic en "Start your project"
   - Inicia sesión con GitHub, Google o email

2. **Crear Nuevo Proyecto**
   - Clic en "New Project"
   - Completa:
     - **Name**: `sistema-academico-ia`
     - **Database Password**: Crea una contraseña fuerte (guárdala bien)
     - **Region**: `South America (São Paulo)` (más cercano a Perú)
     - **Plan**: Free
   - Clic en "Create new project"
   - ⏱️ Espera 2-3 minutos

## 🔑 Paso 2: Obtener Credenciales

Una vez listo tu proyecto:

1. En el panel lateral izquierdo, ve a **Settings** ⚙️
2. Haz clic en **API**
3. Encontrarás:

```
┌─────────────────────────────────────────────────────────┐
│ Project URL                                             │
│ https://abcdefghijklmnop.supabase.co                    │ ← Copia esto
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ anon public                                             │
│ eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ...   │ ← Copia esto
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ service_role (secret)                                   │
│ eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ...   │ ← Copia esto
└─────────────────────────────────────────────────────────┘
```

## 📝 Paso 3: Actualizar Archivos de Configuración

### Frontend (`frontend\.env.local`)

Abre el archivo y reemplaza:

```env
VITE_SUPABASE_URL=https://tu-proyecto.supabase.co
# ↓ Cambia por tu URL real ↓
VITE_SUPABASE_URL=https://abcdefghijklmnop.supabase.co

VITE_SUPABASE_ANON_KEY=tu-anon-key-aqui
# ↓ Cambia por tu anon public key ↓
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Backend (`ml-api\.env`)

Abre el archivo y reemplaza:

```env
SUPABASE_URL=https://tu-proyecto.supabase.co
# ↓ Cambia por tu URL real ↓
SUPABASE_URL=https://abcdefghijklmnop.supabase.co

SUPABASE_KEY=tu-service-role-key-aqui
# ↓ Cambia por tu service_role key ↓
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

SUPABASE_ANON_KEY=tu-anon-key-aqui
# ↓ Cambia por tu anon public key ↓
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 🗄️ Paso 4: Ejecutar Migraciones de Base de Datos

1. En el panel de Supabase, ve a **SQL Editor** (menú lateral)
2. Haz clic en "New query"
3. **Primera migración** - Copia y pega el contenido completo de:
   - `supabase\migrations\001_initial_schema.sql`
   - Haz clic en "Run" (o presiona Ctrl+Enter)
   - ✅ Deberías ver "Success. No rows returned"

4. **Segunda migración** - Crea otra query nueva:
   - Copia y pega el contenido completo de:
   - `supabase\migrations\002_row_level_security.sql`
   - Haz clic en "Run"
   - ✅ Deberías ver "Success"

## 👤 Paso 5: Crear Usuario Administrador

1. En Supabase, ve a **Authentication** > **Users**
2. Haz clic en "Add user" > "Create new user"
3. Completa:
   - **Email**: tu-email@ejemplo.com
   - **Password**: Tu contraseña segura
   - **Auto Confirm User**: ✅ (marcado)
4. Haz clic en "Create user"
5. **Copia el UUID del usuario** (algo como: `a1b2c3d4-e5f6-7890-...`)

6. Ahora ve a **SQL Editor** y ejecuta:

```sql
-- Reemplaza los valores con tu información real
INSERT INTO perfiles (id, email, rol, nombres, apellidos)
VALUES (
  '03917433-91f7-4183-ba65-ec22e0197384',  -- Tu UUID de usuario
  'tu-email@ejemplo.com',                    -- Tu email
  'admin',                                    -- Rol de administrador
  'Administrador',                            -- Tu nombre
  'del Sistema'                               -- Tu apellido
);
```

**💡 Ejemplo con valores reales:**
```sql
INSERT INTO perfiles (id, email, rol, nombres, apellidos)
VALUES (
  '03917433-91f7-4183-ba65-ec22e0197384',
  'alexander@escuela.edu.pe',
  'admin',
  'Alexander',
  'Rodriguez'
);
```

## 🔄 Paso 6: Reiniciar Servicios

En PowerShell, desde la raíz del proyecto:

```powershell
# Reiniciar frontend (presiona Ctrl+C y luego):
cd frontend
npm run dev

# En otra terminal, reiniciar backend:
cd ml-api
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## ✅ Paso 7: Probar el Sistema

1. Abre tu navegador en: http://localhost:5174
2. Inicia sesión con:
   - **Email**: tu-email@ejemplo.com
   - **Password**: La contraseña que creaste

¡Listo! El sistema debería funcionar completamente.

## 🆘 Solución de Problemas

### Error: "Invalid API key"
- Verifica que copiaste correctamente las keys
- Asegúrate de no tener espacios al inicio o final
- Las keys deben empezar con `eyJ`

### Error: "relation does not exist"
- No ejecutaste las migraciones SQL
- Ve al Paso 4 y ejecuta ambos archivos SQL

### Error: "Invalid login credentials"
- El usuario no tiene perfil en la tabla `perfiles`
- Ve al Paso 5 y crea el perfil del administrador

### Error de CORS
- Verifica que el backend esté corriendo en el puerto 8000
- Verifica que el frontend esté corriendo en el puerto 5173 o 5174

## 📞 Necesitas Ayuda?

Si tienes problemas, avísame y te ayudo paso a paso con capturas de pantalla.
