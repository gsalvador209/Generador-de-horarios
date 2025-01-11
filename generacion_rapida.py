from Generator import Materias
from Generator import Generador
from Generator import FolderManager
from Visualizador import GUI
import tkinter as tk


fm = FolderManager()
fm.clear_carpeta()

root = tk.Tk()
agenda = GUI(root)
root.mainloop()

#Materias obligatorias
# Sistemas distribuidos: 1959, 8 creditos

#Materias opativas
# Cómputo Móvil: 674, 6 creditos
# Bases de datos avanzadas: 2929, 8 creditos
# Seguridad Informática Avanzada: 2954, 8 creditos
# Negocios Electronicos y Desarrollo Web: 2931, 8 creditos

# Arq. Cliente Servidor: 2946, 6 creditos
# Bases de Datos Distribuidas: 2947, 8 creditos
# Física cuántica: 2949, 8 creditos
# Procesamiento digital de imágenes: 1916, 8 creditos
# Reconocimeinto de patrones: 757, 6 creditos
# Minería de Datos: 2933, 8 creditos

materias = Materias(claves_mat=[1959, 674, 2929, 2946],nombre_horario="Sugerencias_GPT")
generador = Generador(materias,indisponibilidad=agenda.selected_blocks)

# materias = Materias(claves_mat=[1959,2929,2933,1916],nombre_horario="PDImgs")
# generador = Generador(materias, salida = 18, clases_sabados= False)

fm.abrir_carpeta()