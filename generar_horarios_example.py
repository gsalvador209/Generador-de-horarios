from Generator import Materias
from Generator import Generador
from Generator import FolderManager

fm = FolderManager()
fm.clear_carpeta()

materias = Materias(claves_mat=[1959,2929,2933,2931],nombre_horario="Bases_distruibuidas")
generador = Generador(materias)

materias = Materias(claves_mat=[1959,2929,2933,757],nombre_horario="Patrones")
generador = Generador(materias, clases_sabados= False)

materias = Materias(claves_mat=[1959,2929,2933,2946],nombre_horario="Cliente-Serv")
generador = Generador(materias, entrada = 9)

materias = Materias(claves_mat=[1959,2929,2933,1916],nombre_horario="PDImgs")
generador = Generador(materias, salida = 18, clases_sabados= False)

fm.abrir_carpeta()