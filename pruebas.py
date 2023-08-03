import pandas as pd

lista_horarios = list()
df = pd.read_excel('Excel/Prueba.xlsx')
entrada = 11 #Hora de entrada minima
salida = 22 #Hora máxima de salida

materia_actual = 840
grupos = df.loc[df["Clave"] == materia_actual].Gpo.unique()
#print(grupos)
print(df)
print(df.iloc[:-1])

    