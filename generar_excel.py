from bs4 import BeautifulSoup
from selenium import webdriver
import time
from io import StringIO
import pandas as pd


# Abrir página de la facultad
url = "https://www.ssa.ingenieria.unam.mx/horarios.html"
driver = webdriver.Firefox()
driver.get("https://www.ssa.ingenieria.unam.mx/horarios.html")
time.sleep(1)
campo_clave = driver.find_element("id","clave")
buscar = driver.find_element("id","buscar")

# Iterar entre todas las claves para ir formando el horario
claves = [1535]
palabras_excluidas=['Y','E','DE','FUNDAMENTOS','LA','EN','A','AL','INTRODUCCIÓN','SEMINARIO','TALLER','-','SOCIO-HUM.:']
df = pd.DataFrame()

for clave in claves:
    campo_clave.clear()
    campo_clave.send_keys(clave)
    buscar.click()
    page_source = driver.page_source

    soup = BeautifulSoup(page_source, features="lxml")
    nombre_soup = soup.find_all('div',{"class":"col-10"})
    texto_materia = nombre_soup[0].text.split()
    nombre_filtrado = ' '.join((filter(lambda s: s not in palabras_excluidas, texto_materia)))
    
    nombre_filtrado = ''.join([i for i in nombre_filtrado if not i.isdigit()])
    nombre_filtrado = nombre_filtrado[1:]
    if (":" in nombre_filtrado):
        nombre_filtrado = nombre_filtrado.split(':')
        nombre_filtrado = nombre_filtrado[1:]
        nombre_filtrado = ' '.join(nombre_filtrado)
        
    
     
    tables = soup.find_all('table')
    
    opciones = pd.read_html(StringIO(str(tables[0])))[0]
    opciones[('AUX','Nombre')] = [nombre_filtrado for _ in range(len(opciones))]
    df = pd.concat([df,opciones],axis=0,ignore_index=True)
    if len(tables)>1:
        nombre_filtrado_lab = "L." + nombre_filtrado
        opciones2 = pd.read_html(StringIO(str(tables[1])))[0]
        opciones2[('AUX','Nombre')] = [nombre_filtrado_lab for _ in range(len(opciones2))]
        df = pd.concat([df,opciones2],axis=0,ignore_index=True)


driver.quit()
df.columns = [col [1] for col in df.columns]
print("El excel se ha generado exitosamente")
print(df)
df.to_excel("VLSI.xlsx")