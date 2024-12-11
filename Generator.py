import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import subprocess
import sys
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
from io import StringIO
from tqdm import tqdm

# TODO: 
#   - Globalizar el nombre de la carpeta en las funciones que lo utilizan
#   - Implementar paletas de colores
#   - Agregar filtros avanzados: clases los viernes, bloqueos de horas, grupos excluidos
#   - Agregar barra de progreso basándose en los índices actuales de cada materia (multiplicar los indices relativos y dividir
#     entre el máximo posible).
#   - Agregar modo grupos preferidos por materia

class FolderManager:
    def abrir_carpeta(self,ruta="Horarios_generados"):
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

    def clear_carpeta(self):
        import os, shutil
        folder = "Horarios_generados"
        os.makedirs(folder, exist_ok=True)
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('No fue posible borrar la carpeta %s. Excepción: %s' % (file_path, e))
        

class Materias:
    """
    Esta clase define un DataFrame con las materias que se van a considerar para la generación de horarios.
    """
    cache_materias = "cache_materias.xlsx"

    def __init__(self, claves_mat: list, nombre_horario : str = "Horarios_generados",df_grupos = None, real_time = False, silence = True):
        self.nombre_horario = nombre_horario
        self.claves_mat = claves_mat
        self._df_grupos = df_grupos
        self.real_time = real_time
        self.silence = silence
        self._gen_df(self.silence)

    @property
    def df_grupos(self):
        return self._df_grupos  

    def _gen_df(self, headless = True):
        """
        Genera el DataFrame con la información de las materias que se van a considerar para la generación de horarios.
        """

        df = pd.DataFrame()
        claves = self.claves_mat
        url = "https://www.ssa.ingenieria.unam.mx/horarios.html"
        palabras_excluidas=['Y','E','SISTEMAS','DE','FUNDAMENTOS','LA','EN','A','AL','INTRODUCCIÓN','SEMINARIO','TALLER','-','SOCIO-HUM.:']
        cache_found = False

        if self.real_time:
            print("Se está generando el DataFrame en tiempo real, esto puede tomar varios minutos.")
        else:
            try:
                cache = pd.read_excel(self.cache_materias)
                cache_found = True
            except:
                print("No se encontró el archivo de cache, se procederá a generar uno nuevo.")

        if cache_found:
            cache_list = list(cache['Clave'].unique())

            for clave_cache in cache_list:
                if clave_cache in claves:
                    df = pd.concat([df,cache.loc[cache['Clave'] == clave_cache]],axis=0,ignore_index=True)
                    claves.remove(clave_cache)

        if len(claves) != 0:
            buscados = pd.DataFrame()
            # Abrir página de la facultad
            if headless:
                options = Options()
                options.add_argument("--headless")
            else:
                options = Options()

            driver = webdriver.Firefox(options=options)
            driver.get(url)
            time.sleep(1)
            campo_clave = driver.find_element("id","clave")
            buscar = driver.find_element("id","buscar")
            # Iterar entre todas las claves para ir formando el horario
        
            for clave in claves:
                print(f"Buscando clave {clave}...")
                campo_clave.clear()
                campo_clave.send_keys(clave)
                buscar.click()
                page_source = driver.page_source

                soup = BeautifulSoup(page_source, features="lxml")
                nombre_materia = soup.find('div',{"class":"col-10"}).text.split()

                nombre_filtrado = ' '.join((filter(lambda s: s not in palabras_excluidas, nombre_materia)))
                
                nombre_filtrado = ''.join([i for i in nombre_filtrado if not i.isdigit()])
                nombre_filtrado = nombre_filtrado[1:]
                if (":" in nombre_filtrado):
                    nombre_filtrado = nombre_filtrado.split(':')
                    nombre_filtrado = nombre_filtrado[1:]
                    nombre_filtrado = ' '.join(nombre_filtrado)
            
                tables = soup.find_all('table')

                for table in tables:
                    nombre_tabla = table.find('tbody').find('tr').find('th').text  
                    #print(nombre_tabla)  

                    if nombre_tabla == "GRUPOS SIN VACANTES":
                        if len(tables) == 1:
                            if(self.real_time):
                                raise Exception("Ya no hay grupos disponibles para la materia " + nombre_filtrado + ". Intenta con otras claves.") 
                            #print("No hay grupos disponibles para la materia " + nombre_filtrado)
                        else:
                            continue

                    primera_clave = table.find_all('tbody')[1].find('tr').find('td').text
                    if int(primera_clave) > 5000:
                        nombre_filtrado = "L." + nombre_filtrado  
                        #print("Laboratorio")  

                    opciones = pd.read_html(StringIO(str(table)))[0]
                    opciones[('AUX','Nombre')] = [nombre_filtrado for _ in range(len(opciones))]
                    buscados = pd.concat([buscados,opciones],axis=0,ignore_index=True)
            driver.quit()
            buscados.columns = [col [1] for col in buscados.columns]
            df = pd.concat([df,buscados],axis=0,ignore_index=True)
        self.claves_mat = list(df['Clave'].unique())
        new_cache = pd.merge(df,cache,how='outer')
        new_cache.to_excel(self.cache_materias, index=False) 
        self._df_grupos = df
        print("Información obtenida. Generando horarios...")



class Generador:

    def __init__(self, materias : Materias, df = None):
        self.materias = materias
        self.claves = materias.claves_mat
        self._lista_horarios = list()
        self.combinaciones = 0
        self.grupos_per_materia = None
        self.df = df
        self._generate()


    @property
    def lista_horarios(self):
        return self._lista_horarios
    

    def _ordenarDataFrame(self,df):
        renglones_por_clv = df.groupby('Clave').size().reset_index(name = 'Opciones')
        df_ordenado = df.merge(renglones_por_clv, on = 'Clave').sort_values(['Opciones','Clave'],ascending = False)
        df_ordenado = df_ordenado.reset_index(drop=True)
        return df_ordenado
 

    #Verificación por horario
    def _hayTraslapeHoras(self,a,b): #DataFrame, comparativa a comparativa b
        if b.Inicio_min - a.Inicio_min == 0: #empiezan a la misma hora
            return True
        if b.Inicio_min - a.Inicio_min > 0: #b empieza después que a
            if(b.Inicio_min - a.Inicio_min < a.Duracion*60):
                return True
        else:
            if(abs(b.Inicio_min - a.Inicio_min) < b.Duracion*60):
                return True 
        return False
        

    def _noHayTraslapeDias(self,horario_actual,materia):    
        """
        Verifica si existe un Traslape entre un potencial horario_actual y una materia (renglón del dataframe)

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
                    if(self._hayTraslapeHoras(horario_actual.iloc[i],grupo)):
                        return False
        return True
    
    # def _actualizarBarra(self,horario):

    #     #temp = horario.set_index('Gpo', inplace=True)

    #     #print(str(temp))

    #     grupos_actuales = horario[~horario.Clave.duplicated(keep='first')]

    #     #print(str(~horario.index.duplicated(keep='first')))
            
    #     # Convert the 'value' column to a list
    #     n = grupos_actuales['Gpo'].tolist()
    #     z = grupos_per_materia_global['Cantidad'].tolist()

    #     #print(str(n))
    #     #print(str(z))
        
    #     n.reverse()
    #     z.reverse()
    #     v = []
    #     v_i = 1
    #     for i in range(len(z)):
    #         v.append(v_i)
    #         v_i *= z[i]

    #     #El id se calcula como una combinación lineal de los grupos totales de las materias y
    #     #los del horario creado
    #     id=0
    #     for i in range(len(n)):
    #         if i != 0:
    #             id += (n[i]-1)*v[i]
    #         else:
    #             id += n[i]*v[i]

    #     #print("ID: " + str(id))
    #     porcentaje = (id/combinaciones)*100
    #     progress_bar.n = porcentaje 
    #     progress_bar.refresh()
        
    def _combinarMaterias(self,horario,materia_actual):
        """
        Es una función recursiva que toma los parámetros para ir concatenando un horario
        Parameters
        ------------
            horario: dataFrame
                El horario que se va formando
            materia_actual: int
                La materia del renglón del df que se concatena
        
        """
        if len(horario.Clave.unique())==len(self.claves) or materia_actual in horario.Clave:
            return
        #Obtiene los grupos de la materia actual y los convierte en un arreglo de enteros
        grupos = self.df.loc[self.df["Clave"] == materia_actual].Gpo.unique().tolist()
        for grupo_actual in grupos:
            #Obtiene un df que contiene todas las filas de un grupo
            new_rows = self.df.loc[(self.df["Clave"]==materia_actual) & (self.df["Gpo"]==grupo_actual)]
            #Esta row puede ser multiple dado que algunos grupos se descomponen así
            if self._noHayTraslapeDias(horario,new_rows):
                temp = horario
                horario = pd.concat([horario, new_rows])
                if len(horario.Clave.unique()) == len(self.claves): #Si ya no hay más materias por agregar
                    self._lista_horarios.append(horario)
                    #print("Horario agregado: " + str(horario))
                    #actualizarBarra(horario)
                else:
                    siguiente_mat_ind = self.claves.index(materia_actual) + 1
                    self._combinarMaterias(horario,self.claves[siguiente_mat_ind])
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

    def _includes(self,horario,materia):
        for i in range(0,len(horario)): #Checa con todas las materias del horario
            if (materia.Gpo == horario.iloc[i].Gpo and materia.Clave == horario.iloc[i].Clave):
                return True
        return False

    def _plotMateria(self,df,gnt):
        import random
        R = random.uniform(0.3,0.75)
        G = random.uniform(0, 0.1)
        B = random.uniform(0.6, 1)
        
        i = 0
        hora = (df.Inicio_min/60)
        duracion = df.Duracion
        
        for cat in df.loc[['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab']]: #Lo que hace es particionar el df a los días de la semana
            if cat == 1:
                #print(df)
                gnt.broken_barh([(i,1)], (hora, duracion) ,facecolors = (R, G, B))
                nombre_materia = df['Nombre'][:9]                                                     #Corta el texto para que quepa en el cuadro
                nombre_profe = df['Profesor'].split(" ")
                nombre_pila = nombre_profe[1]
                nombre_pila = nombre_pila[:5]
                apellido = nombre_profe[-2]
                #nombre_pila = df.Profesor[:7]
                inicial = apellido [:1]
                nombre = nombre_materia + "\n" + str(df['Gpo']) + " " + nombre_pila  + " " + inicial                                    
                gnt.text(i+0.1,hora+1.5,nombre,color="white",fontweight = "bold",fontsize = 8) #x,y,texto,color,grosor y tamaño
            i = i+1


    def _plotHorario(self,horario, numero):
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
            self._plotMateria(horario.iloc[i],gnt)

        os.makedirs("Horarios_generados", exist_ok=True)
        plt.savefig("Horarios_generados" + "/" + self.materias.nombre_horario + str(numero) + ".jpg",dpi = 250)
        plt.close()


    def _imprimirHorarios(self):
        #self.clearCarpeta()
        if len(self._lista_horarios) == 0:
            print("No se puede generar ningún horario con las materias ingresadas.")
            return 0
        n=1
        for horario in self.lista_horarios:
            self._plotHorario(horario,n)
            #print(horario.iloc[:,0:8].drop(['Tipo','Cupo'],axis=1))
            horario.drop(horario.tail(1).index,inplace=True)
            n+=1
            #progress_bar.update(1)
        print(f"Los horarios de {self.materias.nombre_horario} han sido generados.")
        

    #Crea un df vacío con las mismas columnas que el df del excel
    #horario = pd.DataFrame(columns = df.columns)
    #indices_iniciales = df.loc[df[df]]


    def _generate(self,entrada: int = 7, salida: int = 22, clases_sabados: bool = True):
        if self.df != None:
            horario = df.head(0)
            self._combinarMaterias(horario,self.claves[0])
            return
        
        df = self.materias.df_grupos
        df = self._ordenarDataFrame(df)

        #Crea el encabezado de los dummy values de los días (en orden)
        orden = ['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab'] 

        #Obtiene los dummy values directo del df
        dummy_dias = pd.Series(df.Días).str.get_dummies(sep=', ')

        # Reordena y añade los valores de las variables ficticias a la serie "dias" y cambia los NaN por 0
        dummy_dias = dummy_dias.reindex(orden, axis=1).infer_objects(copy=False)

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


        if entrada > 0:
            min_entrada = entrada*60
            if clases_sabados:
                deleted = df.loc[(df['Inicio_min'] < min_entrada) & (df['Sab']==0), :]
            else:
                deleted = df.loc[(df['Inicio_min'] < min_entrada) | (df['Sab'] == 1),:]

            claves_desechadas = deleted.itertuples()
            
            
            for fila in claves_desechadas:
                df.drop(df[(df['Clave'] == fila[1]) & (df['Gpo'] == fila[2])].index,inplace=True)
            df = df.reset_index(drop=True)


        if salida>0:
            #print("Salida: " + str(salida))
            min_salida = salida*60
            if clases_sabados:
                deleted = df.loc[(df['Fin_min'] > min_salida) & (df['Sab']==0),:]
            else:
                deleted = df.loc[(df['Fin_min'] > min_salida) | (df['Sab']==1), :]


            claves_desechadas = deleted.itertuples()
            
            for fila in claves_desechadas:
                df.drop(df[(df['Clave'] == fila[1]) & (df['Gpo'] == fila[2])].index,inplace=True)
            df = df.reset_index(drop=True)
            #print(len(df))

        #Calcula la duración de cada clase en horas
        duracion = df.Fin_min - df.Inicio_min
        df = df.assign(Duracion = duracion/60)

        cantidad_grupos_per_materia = df.groupby('Clave')['Gpo'].size().reset_index(name = 'Cantidad')

    
        # for clave in cantidad_grupos_per_materia:
        #     self.combinaciones = self.combinaciones*clave
        self.df = df
        #print(str(combinaciones))
        #progress_bar = tqdm(total=100, desc='Generando horarios', unit="%")
        horario = df.head(0)
        self._combinarMaterias(horario,self.claves[0])
        self._imprimirHorarios()

        # progress_bar.n = 100
        # progress_bar.refresh()
        # progress_bar.close()
        # #chechar_disponibilidad(lista_horarios,opciones_atractivas)
        # print("Horarios generados: " + str(len(self.lista_horarios)))
        # #print("--- %s seconds ---" % (time.time() - start_time))
        # progress_bar = tqdm(total=len(self.lista_horarios), desc='Creando imágenes', unit="%")
        # self.imprimirHorarios()
        # progress_bar.close()


