-- ================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- Sistema de seguridad a nivel de base de datos por roles
-- ================================================

-- ================================================
-- HABILITAR RLS EN TODAS LAS TABLAS
-- ================================================

ALTER TABLE perfiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE estudiantes ENABLE ROW LEVEL SECURITY;
ALTER TABLE docente_estudiante ENABLE ROW LEVEL SECURITY;
ALTER TABLE periodos ENABLE ROW LEVEL SECURITY;
ALTER TABLE cursos ENABLE ROW LEVEL SECURITY;
ALTER TABLE notas ENABLE ROW LEVEL SECURITY;
ALTER TABLE asistencia ENABLE ROW LEVEL SECURITY;
ALTER TABLE conducta ENABLE ROW LEVEL SECURITY;
ALTER TABLE alertas ENABLE ROW LEVEL SECURITY;
ALTER TABLE recomendaciones ENABLE ROW LEVEL SECURITY;
ALTER TABLE intervenciones ENABLE ROW LEVEL SECURITY;
ALTER TABLE predicciones_ml ENABLE ROW LEVEL SECURITY;
ALTER TABLE metricas_modelo ENABLE ROW LEVEL SECURITY;
ALTER TABLE logs_sistema ENABLE ROW LEVEL SECURITY;

-- ================================================
-- FUNCIÓN AUXILIAR: Obtener rol del usuario actual
-- ================================================

CREATE OR REPLACE FUNCTION get_user_role()
RETURNS TEXT AS $$
BEGIN
    RETURN (
        SELECT rol 
        FROM perfiles 
        WHERE id = auth.uid()
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ================================================
-- POLÍTICAS: perfiles
-- ================================================

-- Los usuarios pueden ver su propio perfil
CREATE POLICY "usuarios_ver_propio_perfil" ON perfiles
    FOR SELECT
    USING (id = auth.uid());

-- Los usuarios pueden actualizar su propio perfil (excepto rol)
CREATE POLICY "usuarios_actualizar_propio_perfil" ON perfiles
    FOR UPDATE
    USING (id = auth.uid())
    WITH CHECK (id = auth.uid() AND rol = (SELECT rol FROM perfiles WHERE id = auth.uid()));

-- Admins y directores pueden ver todos los perfiles
CREATE POLICY "admins_directores_ver_perfiles" ON perfiles
    FOR SELECT
    USING (get_user_role() IN ('admin', 'director'));

-- Solo admins pueden insertar/actualizar/eliminar perfiles
CREATE POLICY "admins_gestionar_perfiles" ON perfiles
    FOR ALL
    USING (get_user_role() = 'admin')
    WITH CHECK (get_user_role() = 'admin');

-- ================================================
-- POLÍTICAS: estudiantes
-- ================================================

-- Docentes pueden ver solo sus estudiantes asignados
CREATE POLICY "docentes_ver_sus_estudiantes" ON estudiantes
    FOR SELECT
    USING (
        get_user_role() = 'docente' AND
        id IN (
            SELECT estudiante_id 
            FROM docente_estudiante 
            WHERE docente_id = auth.uid()
        )
    );

-- Admins y directores pueden ver todos los estudiantes
CREATE POLICY "admins_directores_ver_estudiantes" ON estudiantes
    FOR SELECT
    USING (get_user_role() IN ('admin', 'director'));

-- Consulta puede ver todos los estudiantes (solo lectura)
CREATE POLICY "consulta_ver_estudiantes" ON estudiantes
    FOR SELECT
    USING (get_user_role() = 'consulta');

-- Admins y directores pueden gestionar estudiantes
CREATE POLICY "admins_directores_gestionar_estudiantes" ON estudiantes
    FOR ALL
    USING (get_user_role() IN ('admin', 'director'))
    WITH CHECK (get_user_role() IN ('admin', 'director'));

-- ================================================
-- POLÍTICAS: docente_estudiante
-- ================================================

-- Docentes pueden ver sus propias asignaciones
CREATE POLICY "docentes_ver_asignaciones" ON docente_estudiante
    FOR SELECT
    USING (
        docente_id = auth.uid() OR
        get_user_role() IN ('admin', 'director')
    );

-- Solo admins y directores pueden gestionar asignaciones
CREATE POLICY "admins_directores_gestionar_asignaciones" ON docente_estudiante
    FOR ALL
    USING (get_user_role() IN ('admin', 'director'))
    WITH CHECK (get_user_role() IN ('admin', 'director'));

-- ================================================
-- POLÍTICAS: periodos
-- ================================================

-- Todos los roles autenticados pueden ver periodos
CREATE POLICY "todos_ver_periodos" ON periodos
    FOR SELECT
    USING (auth.uid() IS NOT NULL);

-- Solo admins pueden gestionar periodos
CREATE POLICY "admins_gestionar_periodos" ON periodos
    FOR ALL
    USING (get_user_role() = 'admin')
    WITH CHECK (get_user_role() = 'admin');

-- ================================================
-- POLÍTICAS: cursos
-- ================================================

-- Todos los roles autenticados pueden ver cursos
CREATE POLICY "todos_ver_cursos" ON cursos
    FOR SELECT
    USING (auth.uid() IS NOT NULL);

-- Solo admins pueden gestionar cursos
CREATE POLICY "admins_gestionar_cursos" ON cursos
    FOR ALL
    USING (get_user_role() = 'admin')
    WITH CHECK (get_user_role() = 'admin');

-- ================================================
-- POLÍTICAS: notas
-- ================================================

-- Docentes pueden ver notas de sus estudiantes asignados
CREATE POLICY "docentes_ver_notas_sus_estudiantes" ON notas
    FOR SELECT
    USING (
        get_user_role() = 'docente' AND
        estudiante_id IN (
            SELECT estudiante_id 
            FROM docente_estudiante 
            WHERE docente_id = auth.uid()
        )
    );

-- Docentes pueden insertar/actualizar notas de sus estudiantes
CREATE POLICY "docentes_gestionar_notas_sus_estudiantes" ON notas
    FOR INSERT
    WITH CHECK (
        get_user_role() = 'docente' AND
        estudiante_id IN (
            SELECT estudiante_id 
            FROM docente_estudiante 
            WHERE docente_id = auth.uid()
        )
    );

CREATE POLICY "docentes_actualizar_notas" ON notas
    FOR UPDATE
    USING (
        get_user_role() = 'docente' AND
        estudiante_id IN (
            SELECT estudiante_id 
            FROM docente_estudiante 
            WHERE docente_id = auth.uid()
        )
    )
    WITH CHECK (
        get_user_role() = 'docente' AND
        estudiante_id IN (
            SELECT estudiante_id 
            FROM docente_estudiante 
            WHERE docente_id = auth.uid()
        )
    );

-- Admins y directores pueden ver y gestionar todas las notas
CREATE POLICY "admins_directores_ver_notas" ON notas
    FOR SELECT
    USING (get_user_role() IN ('admin', 'director'));

CREATE POLICY "admins_directores_gestionar_notas" ON notas
    FOR ALL
    USING (get_user_role() IN ('admin', 'director'))
    WITH CHECK (get_user_role() IN ('admin', 'director'));

-- Consulta puede ver todas las notas
CREATE POLICY "consulta_ver_notas" ON notas
    FOR SELECT
    USING (get_user_role() = 'consulta');

-- ================================================
-- POLÍTICAS: asistencia
-- ================================================

-- Docentes pueden gestionar asistencia de sus estudiantes
CREATE POLICY "docentes_ver_asistencia_sus_estudiantes" ON asistencia
    FOR SELECT
    USING (
        get_user_role() = 'docente' AND
        estudiante_id IN (
            SELECT estudiante_id 
            FROM docente_estudiante 
            WHERE docente_id = auth.uid()
        )
    );

CREATE POLICY "docentes_gestionar_asistencia" ON asistencia
    FOR ALL
    USING (
        get_user_role() = 'docente' AND
        estudiante_id IN (
            SELECT estudiante_id 
            FROM docente_estudiante 
            WHERE docente_id = auth.uid()
        )
    )
    WITH CHECK (
        get_user_role() = 'docente' AND
        estudiante_id IN (
            SELECT estudiante_id 
            FROM docente_estudiante 
            WHERE docente_id = auth.uid()
        )
    );

-- Admins y directores acceso completo
CREATE POLICY "admins_directores_ver_asistencia" ON asistencia
    FOR SELECT
    USING (get_user_role() IN ('admin', 'director'));

CREATE POLICY "admins_directores_gestionar_asistencia" ON asistencia
    FOR ALL
    USING (get_user_role() IN ('admin', 'director'))
    WITH CHECK (get_user_role() IN ('admin', 'director'));

-- Consulta solo lectura
CREATE POLICY "consulta_ver_asistencia" ON asistencia
    FOR SELECT
    USING (get_user_role() = 'consulta');

-- ================================================
-- POLÍTICAS: conducta
-- ================================================

-- Similar a notas y asistencia
CREATE POLICY "docentes_ver_conducta_sus_estudiantes" ON conducta
    FOR SELECT
    USING (
        get_user_role() = 'docente' AND
        estudiante_id IN (
            SELECT estudiante_id 
            FROM docente_estudiante 
            WHERE docente_id = auth.uid()
        )
    );

CREATE POLICY "docentes_gestionar_conducta" ON conducta
    FOR ALL
    USING (
        get_user_role() = 'docente' AND
        estudiante_id IN (
            SELECT estudiante_id 
            FROM docente_estudiante 
            WHERE docente_id = auth.uid()
        )
    )
    WITH CHECK (
        get_user_role() = 'docente' AND
        estudiante_id IN (
            SELECT estudiante_id 
            FROM docente_estudiante 
            WHERE docente_id = auth.uid()
        )
    );

CREATE POLICY "admins_directores_ver_conducta" ON conducta
    FOR SELECT
    USING (get_user_role() IN ('admin', 'director'));

CREATE POLICY "admins_directores_gestionar_conducta" ON conducta
    FOR ALL
    USING (get_user_role() IN ('admin', 'director'))
    WITH CHECK (get_user_role() IN ('admin', 'director'));

CREATE POLICY "consulta_ver_conducta" ON conducta
    FOR SELECT
    USING (get_user_role() = 'consulta');

-- ================================================
-- POLÍTICAS: alertas
-- ================================================

-- Docentes pueden ver alertas de sus estudiantes
CREATE POLICY "docentes_ver_alertas_sus_estudiantes" ON alertas
    FOR SELECT
    USING (
        get_user_role() = 'docente' AND
        (
            estudiante_id IN (
                SELECT estudiante_id 
                FROM docente_estudiante 
                WHERE docente_id = auth.uid()
            ) OR
            docente_asignado = auth.uid()
        )
    );

-- Docentes pueden actualizar estado de alertas asignadas a ellos
CREATE POLICY "docentes_actualizar_alertas_asignadas" ON alertas
    FOR UPDATE
    USING (
        get_user_role() = 'docente' AND
        docente_asignado = auth.uid()
    )
    WITH CHECK (
        get_user_role() = 'docente' AND
        docente_asignado = auth.uid()
    );

-- Admins y directores acceso completo
CREATE POLICY "admins_directores_ver_alertas" ON alertas
    FOR SELECT
    USING (get_user_role() IN ('admin', 'director'));

CREATE POLICY "admins_directores_gestionar_alertas" ON alertas
    FOR ALL
    USING (get_user_role() IN ('admin', 'director'))
    WITH CHECK (get_user_role() IN ('admin', 'director'));

-- Consulta solo lectura
CREATE POLICY "consulta_ver_alertas" ON alertas
    FOR SELECT
    USING (get_user_role() = 'consulta');

-- ================================================
-- POLÍTICAS: recomendaciones
-- ================================================

-- Pueden ver recomendaciones quienes pueden ver las alertas
CREATE POLICY "ver_recomendaciones_con_alertas" ON recomendaciones
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM alertas 
            WHERE alertas.id = recomendaciones.alerta_id
            AND (
                get_user_role() IN ('admin', 'director', 'consulta') OR
                (get_user_role() = 'docente' AND alertas.docente_asignado = auth.uid())
            )
        )
    );

-- Solo admins pueden gestionar recomendaciones manualmente
CREATE POLICY "admins_gestionar_recomendaciones" ON recomendaciones
    FOR ALL
    USING (get_user_role() = 'admin')
    WITH CHECK (get_user_role() = 'admin');

-- ================================================
-- POLÍTICAS: intervenciones
-- ================================================

-- Docentes pueden ver intervenciones de sus estudiantes
CREATE POLICY "docentes_ver_intervenciones_sus_estudiantes" ON intervenciones
    FOR SELECT
    USING (
        get_user_role() = 'docente' AND
        (
            estudiante_id IN (
                SELECT estudiante_id 
                FROM docente_estudiante 
                WHERE docente_id = auth.uid()
            ) OR
            responsable = auth.uid()
        )
    );

-- Docentes pueden registrar intervenciones
CREATE POLICY "docentes_registrar_intervenciones" ON intervenciones
    FOR INSERT
    WITH CHECK (
        get_user_role() = 'docente' AND
        estudiante_id IN (
            SELECT estudiante_id 
            FROM docente_estudiante 
            WHERE docente_id = auth.uid()
        ) AND
        responsable = auth.uid()
    );

-- Docentes pueden actualizar sus propias intervenciones
CREATE POLICY "docentes_actualizar_sus_intervenciones" ON intervenciones
    FOR UPDATE
    USING (
        get_user_role() = 'docente' AND
        responsable = auth.uid()
    )
    WITH CHECK (
        get_user_role() = 'docente' AND
        responsable = auth.uid()
    );

-- Admins y directores acceso completo
CREATE POLICY "admins_directores_ver_intervenciones" ON intervenciones
    FOR SELECT
    USING (get_user_role() IN ('admin', 'director'));

CREATE POLICY "admins_directores_gestionar_intervenciones" ON intervenciones
    FOR ALL
    USING (get_user_role() IN ('admin', 'director'))
    WITH CHECK (get_user_role() IN ('admin', 'director'));

-- Consulta solo lectura
CREATE POLICY "consulta_ver_intervenciones" ON intervenciones
    FOR SELECT
    USING (get_user_role() = 'consulta');

-- ================================================
-- POLÍTICAS: predicciones_ml
-- ================================================

-- Docentes pueden ver predicciones de sus estudiantes
CREATE POLICY "docentes_ver_predicciones_sus_estudiantes" ON predicciones_ml
    FOR SELECT
    USING (
        get_user_role() = 'docente' AND
        estudiante_id IN (
            SELECT estudiante_id 
            FROM docente_estudiante 
            WHERE docente_id = auth.uid()
        )
    );

-- Admins y directores pueden ver todas
CREATE POLICY "admins_directores_ver_predicciones" ON predicciones_ml
    FOR SELECT
    USING (get_user_role() IN ('admin', 'director'));

-- Solo el sistema (service role) puede insertar predicciones
CREATE POLICY "sistema_insertar_predicciones" ON predicciones_ml
    FOR INSERT
    WITH CHECK (true);  -- Solo service_role key puede acceder

-- Consulta puede ver predicciones
CREATE POLICY "consulta_ver_predicciones" ON predicciones_ml
    FOR SELECT
    USING (get_user_role() = 'consulta');

-- ================================================
-- POLÍTICAS: metricas_modelo
-- ================================================

-- Solo admins pueden ver métricas
CREATE POLICY "admins_ver_metricas" ON metricas_modelo
    FOR SELECT
    USING (get_user_role() = 'admin');

-- Solo sistema puede insertar métricas
CREATE POLICY "sistema_insertar_metricas" ON metricas_modelo
    FOR INSERT
    WITH CHECK (true);  -- Solo service_role key

-- ================================================
-- POLÍTICAS: logs_sistema
-- ================================================

-- Solo admins pueden ver logs
CREATE POLICY "admins_ver_logs" ON logs_sistema
    FOR SELECT
    USING (get_user_role() = 'admin');

-- Sistema puede insertar logs
CREATE POLICY "sistema_insertar_logs" ON logs_sistema
    FOR INSERT
    WITH CHECK (true);  -- Solo service_role key

-- ================================================
-- TRIGGERS PARA AUDITORÍA
-- ================================================

-- Función para registrar cambios en logs_sistema
CREATE OR REPLACE FUNCTION log_cambios_importantes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN
        INSERT INTO logs_sistema (usuario_id, accion, tabla_afectada, registro_id, datos_anteriores, datos_nuevos)
        VALUES (
            auth.uid(),
            'UPDATE',
            TG_TABLE_NAME,
            NEW.id,
            row_to_json(OLD),
            row_to_json(NEW)
        );
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO logs_sistema (usuario_id, accion, tabla_afectada, registro_id, datos_anteriores)
        VALUES (
            auth.uid(),
            'DELETE',
            TG_TABLE_NAME,
            OLD.id,
            row_to_json(OLD)
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Aplicar auditoría a tablas críticas
CREATE TRIGGER audit_estudiantes AFTER UPDATE OR DELETE ON estudiantes
FOR EACH ROW EXECUTE FUNCTION log_cambios_importantes();

CREATE TRIGGER audit_notas AFTER UPDATE OR DELETE ON notas
FOR EACH ROW EXECUTE FUNCTION log_cambios_importantes();

CREATE TRIGGER audit_alertas AFTER UPDATE OR DELETE ON alertas
FOR EACH ROW EXECUTE FUNCTION log_cambios_importantes();

-- ================================================
-- HABILITAR REALTIME
-- ================================================

-- Configurar publicación de realtime para tablas que lo necesitan
ALTER PUBLICATION supabase_realtime ADD TABLE alertas;
ALTER PUBLICATION supabase_realtime ADD TABLE intervenciones;
ALTER PUBLICATION supabase_realtime ADD TABLE predicciones_ml;

-- ================================================
-- COMENTARIOS
-- ================================================

COMMENT ON FUNCTION get_user_role() IS 'Obtiene el rol del usuario autenticado actual';
COMMENT ON FUNCTION log_cambios_importantes() IS 'Registra cambios en tablas críticas para auditoría';
