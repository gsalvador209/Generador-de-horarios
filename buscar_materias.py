from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from io import StringIO
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time
import pickle

def get_tablas(claves: list) -> pd.DataFrame:
    '''
    Realiza la búsqueda de información a través del navegador con Selenium y BeautifulSoup
    
    Parameters:
    clave (int): La clave de materia que se extraerá la información.

    Returns: 
    grupos (list): Lista de Dataframes que representan los grupos de una materia
    '''
    df = pd.DataFrame()
    options = Options()
    #options.add_argument("--headless")
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

with open("grupos.txt", "r") as file:
    claves = {}
    for line in file:
        clave, grupo = line.strip().split(":")
        claves[int(clave)] = grupo

for clave in claves.keys():
    try:
        grupos = get_tablas(clave)
        for grupo in grupos:
            filtered_rows = grupo[grupo['Gpo'] == claves[clave]]
            if not filtered_rows.empty:
                print(filtered_rows[['Clave', 'Gpo', 'Vacantes', 'Nombre', 'Profesor']])
    except Exception as e:
        print(e)
        continue