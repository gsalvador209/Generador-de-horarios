import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import subprocess
import time
import sys
import os, shutil
from bs4 import BeautifulSoup
from bitarray import bitarray
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from io import StringIO
from datetime import datetime

# TODO:
#   - Implementar la GUI para la selección de materias
#   - Implementar la impresion de horarios en la GUI
#   - Implementación y pruebas en tiempo real
#   - Agregar barra de progreso para el generador
#   - Agregar modo grupos preferidos por materia

class FolderManager:
    #Se obtiene la carpeta actual
    def __init__(self):
        self.current_folder = os.getcwd()

    def abrir_carpeta(self,ruta="Horarios_generados"):
        ruta = os.path.join(self.current_folder,ruta)
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
        folder = os.path.join(self.current_folder,"Horarios_generados")
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

    def __init__(self, claves_mat: list, nombre_horario : str = "Opciones",df_grupos = None, real_time = False, silence = True):
        self.nombre_horario = nombre_horario
        self.claves_mat = claves_mat
        self._df_grupos = df_grupos
        self.real_time = real_time
        self.silence = silence
        self._gen_df(self.silence)

    @property
    def df_grupos(self):
        return self._df_grupos

    def _crear_matriz(self,dias_str, horas_str):
        """
        A partir de un horario con formato "Lun, Vie" y "07:00 a 09:00" crea una matriz de bits
        que representa la indisponibilidad en agenda.

        ### Parámetros
        - dias_str: str, días de la semana en formato "Dia, Dia"
        - horas_str: str, horas en formato "HH:MM a HH:MM"

        ### Retorno
        - bit_matrix: bitarray, matriz de bits que representa la disponibilidad en agenda
        """
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

    def _gen_df(self, headless = True):
        """
        Genera el DataFrame con la información de las materias que se van a considerar para la generación de horarios.
        """

        df = pd.DataFrame()
        claves = self.claves_mat
        claves_to_remove = []
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
                try:
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
                except AttributeError:
                    print(f"No fue posible encontrar algúna asignatura con clave {clave}. Se ignorará esta clave.")
                    claves_to_remove.append(clave) #Aun no se usa

            driver.quit()
            buscados.columns = [col [1] for col in buscados.columns]
            df = pd.concat([df,buscados],axis=0,ignore_index=True)

        if cache_found:
            new_cache = pd.merge(df,cache,how='outer')
            new_cache.to_excel(self.cache_materias, index=False)
        else:
            df.to_excel(self.cache_materias, index=False)

        self.claves_mat = list(df['Clave'].unique())

        df['Binary'] = df.apply(lambda row: self._crear_matriz(row['Días'], row['Horario']), axis=1)

        self._df_grupos = df
        print("Información obtenida. Generando horarios...")



class Generador:

    def __init__(self, materias : Materias, df = None, indisponibilidad = bitarray(30*6)):
        self.materias = materias
        self.claves = materias.claves_mat
        self._lista_horarios = list()
        self.combinaciones = 0
        self.grupos_per_materia = None
        self.df = df
        self.indisp = indisponibilidad
        self._generate()

    @property
    def lista_horarios(self):
        return self._lista_horarios


    def _ordenarDataFrame(self,df):
        renglones_por_clv = df.groupby('Clave').size().reset_index(name = 'Opciones')
        df_ordenado = df.merge(renglones_por_clv, on = 'Clave').sort_values(['Opciones','Clave'],ascending = False)
        df_ordenado = df_ordenado.reset_index(drop=True)
        return df_ordenado



    # #Verificación por horario
    # def _hayTraslapeHoras(self,a,b): #DataFrame, comparativa a comparativa b
    #     if b.Inicio_min - a.Inicio_min == 0: #empiezan a la misma hora
    #         return True
    #     if b.Inicio_min - a.Inicio_min > 0: #b empieza después que a
    #         if(b.Inicio_min - a.Inicio_min < a.Duracion*60):
    #             return True
    #     else:
    #         if(abs(b.Inicio_min - a.Inicio_min) < b.Duracion*60):
    #             return True
    #     return False


    def _noTraslape(self,horario_armandose,rows_materia):
        horario_bin = bitarray(30*6)
        horario_bin.setall(0)
        materia_bin = bitarray(30*6)
        materia_bin.setall(0)

        for row in horario_armandose.itertuples():
            horario_bin = horario_bin | row.Binary

        for row in rows_materia.itertuples():
            materia_bin = materia_bin | row.Binary

        return not (horario_bin & materia_bin).any()

    # def _noHayTraslapeDias(self,horario_actual,materia):
    #     """
    #     Verifica si existe un Traslape entre un potencial horario_actual y una materia (renglón del dataframe)

    #     Parameters
    #     ----------
    #         horario_actual: dataFrame
    #             Es el horario_actual que se va armando
    #         materia: series
    #             Es la fila que contiene toda la info de la materia que se quiere meter
    #     """
    #     orden = ['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab']
    #     for i in range(len(horario_actual)):
    #         for j in range(len(materia)):
    #             grupo = materia.iloc[j]
    #             prod = horario_actual.iloc[i].loc[orden] * grupo.loc[orden]
    #             #Ejecuta la funcion all para ver si todos los elementos son cero
    #             if(not (prod == 0).all()):
    #                 if(self._hayTraslapeHoras(horario_actual.iloc[i],grupo)):
    #                     return False
    #     return True


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
            if self._noTraslape(horario,new_rows):
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


    def _plotMateria(self,gpo_materia,gnt):
        import random
        R = random.uniform(0.3,0.75)
        G = random.uniform(0, 0.1)
        B = random.uniform(0.6, 1)

        i = 0
        ba = gpo_materia.Binary

        dias = [any(ba[row * 6 + col] for row in range(30)) for col in range(6)]
 
        for i,val in enumerate(dias): #Lo que hace es particionar el df a los días de la semana
            if val:
                duracion = 0#sum(ba[row * 6 + i] for row in range(30))/2
                hora = -1
                for row in range(30):
                    if ba[row * 6 + i] == 1:
                        # Count the number of zeros before the first 1
                        if hora == -1:
                            hora = row  # The number of zeros is the row index
                        duracion += 1
                
                duracion /= 2
                hora = 7 + hora / 2        
                   
                #print(df)
                gnt.broken_barh([(i,1)], (hora, duracion) ,facecolors = (R, G, B))
                nombre_materia = gpo_materia['Nombre'][:9]                                                     #Corta el texto para que quepa en el cuadro
                nombre_profe = gpo_materia['Profesor'].split(" ")
                nombre_pila = nombre_profe[1]
                nombre_pila = nombre_pila[:5]
                apellido = nombre_profe[-2]
                #nombre_pila = df.Profesor[:7]
                inicial = apellido [:1]
                nombre = nombre_materia + "\n" + str(gpo_materia['Gpo']) + " " + nombre_pila  + " " + inicial
                gnt.text(i+0.1,hora+1.5,nombre,color="white",fontweight = "bold",fontsize = 8) #x,y,texto,color,grosor y tamaño


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
        ruta = os.path.join(os.getcwd(),"Horarios_generados")
        plt.savefig(ruta + "/" + self.materias.nombre_horario + "_" +str(numero) + ".jpg",dpi = 250)
        plt.close()


    def _imprimirHorarios(self):
        #self.clearCarpeta()
        print(f"Los horarios de {self.materias.nombre_horario} han sido creados, se están guardando en la carpeta Horarios_generados")
        if len(self._lista_horarios) == 0:
            print(f"No se puede generar ningún horario en {self.materias.nombre_horario} con las materias ingresadas.")
            return 0
        else:
            print(f"Se generaron {len(self._lista_horarios)} horarios. Imprimiendo horarios...")
        n=1
        for horario in self.lista_horarios:
            self._plotHorario(horario,n)
            #print(horario.iloc[:,0:8].drop(['Tipo','Cupo'],axis=1))
            horario.drop(horario.tail(1).index,inplace=True)
            n+=1
            #progress_bar.update(1)
        print(f"Los horarios de {self.materias.nombre_horario} han sido generados.")

    def _compatibilidad(self,A,B):
        return not (A & B).any()



    def _generate(self):
        if self.df != None:
            horario = df.head(0)
            self._combinarMaterias(horario,self.claves[0])
            return

        df = self.materias.df_grupos
        df = self._ordenarDataFrame(df)

        df = df[df.apply(lambda row: self._compatibilidad(self.indisp,row.Binary), axis=1)]
        df = df.reset_index(drop=True)

        self.df = df
        horario = df.head(0)
        self._combinarMaterias(horario,self.claves[0])
        self._imprimirHorarios()




