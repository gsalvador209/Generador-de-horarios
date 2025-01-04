from bitarray import bitarray
import pandas as pd
import numpy as np
from datetime import datetime


def check_compatibility(A,B):
    return not (A & B).any()



def create_matrix(dias_str, horas_str):
    orden = ['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab'] 
    time_format = "%H:%M"   

    #Extrae los días que esan en formato "Lun, Vie"
    dias_list = dias_str.split(", ")
    dias = ['1' if dia in dias_list else '0' for dia in orden]
    dias = np.array(dias, dtype=int).reshape(1, 6)

    #Extrae las horas que estan en formato "07:00 a 09:00"
    horas_sep = horas_str.split(" a ")
    hora_inicio = datetime.strptime(horas_sep[0], time_format)
    hora_fin = datetime.strptime(horas_sep[1], time_format)
    duration = (hora_fin-hora_inicio).total_seconds()/(60*30) # Obtener la duración en bloques de 30 minutos
    duration = '1'*int(duration) # Crea los bits que indican duración
    inicio_h = hora_inicio.hour - 7   
    inicio_m = hora_inicio.minute//30
    horas = '0'*(inicio_h*2+inicio_m) + duration
    horas = horas.ljust(30,'0')
    horas = np.array(list(horas), dtype=int).reshape(30,1)
 
    # Creación de la matriz
    matriz = np.logical_and(horas, dias)
    flatten = matriz.flatten()
    bit_matrix = bitarray(flatten.tolist()) 
    return bit_matrix

df = pd.read_excel("cache_materias.xlsx")
for row in df.itertuples():
    #print(row)
    print(create_matrix(row.Días, row.Horario))
    #break
