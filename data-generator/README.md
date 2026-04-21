# Generador de Datos Sintéticos

Genera datos académicos realistas para pruebas del sistema.

## Instalación

```bash
pip install -r requirements.txt
```

## Configuración

```bash
cp .env.example .env
# Editar .env con credenciales de Supabase
```

## Uso

### Generar todos los datos

```bash
python generate_all.py
```

### Generar datos individuales

```bash
# Solo estudiantes
python generate_students.py

# Solo docentes
python generate_teachers.py

# Solo datos académicos
python generate_academic_data.py
```

## Datos Generados

- **Estudiantes**: 500 (configurable)
- **Docentes**: 25 (configurable)
- **Periodos**: 3 años académicos
- **Notas**: ~40,000 calificaciones
- **Asistencia**: ~150,000 registros
- **Conducta**: ~1,500 evaluaciones

## Características

- Datos realistas con distribución normal
- Correlación entre variables (notas, asistencia, conducta)
- Estudiantes con diferentes perfiles de rendimiento
- Fechas y periodos académicos consistentes
- DNIs, teléfonos y emails generados
