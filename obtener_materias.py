import requests
import pandas as pd

# URL de la página web
url = "https://www.ssa.ingenieria.unam.mx/horarios.html"

# Lista de claves
claves = ["1537", "1535", "0406", "0434", "1686", "1413"]

# Crear un nuevo archivo de Excel
df = pd.DataFrame()

# Iterar sobre las claves
for clave in claves:

    # Ingresar la clave en el campo
    requests.post(url, data={"clave": clave})

    # Obtener la tabla de datos
    table = requests.get(url).content

     # Convertir la tabla de datos a un DataFrame de Pandas
    df2 = pd.read_html(table,match=["table table-horarios-custom"])[0]

    # Omitir los encabezados posteriores
    #df2.columns = df2.columns.tolist()[:1]

    # Combinar los DataFrames
    df = pd.concat([df, df2], ignore_index=True)

# Guardar el DataFrame en el archivo de Excel
df.to_excel("septimo.xlsx")
