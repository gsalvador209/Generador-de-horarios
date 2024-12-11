from Generator import Materias
from Generator import Generador
from Generator import FolderManager


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

    print("\nIngresa la hora de entrada")
    while True:
        entrada = input("Hora de entrada: ")
        if entrada == "":
            entrada = 7
            print("Hora de entrada por defecto: 7")
            break
        elif (entrada.isdigit() and (int(entrada) >= 7 and int(entrada) <= 20)):
            entrada = int(entrada)
            break
        else:
            print("Hora de ingreso no válida")
    
    print("\nIngresa la hora de salida")
    while True:
        salida = input("Hora de salida: ")
        if salida == "":
            salida = 15
            print("Hora de salida por defecto: 15")
            break
        elif (salida.isdigit() and (int(salida) >= 9 and int(salida) <= 22)):
            salida = int(salida)
            break
        else:
            print("Hora de salida no válida")
    
    print("\n¿Desea clases los sábados?")
    while True:
        clases_sabados = str(input("Si o No:"))
        if clases_sabados.lower() in ["si", "s", "y", "yes", "sí","1"]:
            clases_sabados = True
            break
        elif clases_sabados.lower() in ["no", "n","0"]:
            clases_sabados = False
            break
        else:
            print("Respuesta no válida")
    
    print("\nIngresa un nombre para identificar las opciones para este horario")
    while True:
        nombre_horario = input("Nombre: ")
        if nombre_horario == "":
            print("Nombre inválido")
        else:
            nombre_horario = ''.join(e if e.isalnum() else '_' for e in nombre_horario)
            break
    
    configuraciones = [entrada, salida, clases_sabados]

    lista_set_claves.append(claves)
    lista_nombres.append(nombre_horario)
    lista_configuraciones.append(configuraciones)

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

print("\nSe van a generar los horarios")

for i in range(len(lista_set_claves)):
    opcion = Materias(claves_mat=lista_set_claves[i], nombre_horario=lista_nombres[i])  
    entrada = lista_configuraciones[i][0]
    salida = lista_configuraciones[i][1]
    clases_sabados = lista_configuraciones[i][2]
    generador = Generador(materias=opcion, entrada=entrada, salida=salida, clases_sabados=clases_sabados)   

print("Todos los horarios han sido generados")
print("Asegurate de eliminar el archivo cache cuando se publiquen los nuevos horarios") 


fm.abrir_carpeta()

input("Presiona Enter para salir")