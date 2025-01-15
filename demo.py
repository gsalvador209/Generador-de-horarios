from Generator import Generador
from Generator import FolderManager
from Visualizador import GUI

"""
TODO:
- Hacer pruebas sin archivos iniciales
"""


app = GUI()
app.mainloop()

fm = FolderManager()
fm.clear_carpeta()

print("Generando horarios...")

generador = Generador()   
generador.generar_horarios()

print("Todos los horarios han sido generados")
print("Asegurate de eliminar el archivo cache cuando se publiquen los nuevos horarios") 


fm.abrir_carpeta()
