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
claves = [1672,1590,1052,1598]
df = pd.DataFrame()
for clave in claves:
    campo_clave.clear()
    campo_clave.send_keys(clave)
    buscar.click()
    page_source = driver.page_source

    soup = BeautifulSoup(page_source, features="lxml")
    
    tables = soup.find_all('table')
    
    opciones = pd.read_html(StringIO(str(tables[0])))[0]
    df = pd.concat([df,opciones],axis=0,ignore_index=True)
    if len(tables)>1:
        opciones2 = pd.read_html(StringIO(str(tables[1])))[0]
        df = pd.concat([df,opciones2],axis=0,ignore_index=True)

driver.quit()
df.columns = [col [1] for col in df.columns]
df.to_excel("output.xlsx")