from Generator import Materias
from Generator import Generador
from Generator import FolderManager
from Visualizador import GUI
import tkinter as tk


fm = FolderManager()

print("Generador de horarios")

lista_set_claves = []
lista_nombres = []
lista_configuraciones = []
flag = True

while flag:
    print("\nIngrese las claves de las materias que desea cursar")
    print("Para finalizar, presiona únicamente Enter")
    claves = []
    while True:
        clave = input("Clave de materia: ")
        if clave == "":
            break
        elif (clave.isdigit() and (len(clave) == 4 or len(clave) == 3)):
            claves.append(int(clave))
        else:
            print("Clave inválida")
    if len(claves) == 0:
        break

    print("\nIngresa un nombre para identificar las opciones para este horario")
    while True:
        nombre_horario = input("Nombre: ")
        if nombre_horario == "":
            print("Nombre inválido")
        else:
            nombre_horario = ''.join(e if e.isalnum() else '_' for e in nombre_horario)
            break
    

    lista_set_claves.append(claves)
    lista_nombres.append(nombre_horario)

    print("\nOpciones guardadas")
    print("\n¿Deseas generar otro horario?")
    while True:
        respuesta = str(input("Si o No: "))
        if respuesta.lower() in ["si", "s", "y", "yes", "sí","1"]:
            break
        elif respuesta.lower() in ["no", "n","0"]:
            flag = False
            break
        else:
            print("Respuesta no válida")   

fm.clear_carpeta()

print("\nSelecciona los bloques de tiempo en los que sin disponibilidad de tiempo en la ventana emergente")
root = tk.Tk()
agenda = GUI(root)
root.mainloop()


for i in range(len(lista_set_claves)):
    opcion = Materias(claves_mat=lista_set_claves[i], nombre_horario=lista_nombres[i])  
    generador = Generador(materias=opcion, indisponibilidad=agenda.selected_blocks)   

print("Todos los horarios han sido generados")
print("Asegurate de eliminar el archivo cache cuando se publiquen los nuevos horarios") 


fm.abrir_carpeta()

input("Presiona Enter para salir")