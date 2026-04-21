"""
Generador de datos sintéticos de docentes
Crea perfiles de docentes y coordinadores
"""

import pandas as pd
import numpy as np
from faker import Faker
import os

fake = Faker('es_PE')


def generar_docentes(num_docentes: int = None) -> pd.DataFrame:
    """
    Genera datos sintéticos de docentes
    
    Args:
        num_docentes: Número de docentes a generar
    
    Returns:
        DataFrame con datos de docentes
    """
    if num_docentes is None:
        num_docentes = int(os.getenv("NUM_DOCENTES", 25))
    
    docentes = []
    
    # Roles: la mayoría son docentes, algunos son directores
    roles = ['docente'] * (num_docentes - 2) + ['director'] * 2
    np.random.shuffle(roles)
    
    for i, rol in enumerate(roles):
        genero = np.random.choice(['M', 'F'])
        nombres = fake.first_name_male() if genero == 'M' else fake.first_name_female()
        apellidos = f"{fake.last_name()} {fake.last_name()}"
        
        docente = {
            'rol': rol,
            'nombres': nombres,
            'apellidos': apellidos,
            'dni': fake.unique.random_number(digits=8, fix_len=True),
            'telefono': fake.phone_number()[:15],
            'email': f"{nombres.lower()}.{apellidos.split()[0].lower()}@dosdmayo.edu.pe",
            'activo': True
        }
        
        docentes.append(docente)
    
    df = pd.DataFrame(docentes)
    
    # Guardar localmente
    os.makedirs('output', exist_ok=True)
    df.to_csv('output/docentes.csv', index=False)
    print(f"✅ {len(df)} docentes generados y guardados en output/docentes.csv")
    
    return df


if __name__ == "__main__":
    generar_docentes()
