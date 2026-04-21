"""
Generador de datos académicos sintéticos
Genera notas, asistencia y conducta con correlaciones realistas
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os


def generar_datos_academicos(estudiantes_df: pd.DataFrame) -> dict:
    """
    Genera datos académicos realistas para los estudiantes
    
    Args:
        estudiantes_df: DataFrame con información de estudiantes
    
    Returns:
        Dict con DataFrames de notas, asistencia y conducta
    """
    
    # Definir periodos académicos
    anio_inicio = int(os.getenv("ANIO_INICIO", 2023))
    num_periodos = int(os.getenv("NUM_PERIODOS", 3))
    
    periodos = []
    for anio in range(anio_inicio, anio_inicio + 2):
        for bimestre in range(1, 5):
            fecha_inicio = datetime(anio, (bimestre-1)*2 + 3, 1)
            fecha_fin = fecha_inicio + timedelta(days=60)
            periodos.append({
                'anio': anio,
                'tipo': 'bimestre',
                'numero': bimestre,
                'nombre': f'{anio} - Bimestre {bimestre}',
                'fecha_inicio': fecha_inicio.date().isoformat(),
                'fecha_fin': fecha_fin.date().isoformat(),
                'activo': (anio == anio_inicio + 1 and bimestre == 2)  # Periodo actual
            })
    
    periodos_df = pd.DataFrame(periodos[:num_periodos * 2])
    
    # Cursos por grado
    cursos_data = []
    areas_curriculo = {
        'Matemática': ['Matemática'],
        'Comunicación': ['Comunicación'],
        'Ciencias': ['Ciencia y Tecnología', 'Biología', 'Física', 'Química'],
        'Sociales': ['Ciencias Sociales', 'Historia', 'Geografía'],
        'Inglés': ['Inglés'],
        'Otros': ['Educación Física', 'Arte y Cultura', 'EPT', 'Religión']
    }
    
    codigo_curso = 1
    for grado in range(1, 6):
        for area, cursos in areas_curriculo.items():
            for curso in cursos:
                # No todos los cursos en todos los grados
                if grado <= 2 and curso in ['Biología', 'Física', 'Química']:
                    continue
                
                cursos_data.append({
                    'nombre': curso,
                    'codigo': f'CUR{str(codigo_curso).zfill(3)}',
                    'area': area,
                    'grado': grado,
                    'creditos': 1,
                    'activo': True
                })
                codigo_curso += 1
    
    cursos_df = pd.DataFrame(cursos_data)
    
    # Generar notas
    print("📊 Generando notas...")
    notas = generar_notas(estudiantes_df, periodos_df, cursos_df)
    
    # Generar asistencia
    print("📅 Generando registros de asistencia...")
    asistencia = generar_asistencia(estudiantes_df, periodos_df)
    
    # Generar conducta
    print("⭐ Generando evaluaciones de conducta...")
    conducta = generar_conducta(estudiantes_df, periodos_df, notas, asistencia)
    
    return {
        'periodos': periodos_df,
        'cursos': cursos_df,
        'notas': notas,
        'asistencia': asistencia,
        'conducta': conducta
    }


def generar_notas(estudiantes_df, periodos_df, cursos_df):
    """Genera notas realistas con distribución normal"""
    notas = []
    
    for _, estudiante in estudiantes_df.iterrows():
        # Asignar perfil de rendimiento al estudiante
        perfil = np.random.choice(['excelente', 'bueno', 'regular', 'bajo'], 
                                   p=[0.15, 0.40, 0.30, 0.15])
        
        # Promedio base según perfil
        promedio_base = {
            'excelente': 17,
            'bueno': 14,
            'regular': 12,
            'bajo': 9
        }[perfil]
        
        # Cursos del grado del estudiante
        cursos_grado = cursos_df[cursos_df['grado'] == estudiante['grado']]
        
        for _, periodo in periodos_df.iterrows():
            for _, curso in cursos_grado.iterrows():
                # Variabilidad por curso
                desviacion = np.random.uniform(1, 3)
                nota = np.random.normal(promedio_base, desviacion)
                
                # Limitar entre 0 y 20
                nota = max(0, min(20, round(nota, 2)))
                
                notas.append({
                    'estudiante_codigo': estudiante['codigo'],
                    'curso_codigo': curso['codigo'],
                    'periodo_nombre': periodo['nombre'],
                    'nota': nota,
                    'tipo_evaluacion': np.random.choice(['continua', 'parcial', 'final']),
                    'observaciones': '' if nota >= 11 else 'Requiere reforzamiento'
                })
    
    return pd.DataFrame(notas)


def generar_asistencia(estudiantes_df, periodos_df):
    """Genera registros de asistencia diaria"""
    asistencia = []
    
    for _, estudiante in estudiantes_df.iterrows():
        # Perfil de asistencia
        perfil_asist = np.random.choice(['excelente', 'bueno', 'regular', 'malo'], 
                                        p=[0.50, 0.30, 0.15, 0.05])
        
        prob_ausente = {
            'excelente': 0.02,
            'bueno': 0.05,
            'regular': 0.15,
            'malo': 0.30
        }[perfil_asist]
        
        for _, periodo in periodos_df.iterrows():
            fecha_inicio = datetime.fromisoformat(periodo['fecha_inicio'])
            fecha_fin = datetime.fromisoformat(periodo['fecha_fin'])
            
            # Generar registros para días hábiles
            current_date = fecha_inicio
            while current_date <= fecha_fin:
                # Solo días de semana
                if current_date.weekday() < 5:
                    estado = np.random.choice(
                        ['presente', 'ausente', 'tardanza'],
                        p=[1-prob_ausente-0.03, prob_ausente, 0.03]
                    )
                    
                    justificado = False
                    if estado == 'ausente':
                        justificado = np.random.choice([True, False], p=[0.3, 0.7])
                    
                    asistencia.append({
                        'estudiante_codigo': estudiante['codigo'],
                        'fecha': current_date.date().isoformat(),
                        'estado': estado,
                        'justificado': justificado,
                        'motivo': 'Enfermedad' if justificado else None
                    })
                
                current_date += timedelta(days=1)
    
    return pd.DataFrame(asistencia)


def generar_conducta(estudiantes_df, periodos_df, notas_df, asistencia_df):
    """Genera evaluaciones de conducta correlacionadas con rendimiento"""
    conducta = []
    
    for _, estudiante in estudiantes_df.iterrows():
        for _, periodo in periodos_df.iterrows():
            # Calcular promedio del estudiante en el periodo
            notas_est_per = notas_df[
                (notas_df['estudiante_codigo'] == estudiante['codigo']) &
                (notas_df['periodo_nombre'] == periodo['nombre'])
            ]
            
            promedio = notas_est_per['nota'].mean() if len(notas_est_per) > 0 else 13
            
            # Conducta correlacionada con rendimiento (no siempre perfecto)
            if promedio >= 16:
                calif_conducta = np.random.choice(['AD', 'A'], p=[0.7, 0.3])
            elif promedio >= 14:
                calif_conducta = np.random.choice(['A', 'B'], p=[0.6, 0.4])
            elif promedio >= 11:
                calif_conducta = np.random.choice(['A', 'B', 'C'], p=[0.2, 0.6, 0.2])
            else:
                calif_conducta = np.random.choice(['B', 'C'], p=[0.4, 0.6])
            
            tiene_incidencias = np.random.choice([True, False], p=[0.1, 0.9])
            
            conducta.append({
                'estudiante_codigo': estudiante['codigo'],
                'periodo_nombre': periodo['nombre'],
                'calificacion': calif_conducta,
                'incidencias': 'Conversación excesiva en clase' if tiene_incidencias else None,
                'observaciones': '' if calif_conducta in ['AD', 'A'] else 'Mejorar comportamiento'
            })
    
    return pd.DataFrame(conducta)


if __name__ == "__main__":
    # Para prueba independiente
    import generate_students
    estudiantes = generate_students.generar_estudiantes(50)
    datos = generar_datos_academicos(estudiantes)
    
    os.makedirs('output', exist_ok=True)
    datos['notas'].to_csv('output/notas.csv', index=False)
    datos['asistencia'].to_csv('output/asistencia.csv', index=False)
    datos['conducta'].to_csv('output/conducta.csv', index=False)
    print("✅ Datos académicos generados")
