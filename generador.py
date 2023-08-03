import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sbs
from multiprocess.dummy import Pool
import subprocess
import sys
import os

"""
TO DO:
- Entrar a la página de la facultad de ingenieria y probar la clave 1413 (Introducción a la Economia) y extraer la tabla de datos
- Colocar los datos en un excel y guardarlo
- Generalizar la función para cualquier clabe
- Anidar los datos extraidos en un único excell


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

#Accede al navegador y a la página de la facultad
driver = webdriver.Chrome()
driver.get("https://www.ssa.ingenieria.unam.mx/horarios.html")

campo_clave = driver.find_element("id","clave")
buscar = driver.find_element("id","buscar")
campo_clave.send_keys("1413")
buscar.click()

import re
import requests
from colorama import Fore

website = "https://www.ssa.ingenieria.unam.mx/horarios.html"
resultado = requests.get(website)
content = resultado.text
print(content)

time.sleep(5)

driver.close()
"""

def llenarNulos(df):
    df = df.dropna(subset=['Días'])

lista_horarios = list()
df = pd.read_excel('Excel/Septimo.xlsx')

entrada = 13 #Hora de entrada minima
salida = 22 #Hora máxima de salida
clases_sabados = False


df = df.dropna(subset=['Días']).reset_index(drop=True)
df['Clave'].fillna(method='ffill',inplace=True)
df['Gpo'].fillna(method='ffill',inplace=True)
df['Tipo'].fillna(method='ffill',inplace=True)
df['Cupo'].fillna(method='ffill',inplace=True)
#df['Nombre'].fillna(method='ffill',inplace=True)
for i in range(len(df)-1):
    if df.iloc[i+1].Profesor == '(PRESENCIAL)':
        df.loc[i+1,'Profesor'] = df.iloc[i].Profesor



def ordenarDataFrame(df):
    renglones_por_clv = df.groupby('Clave').size().reset_index(name = 'Opciones')
    df_ordenado = df.merge(renglones_por_clv, on = 'Clave').sort_values(['Opciones','Clave'],ascending = False)
    df_ordenado = df_ordenado.reset_index(drop=True)
    return df_ordenado

def abrir_carpeta(ruta):
    if sys.platform == "win32":
        subprocess.Popen(f'explorer "{ruta}"')
    elif sys.platform == "darwin":
        # macOS
        subprocess.Popen(["open", ruta])
    elif sys.platform == "linux":
        # Linux
        subprocess.Popen(["xdg-open", ruta])
    else:
        print("No se pudo abrir la carpeta")    

#Verificación por horario
def haySolapeHoras(a,b): #DataFrame, comparativa a comparativa b
    if b.Inicio_min - a.Inicio_min == 0: #empiezan a la misma hora
        return True
    if b.Inicio_min - a.Inicio_min > 0: #b empieza después que a
        if(b.Inicio_min - a.Inicio_min < a.Duracion*60):
            return True
    else:
        if(abs(b.Inicio_min - a.Inicio_min) < b.Duracion*60):
            return True 
    return False
    

def noHaySolape(horario_actual,materia):    
    """
    Verifica si existe un solape entre un potencial horario_actual y una materia (renglón del dataframe)

    Parameters
    ----------
        horario_actual: dataFrame
            Es el horario_actual que se va armando
        materia: series
            Es la fila que contiene toda la info de la materia que se quiere meter
    """
    orden = ['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab']
    for i in range(len(horario_actual)):
        for j in range(len(materia)):
            grupo = materia.iloc[j]
            prod = horario_actual.iloc[i].loc[orden] * grupo.loc[orden]
            #Ejecuta la funcion all para ver si todos los elementos son cero
            if(not (prod == 0).all()):
               if(haySolapeHoras(horario_actual.iloc[i],grupo)):
                   return False
    return True

no_materia = len(df.Clave.unique())
df = ordenarDataFrame(df)
claves = df.Clave.unique().tolist()
print(claves)

#Crea el encabezado de los dummy values de los días (en orden)
orden = ['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab'] 

#Obtiene los dummy values directo del df
dummy_dias = pd.Series(df.Días).str.get_dummies(sep=', ')

# Reordena y añade los valores de las variables ficticias a la serie "dias" y cambia los NaN por 0
dummy_dias = dummy_dias.reindex(orden, axis=1).fillna(0, downcast='int64')

#Añade este nuevo df al df original
df = df.assign(**dummy_dias)

# # Get dummies de las horas

#Crea una series de las horas que se imparte esa materia
horas_sep = df.Horario.str.split(" a ")

#Crea un diccionario con la series anterior, la clave es el índice de la serie y el valor la tupla de horas
diccionario = dict(zip(horas_sep.index, horas_sep.values))

#A partir de este diccionario, crea un dataframe llamado horas y nombra sus columnas
horas = pd.DataFrame.from_dict(diccionario).transpose()
horas.columns = ['Inicio','Fin']

#Une las horas al dataframe original
df = df.assign(**horas)


#Genera una series que contiene las horas y los minutos como tupla
hrs_y_min = df.Inicio.str.split(":")

#Obtiene la hora de inicio en terminos de minutos y crea una nueva columna en el df
minutos = hrs_y_min.str[0].astype(int)*60 +  hrs_y_min.str[1].astype(int)

#Une la variable minutos como inicio
df = df.assign(Inicio_min = minutos)

#obtiene la hora final en terminos de minutos y crea una nueva columna en el df
hrs_y_min = df.Fin.str.split(":")
minutos = hrs_y_min.str[0].astype(int)*60 +  hrs_y_min.str[1].astype(int)

#Une la variable miniutos como fin
df = df.assign(Fin_min = minutos)

if entrada>0:
    min_entrada = entrada*60
    if clases_sabados:
        deleted = df.loc[(df['Inicio_min'] < min_entrada) & (df['Sab'] == 0), :]
    else:
        deleted = df.loc[(df['Inicio_min'] < min_entrada),:]

    claves_desechadas = deleted.itertuples()

    
    for fila in claves_desechadas:
        #print(str(fila[1]) + " " + str(fila[2]))
        df.drop(df[(df['Clave'] == fila[1]) & (df['Gpo'] == fila[2])].index,inplace=True)
    df = df.reset_index(drop=True)


if salida>0:
    min_salida = salida*60
    if clases_sabados:
        deleted = df.loc[(df['Fin_min'] > min_salida) & (df['Sab']==0),:]
    else:
        deleted = df.loc[(df['Fin_min'] > min_salida), :]
    for fila in claves_desechadas:
        df.drop(df[(df['Clave'] == fila[1]) & (df['Gpo'] == fila[2])].index,inplace=True)
    df = df.reset_index(drop=True)


#Calcula la duración de cada clase en horas
duracion = df.Fin_min - df.Inicio_min
df = df.assign(Duracion = duracion/60)

def combinarMaterias(horario,materia_actual):
    """
    Es una función recursiva que toma los parámetros para ir concatenando un horario
    Parameters
    ------------
        horario: dataFrame
            El horario que se va formando
        materia_actual: int
            La materia del renglón del df que se concatena
    
    """
    # if len(horario.Clave.unique())==len(claves) or materia_actual in horario.Clave:
    #     return
    #Obtiene los grupos de la materia actual y los convierte en un arreglo de enteros
    grupos = df.loc[df["Clave"] == materia_actual].Gpo.unique().tolist()
    for grupo_actual in grupos:
        #Obtiene un df que contiene todas las filas de un grupo
        new_rows = df.loc[(df["Clave"]==materia_actual) & (df["Gpo"]==grupo_actual)]
        #Esta row puede ser multiple dado que algunos grupos se descomponen así
        if noHaySolape(horario,new_rows):
            temp = horario
            horario = pd.concat([horario, new_rows])
            if len(horario.Clave.unique()) == len(claves):
                lista_horarios.append(horario)
            else:
                siguiente_mat_ind = claves.index(materia_actual) + 1
                combinarMaterias(horario,claves[siguiente_mat_ind])
            horario = temp
                
            


# def procesar_datos(args):
#     #print("Se está procesando")
#     horario, indice, = args
#     combinarMaterias(horario, indice)


# def generarHorarios():
#         indices =  df.loc[df['Clave']==df.iloc[0]['Clave']].index
#         horarios = [None]*len(indices)

#         pool = Pool(len(indices)) 
        
#         #print("Procesos:" + str(len(indices)))

#         pool.map(procesar_datos, zip(horarios,indices))
#         pool.close()
#         pool.join()

def includes(horario,materia):
    for i in range(0,len(horario)): #Checa con todas las materias del horario
        if (materia.Gpo == horario.iloc[i].Gpo and materia.Clave == horario.iloc[i].Clave):
            return True
    return False

def plotMateria(df,gnt):
    import random
    R = random.uniform(0.3,0.75)
    G = random.uniform(0, 0.1)
    B = random.uniform(0.6, 1)
    
    i = 0
    hora = (df.Inicio_min/60)
    duracion = df.Duracion
    
    for cat in df.loc[orden]: #Lo que hace es particionar el df a los días de la semana
        if cat == 1:
            gnt.broken_barh([(i,1)], (hora, duracion) ,facecolors = (R, G, B))
            nombre_materia = df.Nombre[:10]                                                     #Corta el texto para que quepa en el cuadro
            nombre_profe = df.Profesor.split(" ")
            nombre_pila = nombre_profe[1]
            nombre_pila = nombre_pila[:5]
            apellido = nombre_profe[-2]
            #nombre_pila = df.Profesor[:7]
            inicial = apellido [:1]
            nombre = nombre_materia + "\n" + str(df.Gpo) + " " + nombre_pila  + " " + inicial                                    
            gnt.text(i+0.1,hora+1.5,nombre,color="white",fontweight = "bold",fontsize = 8) #x,y,texto,color,grosor y tamaño
        i = i+1


def plotHorario(horario, numero):
    fig, gnt = plt.subplots()
    gnt.set_ylim(6,23 )
    gnt.set_xlim(0,6)
    gnt.set_xlabel('Día')
    gnt.set_ylabel('Hora')
    gnt.set_facecolor('white')
    #horas = ['7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22']
    dias = ['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado']
    plt.gca().invert_yaxis()
    gnt.set_yticks(np.arange(7, 23,1))
    gnt.set_xticks(np.arange(0,6,1))
    gnt.set_xticklabels(dias,ha="left")
    gnt.grid(True)

    for i in range(0,len(horario)):
        plotMateria(horario.iloc[i],gnt)

    plt.savefig("Horarios/opción" + str(numero) + ".jpg",dpi = 250)
    plt.close()


def clearCarpeta():
    import os, shutil
    folder = 'Horarios/'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('No fue posible borrar la carpeta %s. Excepción: %s' % (file_path, e))
    

def imprimirHorarios():
    clearCarpeta()
    if len(lista_horarios) == 0:
        print("No se puede generar ningún horario con las materias ingresadas.")
        return 0
    n=1
    for horario in lista_horarios:
        plotHorario(horario,n)
        #print(horario.iloc[:,0:8].drop(['Tipo','Cupo'],axis=1))
        horario.drop(horario.tail(1).index,inplace=True)
        n+=1
    abrir_carpeta("Horarios")
    

#Crea un df vacío con las mismas columnas que el df del excel
#horario = pd.DataFrame(columns = df.columns)
#indices_iniciales = df.loc[df[df]]

#generarHorarios(df)
if __name__ == '__main__':
    horario = df.head(0)
    combinarMaterias(horario,claves[0])
print("Horarios generados: " + str(len(lista_horarios)))
imprimirHorarios()



