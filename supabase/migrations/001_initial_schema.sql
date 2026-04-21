-- ================================================
-- SISTEMA INTELIGENTE DE ANÁLISIS ACADÉMICO
-- IE Pública Dos de Mayo - Chincha, 2026
-- ================================================

-- Habilitar extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ================================================
-- TABLA: perfiles
-- Extiende auth.users con información adicional y roles
-- ================================================
CREATE TABLE perfiles (
    id UUID REFERENCES auth.users ON DELETE CASCADE PRIMARY KEY,
    rol TEXT NOT NULL CHECK (rol IN ('admin', 'director', 'docente', 'consulta')),
    nombres TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    dni TEXT UNIQUE,
    telefono TEXT,
    email TEXT,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para perfiles
CREATE INDEX idx_perfiles_rol ON perfiles(rol);
CREATE INDEX idx_perfiles_dni ON perfiles(dni);

-- Comentarios
COMMENT ON TABLE perfiles IS 'Perfiles de usuarios del sistema con roles específicos';
COMMENT ON COLUMN perfiles.rol IS 'admin: administrador, director: coordinador académico, docente: profesor, consulta: solo lectura';

-- ================================================
-- TABLA: estudiantes
-- Datos de estudiantes matriculados
-- ================================================
CREATE TABLE estudiantes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    codigo TEXT UNIQUE NOT NULL,
    nombres TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    dni TEXT UNIQUE,
    fecha_nacimiento DATE,
    genero TEXT CHECK (genero IN ('M', 'F')),
    grado INTEGER NOT NULL CHECK (grado BETWEEN 1 AND 5),
    seccion TEXT NOT NULL,
    direccion TEXT,
    telefono_contacto TEXT,
    email_contacto TEXT,
    nombre_apoderado TEXT,
    telefono_apoderado TEXT,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para estudiantes
CREATE INDEX idx_estudiantes_codigo ON estudiantes(codigo);
CREATE INDEX idx_estudiantes_dni ON estudiantes(dni);
CREATE INDEX idx_estudiantes_grado_seccion ON estudiantes(grado, seccion);
CREATE INDEX idx_estudiantes_activo ON estudiantes(activo);

-- Comentarios
COMMENT ON TABLE estudiantes IS 'Registro de estudiantes de la institución educativa';
COMMENT ON COLUMN estudiantes.grado IS 'Grado escolar: 1-5 (secundaria)';

-- ================================================
-- TABLA: docente_estudiante
-- Asignación de docentes a estudiantes (muchos a muchos)
-- ================================================
CREATE TABLE docente_estudiante (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    docente_id UUID REFERENCES perfiles(id) ON DELETE CASCADE,
    estudiante_id UUID REFERENCES estudiantes(id) ON DELETE CASCADE,
    periodo_id UUID,
    es_tutor BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(docente_id, estudiante_id, periodo_id)
);

-- Índices para docente_estudiante
CREATE INDEX idx_docente_estudiante_docente ON docente_estudiante(docente_id);
CREATE INDEX idx_docente_estudiante_estudiante ON docente_estudiante(estudiante_id);

-- Comentarios
COMMENT ON TABLE docente_estudiante IS 'Asignación de docentes a estudiantes por periodo';

-- ================================================
-- TABLA: periodos
-- Periodos académicos (bimestres, trimestres)
-- ================================================
CREATE TABLE periodos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    anio INTEGER NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN ('bimestre', 'trimestre', 'semestre')),
    numero INTEGER NOT NULL CHECK (numero BETWEEN 1 AND 4),
    nombre TEXT NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    activo BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(anio, tipo, numero)
);

-- Índices para periodos
CREATE INDEX idx_periodos_activo ON periodos(activo);
CREATE INDEX idx_periodos_anio ON periodos(anio);

-- Comentarios
COMMENT ON TABLE periodos IS 'Periodos académicos (bimestres o trimestres)';
COMMENT ON COLUMN periodos.activo IS 'Solo un periodo puede estar activo a la vez';

-- ================================================
-- TABLA: cursos
-- Catálogo de cursos/asignaturas
-- ================================================
CREATE TABLE cursos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nombre TEXT NOT NULL,
    codigo TEXT UNIQUE NOT NULL,
    area TEXT NOT NULL,
    grado INTEGER CHECK (grado BETWEEN 1 AND 5),
    creditos INTEGER DEFAULT 1,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para cursos
CREATE INDEX idx_cursos_codigo ON cursos(codigo);
CREATE INDEX idx_cursos_grado ON cursos(grado);
CREATE INDEX idx_cursos_area ON cursos(area);

-- Comentarios
COMMENT ON TABLE cursos IS 'Catálogo de cursos del currículo escolar';
COMMENT ON COLUMN cursos.area IS 'Área curricular: Matemática, Comunicación, Ciencias, etc.';

-- ================================================
-- TABLA: notas
-- Calificaciones de estudiantes por curso
-- ================================================
CREATE TABLE notas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    estudiante_id UUID REFERENCES estudiantes(id) ON DELETE CASCADE,
    curso_id UUID REFERENCES cursos(id) ON DELETE CASCADE,
    periodo_id UUID REFERENCES periodos(id) ON DELETE CASCADE,
    nota DECIMAL(4,2) NOT NULL CHECK (nota BETWEEN 0 AND 20),
    tipo_evaluacion TEXT CHECK (tipo_evaluacion IN ('continua', 'parcial', 'final')),
    observaciones TEXT,
    registrado_por UUID REFERENCES perfiles(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para notas
CREATE INDEX idx_notas_estudiante ON notas(estudiante_id);
CREATE INDEX idx_notas_curso ON notas(curso_id);
CREATE INDEX idx_notas_periodo ON notas(periodo_id);
CREATE INDEX idx_notas_estudiante_periodo ON notas(estudiante_id, periodo_id);

-- Comentarios
COMMENT ON TABLE notas IS 'Registro de calificaciones en escala vigesimal (0-20)';
COMMENT ON COLUMN notas.nota IS 'Nota en escala de 0 a 20';

-- ================================================
-- TABLA: asistencia
-- Registro diario de asistencia
-- ================================================
CREATE TABLE asistencia (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    estudiante_id UUID REFERENCES estudiantes(id) ON DELETE CASCADE,
    fecha DATE NOT NULL,
    estado TEXT NOT NULL CHECK (estado IN ('presente', 'ausente', 'tardanza')),
    justificado BOOLEAN DEFAULT FALSE,
    motivo TEXT,
    registrado_por UUID REFERENCES perfiles(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(estudiante_id, fecha)
);

-- Índices para asistencia
CREATE INDEX idx_asistencia_estudiante ON asistencia(estudiante_id);
CREATE INDEX idx_asistencia_fecha ON asistencia(fecha);
CREATE INDEX idx_asistencia_estado ON asistencia(estado);
CREATE INDEX idx_asistencia_estudiante_fecha ON asistencia(estudiante_id, fecha DESC);

-- Comentarios
COMMENT ON TABLE asistencia IS 'Registro diario de asistencia de estudiantes';

-- ================================================
-- TABLA: conducta
-- Evaluación de conducta por periodo
-- ================================================
CREATE TABLE conducta (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    estudiante_id UUID REFERENCES estudiantes(id) ON DELETE CASCADE,
    periodo_id UUID REFERENCES periodos(id) ON DELETE CASCADE,
    calificacion TEXT NOT NULL CHECK (calificacion IN ('AD', 'A', 'B', 'C')),
    incidencias TEXT,
    observaciones TEXT,
    registrado_por UUID REFERENCES perfiles(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(estudiante_id, periodo_id)
);

-- Índices para conducta
CREATE INDEX idx_conducta_estudiante ON conducta(estudiante_id);
CREATE INDEX idx_conducta_periodo ON conducta(periodo_id);
CREATE INDEX idx_conducta_calificacion ON conducta(calificacion);

-- Comentarios
COMMENT ON TABLE conducta IS 'Evaluación de comportamiento por periodo';
COMMENT ON COLUMN conducta.calificacion IS 'AD: Logro Destacado, A: Logro Esperado, B: En Proceso, C: En Inicio';

-- ================================================
-- TABLA: alertas
-- Sistema de alertas tempranas de riesgo académico
-- ================================================
CREATE TABLE alertas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    estudiante_id UUID REFERENCES estudiantes(id) ON DELETE CASCADE,
    tipo TEXT NOT NULL CHECK (tipo IN ('critica', 'moderada', 'preventiva')),
    nivel_riesgo DECIMAL(3,2) CHECK (nivel_riesgo BETWEEN 0 AND 1),
    categoria TEXT CHECK (categoria IN ('rendimiento', 'asistencia', 'conducta', 'multiple')),
    motivo TEXT NOT NULL,
    detalles JSONB,
    estado TEXT DEFAULT 'activa' CHECK (estado IN ('activa', 'en_atencion', 'resuelta', 'descartada')),
    prioridad INTEGER DEFAULT 1 CHECK (prioridad BETWEEN 1 AND 5),
    docente_asignado UUID REFERENCES perfiles(id),
    fecha_atencion TIMESTAMPTZ,
    fecha_resolucion TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para alertas
CREATE INDEX idx_alertas_estudiante ON alertas(estudiante_id);
CREATE INDEX idx_alertas_tipo ON alertas(tipo);
CREATE INDEX idx_alertas_estado ON alertas(estado);
CREATE INDEX idx_alertas_prioridad ON alertas(prioridad DESC);
CREATE INDEX idx_alertas_docente ON alertas(docente_asignado);
CREATE INDEX idx_alertas_activas ON alertas(estudiante_id, estado) WHERE estado IN ('activa', 'en_atencion');

-- Comentarios
COMMENT ON TABLE alertas IS 'Sistema de alertas tempranas para estudiantes en riesgo';
COMMENT ON COLUMN alertas.tipo IS 'critica: >70% riesgo, moderada: 40-70%, preventiva: <40%';
COMMENT ON COLUMN alertas.nivel_riesgo IS 'Probabilidad de 0 a 1 generada por modelo ML';

-- ================================================
-- TABLA: recomendaciones
-- Recomendaciones pedagógicas sugeridas
-- ================================================
CREATE TABLE recomendaciones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    alerta_id UUID REFERENCES alertas(id) ON DELETE CASCADE,
    tipo TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    estrategia TEXT NOT NULL,
    recursos TEXT,
    prioridad INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para recomendaciones
CREATE INDEX idx_recomendaciones_alerta ON recomendaciones(alerta_id);

-- Comentarios
COMMENT ON TABLE recomendaciones IS 'Recomendaciones pedagógicas generadas automáticamente';

-- ================================================
-- TABLA: intervenciones
-- Registro de intervenciones realizadas
-- ================================================
CREATE TABLE intervenciones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    alerta_id UUID REFERENCES alertas(id) ON DELETE CASCADE,
    estudiante_id UUID REFERENCES estudiantes(id) ON DELETE CASCADE,
    tipo_intervencion TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    estrategia_aplicada TEXT,
    responsable UUID REFERENCES perfiles(id),
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE,
    resultado TEXT CHECK (resultado IN ('exitosa', 'en_progreso', 'sin_efecto', 'pendiente_evaluacion')),
    observaciones TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para intervenciones
CREATE INDEX idx_intervenciones_alerta ON intervenciones(alerta_id);
CREATE INDEX idx_intervenciones_estudiante ON intervenciones(estudiante_id);
CREATE INDEX idx_intervenciones_responsable ON intervenciones(responsable);
CREATE INDEX idx_intervenciones_resultado ON intervenciones(resultado);

-- Comentarios
COMMENT ON TABLE intervenciones IS 'Registro de intervenciones pedagógicas realizadas';

-- ================================================
-- TABLA: predicciones_ml
-- Historial de predicciones del modelo ML
-- ================================================
CREATE TABLE predicciones_ml (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    estudiante_id UUID REFERENCES estudiantes(id) ON DELETE CASCADE,
    periodo_id UUID REFERENCES periodos(id) ON DELETE CASCADE,
    tipo_prediccion TEXT NOT NULL CHECK (tipo_prediccion IN ('desaprobacion', 'desercion', 'nota_estimada')),
    probabilidad DECIMAL(4,3) CHECK (probabilidad BETWEEN 0 AND 1),
    valor_estimado DECIMAL(4,2),
    confianza DECIMAL(4,3),
    modelo_usado TEXT NOT NULL,
    version_modelo TEXT NOT NULL,
    features_usadas JSONB,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para predicciones_ml
CREATE INDEX idx_predicciones_estudiante ON predicciones_ml(estudiante_id);
CREATE INDEX idx_predicciones_periodo ON predicciones_ml(periodo_id);
CREATE INDEX idx_predicciones_tipo ON predicciones_ml(tipo_prediccion);
CREATE INDEX idx_predicciones_fecha ON predicciones_ml(created_at DESC);

-- Comentarios
COMMENT ON TABLE predicciones_ml IS 'Historial de predicciones generadas por modelos ML';
COMMENT ON COLUMN predicciones_ml.confianza IS 'Nivel de confianza del modelo (0-1)';

-- ================================================
-- TABLA: metricas_modelo
-- Métricas de evaluación de modelos ML
-- ================================================
CREATE TABLE metricas_modelo (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    modelo_nombre TEXT NOT NULL,
    version TEXT NOT NULL,
    tipo_modelo TEXT NOT NULL,
    accuracy DECIMAL(5,4),
    precision DECIMAL(5,4),
    recall DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    roc_auc DECIMAL(5,4),
    parametros JSONB,
    dataset_size INTEGER,
    fecha_entrenamiento TIMESTAMPTZ NOT NULL,
    activo BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para metricas_modelo
CREATE INDEX idx_metricas_modelo_nombre ON metricas_modelo(modelo_nombre);
CREATE INDEX idx_metricas_modelo_activo ON metricas_modelo(activo);
CREATE INDEX idx_metricas_fecha ON metricas_modelo(fecha_entrenamiento DESC);

-- Comentarios
COMMENT ON TABLE metricas_modelo IS 'Métricas de evaluación de modelos ML entrenados';

-- ================================================
-- TABLA: logs_sistema
-- Registro de acciones importantes del sistema
-- ================================================
CREATE TABLE logs_sistema (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id UUID REFERENCES perfiles(id),
    accion TEXT NOT NULL,
    tabla_afectada TEXT,
    registro_id UUID,
    datos_anteriores JSONB,
    datos_nuevos JSONB,
    ip_address TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices para logs_sistema
CREATE INDEX idx_logs_usuario ON logs_sistema(usuario_id);
CREATE INDEX idx_logs_accion ON logs_sistema(accion);
CREATE INDEX idx_logs_fecha ON logs_sistema(created_at DESC);

-- Comentarios
COMMENT ON TABLE logs_sistema IS 'Auditoría de acciones críticas del sistema';

-- ================================================
-- FUNCIONES Y TRIGGERS
-- ================================================

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplicar trigger a todas las tablas con updated_at
CREATE TRIGGER update_perfiles_updated_at BEFORE UPDATE ON perfiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_estudiantes_updated_at BEFORE UPDATE ON estudiantes FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_periodos_updated_at BEFORE UPDATE ON periodos FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_cursos_updated_at BEFORE UPDATE ON cursos FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_notas_updated_at BEFORE UPDATE ON notas FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_asistencia_updated_at BEFORE UPDATE ON asistencia FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_conducta_updated_at BEFORE UPDATE ON conducta FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_alertas_updated_at BEFORE UPDATE ON alertas FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_intervenciones_updated_at BEFORE UPDATE ON intervenciones FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ================================================
-- VISTAS ÚTILES
-- ================================================

-- Vista: resumen de estudiantes con datos académicos
CREATE OR REPLACE VIEW vista_estudiantes_resumen AS
SELECT 
    e.id,
    e.codigo,
    e.nombres,
    e.apellidos,
    e.grado,
    e.seccion,
    COUNT(DISTINCT n.id) as total_notas,
    ROUND(AVG(n.nota), 2) as promedio_general,
    COUNT(DISTINCT CASE WHEN a.estado = 'ausente' THEN a.id END) as total_inasistencias,
    COUNT(DISTINCT CASE WHEN al.estado IN ('activa', 'en_atencion') THEN al.id END) as alertas_activas
FROM estudiantes e
LEFT JOIN notas n ON e.id = n.estudiante_id
LEFT JOIN asistencia a ON e.id = a.estudiante_id
LEFT JOIN alertas al ON e.id = al.estudiante_id
WHERE e.activo = TRUE
GROUP BY e.id, e.codigo, e.nombres, e.apellidos, e.grado, e.seccion;

-- Vista: alertas activas con información del estudiante
CREATE OR REPLACE VIEW vista_alertas_activas AS
SELECT 
    al.id,
    al.tipo,
    al.nivel_riesgo,
    al.categoria,
    al.motivo,
    al.prioridad,
    al.estado,
    e.codigo as estudiante_codigo,
    e.nombres || ' ' || e.apellidos as estudiante_nombre,
    e.grado,
    e.seccion,
    p.nombres || ' ' || p.apellidos as docente_asignado_nombre,
    al.created_at,
    al.fecha_atencion
FROM alertas al
JOIN estudiantes e ON al.estudiante_id = e.id
LEFT JOIN perfiles p ON al.docente_asignado = p.id
WHERE al.estado IN ('activa', 'en_atencion')
ORDER BY al.prioridad DESC, al.created_at DESC;

-- Vista: rendimiento por curso y periodo
CREATE OR REPLACE VIEW vista_rendimiento_curso AS
SELECT 
    c.nombre as curso,
    c.area,
    p.anio,
    p.nombre as periodo,
    COUNT(n.id) as total_evaluaciones,
    ROUND(AVG(n.nota), 2) as promedio,
    COUNT(CASE WHEN n.nota < 11 THEN 1 END) as desaprobados,
    COUNT(CASE WHEN n.nota >= 11 THEN 1 END) as aprobados,
    ROUND(COUNT(CASE WHEN n.nota < 11 THEN 1 END)::DECIMAL / NULLIF(COUNT(n.id), 0) * 100, 2) as porcentaje_desaprobacion
FROM cursos c
JOIN notas n ON c.id = n.curso_id
JOIN periodos p ON n.periodo_id = p.id
GROUP BY c.id, c.nombre, c.area, p.anio, p.nombre;

-- ================================================
-- COMENTARIOS FINALES
-- ================================================

COMMENT ON DATABASE postgres IS 'Sistema Inteligente de Análisis del Rendimiento Académico - IE Dos de Mayo';
