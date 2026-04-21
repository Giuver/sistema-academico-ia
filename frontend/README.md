# Frontend - Sistema de Análisis Académico

Aplicación web React para el Sistema Inteligente de Análisis del Rendimiento Académico.

## Características

- 🔐 Autenticación con Supabase Auth
- 📊 Dashboards interactivos con Recharts
- ⚡ Alertas en tiempo real con Supabase Realtime
- 🎨 UI moderna con TailwindCSS
- 📱 Diseño responsive
- 🔄 Gestión de estado con React Query

## Instalación

### 1. Instalar dependencias

```bash
npm install
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env.local
# Editar .env.local con tus credenciales
```

### 3. Ejecutar en desarrollo

```bash
npm run dev
```

La aplicación estará disponible en http://localhost:5173

## Estructura del Proyecto

```
frontend/
├── src/
│   ├── components/      # Componentes React
│   │   ├── auth/        # Componentes de autenticación
│   │   ├── dashboard/   # Dashboards y gráficos
│   │   ├── estudiantes/ # Gestión de estudiantes
│   │   ├── alertas/     # Panel de alertas
│   │   └── common/      # Componentes reutilizables
│   ├── pages/           # Páginas principales
│   ├── services/        # Servicios de API
│   │   ├── supabase.ts  # Cliente Supabase
│   │   └── mlApi.ts     # Cliente ML API
│   ├── hooks/           # Custom React hooks
│   ├── types/           # TypeScript types
│   ├── utils/           # Utilidades
│   ├── App.tsx          # Componente principal
│   └── main.tsx         # Punto de entrada
├── public/              # Archivos estáticos
└── package.json         # Dependencias
```

## Scripts Disponibles

- `npm run dev` - Servidor de desarrollo
- `npm run build` - Build para producción
- `npm run preview` - Preview de build
- `npm run lint` - Ejecutar linter

## Rutas Principales

- `/` - Landing page
- `/login` - Inicio de sesión
- `/dashboard` - Dashboard principal
- `/estudiantes` - Listado de estudiantes
- `/alertas` - Panel de alertas
- `/reportes` - Generación de reportes

## Roles y Permisos

- **Admin**: Acceso completo al sistema
- **Director**: Vista institucional completa
- **Docente**: Vista de estudiantes asignados
- **Consulta**: Solo lectura

## Tecnologías

- React 18
- TypeScript
- Vite
- TailwindCSS
- Supabase JS Client
- React Query (TanStack Query)
- React Router v6
- Recharts
- Lucide React (iconos)

## Build para Producción

```bash
npm run build
```

Los archivos optimizados estarán en la carpeta `dist/`

## Despliegue

### Vercel

```bash
vercel deploy --prod
```

### Netlify

Conecta tu repositorio Git en Netlify y configura:
- Build command: `npm run build`
- Publish directory: `dist`

## Variables de Entorno Requeridas

```env
VITE_SUPABASE_URL=         # URL de tu proyecto Supabase
VITE_SUPABASE_ANON_KEY=    # Anon key de Supabase
VITE_ML_API_URL=           # URL de la API de ML
```

## Desarrollo

### Agregar nueva página

1. Crear componente en `src/pages/`
2. Agregar ruta en `src/App.tsx`
3. Agregar enlace en navegación

### Agregar nuevo componente

1. Crear en `src/components/`
2. Exportar desde `index.ts` si es común
3. Usar TypeScript para props

### Conectar con Supabase

```typescript
import { supabase } from '@/services/supabase'

// Consultar datos
const { data, error } = await supabase
  .from('estudiantes')
  .select('*')

// Suscribirse a cambios en tiempo real
supabase
  .channel('alertas')
  .on('postgres_changes', 
    { event: 'INSERT', schema: 'public', table: 'alertas' },
    (payload) => {
      console.log('Nueva alerta:', payload)
    }
  )
  .subscribe()
```

## Licencia

Proyecto académico - IE Pública Dos de Mayo - Chincha, 2026
