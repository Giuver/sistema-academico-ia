"""
Generador de datos sintéticos de estudiantes
Crea perfiles realistas de estudiantes de secundaria
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import os

fake = Faker('es_PE')  # Locale peruano


def generar_estudiantes(num_estudiantes: int = None) -> pd.DataFrame:
    """
    Genera datos sintéticos de estudiantes
    
    Args:
        num_estudiantes: Número de estudiantes a generar (default: desde ENV)
    
    Returns:
        DataFrame con datos de estudiantes
    """
    if num_estudiantes is None:
        num_estudiantes = int(os.getenv("NUM_ESTUDIANTES", 500))
    
    estudiantes = []
    
    # Distribución por grado (1ro a 5to de secundaria)
    grados_dist = [1, 2, 3, 4, 5]
    secciones = ['A', 'B', 'C', 'D']
    
    for i in range(num_estudiantes):
        grado = np.random.choice(grados_dist)
        
        # Edad apropiada para el grado (12-13 para 1ro, hasta 16-17 para 5to)
        edad_base = 11 + grado
        edad_variacion = np.random.choice([0, 1])  # Algunos repitieron
        edad = edad_base + edad_variacion
        
        # Fecha de nacimiento basada en edad
        anio_nacimiento = datetime.now().year - edad
        fecha_nacimiento = fake.date_between(
            start_date=f'{anio_nacimiento}-01-01',
            end_date=f'{anio_nacimiento}-12-31'
        )
        
        # Datos del estudiante
        genero = np.random.choice(['M', 'F'])
        nombres = fake.first_name_male() if genero == 'M' else fake.first_name_female()
        apellidos = f"{fake.last_name()} {fake.last_name()}"
        
        estudiante = {
            'codigo': f'EST{str(i+1).zfill(4)}',
            'nombres': nombres,
            'apellidos': apellidos,
            'dni': fake.unique.random_number(digits=8, fix_len=True),
            'fecha_nacimiento': fecha_nacimiento.isoformat(),
            'genero': genero,
            'grado': grado,
            'seccion': np.random.choice(secciones),
            'direccion': fake.address(),
            'telefono_contacto': fake.phone_number()[:15],
            'email_contacto': fake.email(),
            'nombre_apoderado': fake.name(),
            'telefono_apoderado': fake.phone_number()[:15],
            'activo': True
        }
        
        estudiantes.append(estudiante)
    
    df = pd.DataFrame(estudiantes)
    
    # Guardar localmente
    df.to_csv('output/estudiantes.csv', index=False)
    print(f"✅ {len(df)} estudiantes generados y guardados en output/estudiantes.csv")
    
    return df


if __name__ == "__main__":
    os.makedirs('output', exist_ok=True)
    generar_estudiantes()
