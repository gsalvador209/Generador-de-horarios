import pandas as pd
import numpy as np

sc = pd.read_excel("Generador-de-horarios/Molde_horario.xlsx")
df = pd.read_excel("Octavo_sem.xlsx")
sc = sc.fillna('x')
#print(sc)


renglones_por_clv = df.groupby('Clave').size().reset_index(name = 'Opciones')
print(renglones_por_clv)