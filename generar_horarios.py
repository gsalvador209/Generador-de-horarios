from Generator import Materias
from Generator import Generador
from Generator import FolderManager

fm = FolderManager()
fm.clear_carpeta()

materias = Materias(claves_mat=[1959,2929,2933,2931],nombre_horario="Bases_distruibuidas",silence=False,real_time=False)
generador = Generador(materias)

materias = Materias(claves_mat=[1959,2929,2933,757],nombre_horario="Patrones",silence=False,real_time=False)
generador = Generador(materias)

materias = Materias(claves_mat=[1959,2929,2933,2946],nombre_horario="Cliente-Serv",silence=False,real_time=False)
generador = Generador(materias)

materias = Materias(claves_mat=[1959,2929,2933,1916],nombre_horario="PDImgs",silence=False,real_time=False)
generador = Generador(materias)

fm.abrir_carpeta()