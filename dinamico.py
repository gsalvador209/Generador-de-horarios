from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from io import StringIO
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time
import pickle

def fill_horario(row: np.array):
    """Tranforma las filas de una matriz para que se llenen los 0 por 1
    en los patrones de horas. Llena cada lista 1[0,...]1 a 1[1,...]0

    Arguments: 
    row (np.array): La fila de la matriz que será transformada

    Returns:
    row: La fila transformada

    """

    ones_indices = np.where(row == 1)[0]  # Encuentra los índices de los unos
    if len(ones_indices) < 2:  # Si hay menos de dos unos, no se puede hacer la transformación
        return row
    
    start, end = ones_indices[0], ones_indices[-1]  # Primer y último índice de los unos
    row[start:end] = 1  # Llena los ceros entre el primer y el último uno con unos
    row[end] = 0  # Convierte el último uno en cero
    return row

def get_tablas(clave: int) -> pd.DataFrame:
    '''
    Realiza la búsqueda de información a través del navegador con Selenium y BeautifulSoup
    
    Parameters:
    clave (int): La clave de materia que se extraerá la información.

    Returns: 
    grupos (list): Lista de Dataframes que representan los grupos de una materia
    '''
    options = Options()
    options.add_argument("--headless")
    url = "https://www.ssa.ingenieria.unam.mx/horarios.html"
    palabras_excluidas=['Y','E','SISTEMAS','DE','FUNDAMENTOS','LA','EN','A','AL','INTRODUCCIÓN','SEMINARIO','TALLER','-','SOCIO-HUM.:']
    grupos = []

    driver = webdriver.Firefox(options=options)
    driver.get(url)
    time.sleep(1)
    campo_clave = driver.find_element("id","clave")
    buscar = driver.find_element("id","buscar")

    campo_clave.clear()
    campo_clave.send_keys(clave)
    buscar.click()
    page_source = driver.page_source
    driver.quit()
    soup = BeautifulSoup(page_source, features="lxml")

    #Obtención del nombre de la materia
    nombre_materia = soup.find('div',{"class":"col-10"}).text.split()

    #Limpia el nombre de las materias para hacerlo más identificable
    nombre_filtrado = ' '.join((filter(lambda s: s not in palabras_excluidas, nombre_materia))) 
    nombre_filtrado = ''.join([i for i in nombre_filtrado if not i.isdigit()])
    nombre_filtrado = nombre_filtrado[1:]
    if (":" in nombre_filtrado):
        nombre_filtrado = nombre_filtrado.split(':')
        nombre_filtrado = nombre_filtrado[1:]
        nombre_filtrado = ' '.join(nombre_filtrado)

    #Obtiene todas las tablas de la página
    tables = soup.find_all('table')

    for table in tables:
        nombre_tabla = table.find('tbody').find('tr').find('th').text  
        #print(nombre_tabla)  

        if nombre_tabla == "GRUPOS SIN VACANTES":
            if len(tables) == 1: 
                #En este caso solo hay grupos sin vacantes
                raise Exception("No hay grupos disponibles para la materia " + nombre_filtrado) 
            else:
                #Se salta los grupos sin vacantes
                continue

        primera_clave = table.find_all('tbody')[1].find('tr').find('td').text
        if int(primera_clave) > 5000:
            laboratorio=  True
            #Agrega el "Laboratorio" al nombre de la materia si es el caso
            nombre_filtrado = "L." + nombre_filtrado  

        opciones = pd.read_html(StringIO(str(table)))[0]
        opciones[('AUX','Nombre')] = [nombre_filtrado for _ in range(len(opciones))]
        opciones.columns = [col [1] for col in opciones.columns]

        grupos.append(opciones)
            
    return grupos

def grupos_to_matrices(grupos: pd.DataFrame):
        dummy_dias = pd.Series(grupos.Días).str.get_dummies(sep=', ')
        dummy_dias = dummy_dias.reindex(['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab'], axis=1,fill_value=0)
        days_matrix = dummy_dias.to_numpy()

        # Generar el rango de tiempo
        time_range = pd.date_range(start="07:00", end="21:30", freq="30min")

        # Convertir a una lista de cadenas de tiempo
        time_list = time_range.strftime('%H:%M').tolist()

        dummy_hours = pd.Series(grupos.Horario).str.get_dummies(sep=' a ')
        hours_matrix = dummy_hours.reindex(time_list,axis=1,fill_value=0).to_numpy()

        for i in range(hours_matrix.shape[0]):
             hours_matrix[i, :] = fill_horario(hours_matrix[i, :])

        nos_grupo = grupos["Gpo"].unique().tolist()
        #return days_matrix,hours_matrix,nos_grupo

        group_indxs = grupos[grupos['Gpo'].duplicated(keep='last')].index.to_numpy()
        skip_indxs = group_indxs + 1

        matrices_de_grupos = []

        for i in range(len(grupos)):
            if i in skip_indxs:
                continue
            grupo_matrix = np.dot(hours_matrix[i].reshape((30,1)),days_matrix[i].reshape((1,6)))
            if i in group_indxs:
               grupo_matrix = grupo_matrix + np.dot(hours_matrix[i+1].reshape((30,1)),days_matrix[i+1].reshape((1,6)))
            #print(grupo_matrix)

            matrices_de_grupos.append([nos_grupo[i],grupo_matrix])
        return matrices_de_grupos

def build_horarios(grupos: list,horarios : list)->list:
        horarios_temporales = []
        if len(horarios) == 0:
            horarios = grupos    
            return horarios
       
        for i,horario in enumerate(horarios):
            for j,materia in enumerate(grupos):
                if not np.any(np.bitwise_and(horario[0,:],materia)): #Compara materia actual con el horario base
                    print("Compatibles")
                # print(horario.ndim, materia.ndim)
                # print(horario.shape,materia.shape)
                # horario[0,:] = horario[0,:]+materia
                # horario = np.concatenate([horario,materia.reshape(1,30,6)])
                # horarios_temporales.append(horario)
                # new_materia = [horario[0][0]+materia]
                # new_horario=[]
                # new_horario.append(new_materia)
                # new_horario.append(horario[0][0])
                # new_horario.append(materia)
                # horarios_temporales.append(new_horario)
        # else:
        #     new_horario = np.array([materia,materia]) #Crea un arreglo 3D 30x7x2, el base y la materia
        #     horarios_temporales.append(new_horario) #Lista de horarios temporal
        # claves.append(clave)
        # horarios_actuales = horarios_temporales
        # horarios_temporales = []

# def check_compatibility(materias: list):
#     horarios = []
#     for i,row in enumerate(materias[0][0]):
#         colis_days_m = np.bitwise_and(materias[1][0],row)
#         if(not np.any(colis_days_m)):
#             print("El grupo %d es compatible con todas las materias"%(i+1))
#         else:
#             #Se obtienen las horas de la materia iterada en el día que hay colisión
#             hours_second_m = np.dot(materias[1][1].T,colis_days_m)

#             #Se obtiene el AND entre las horas del grupo iterador y la matriz de horas de la iterada
#             colis_hours = np.bitwise_and(hours_second_m,materias[0][1][i].reshape((30,1)))

#             if not np.any(colis_hours):
#                 for j in materias[1][2]:
#                     horario = [materias[0][2][i],j]    
#                     horarios.append(horario)
#             else:
#                 print("Grupo: ",i+1)
#                 #print(colis_hours)
#                 #print(materias[1][0])
#                 #print(colis_days_m)
#                 #print(hours_second_m)
#                 #print(np.bitwise_and(colis_hours,materias[1][1].T))
#                 # print("El grupo {0} es compatible con todos lod grupos de la materia B".format(i+1))
#             #horarios.append(horario)
#     #print(horarios)
        
        

def main():
    claves = 1867,2948
    debug =  True
    materias = []
    horarios = []

    if not debug:
        for clave in claves:
            arr_grupos = get_tablas(clave)
            for teo_lab in arr_grupos:
                lista_grupos = grupos_to_matrices(teo_lab)
                materias.append(lista_grupos)
                #print(lista_grupos)
        with open('materias.pkl','wb') as file:
            pickle.dump(materias,file)
    else:
        with open('materias.pkl','rb') as file:
            materias = pickle.load(file)
            #horarios = build_horarios(lista_grupos,horarios)
            #print(len(horarios))
            #return
    
    print(len(materias))


start_time = time.time()
main()
print("--- %s seconds ---" % (time.time() - start_time))