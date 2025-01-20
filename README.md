# Generador de horarios
Este código escrito puramente en Python pretende sustituir la ardua tarea de estar pensando que materias son compatibles entre sí al generar **todas los horarios posibles** ante un grupo de materias y rango de horario dado para las inscripciones de la Facultad de Ingeniería. Esto es útil para visualizar de manera rápida cuales son las posibles opciones que pueden inscribirse en el semestre.

## Requisitos
Es necesaria la instalación de Python3 y las siguientes bibliotecas:
1. pandas
2. matplotlib
3. BeautifulSoup4
4. selenium
5. lmxl
6. openpyxl
7. bitarray   

## Instalación y uso en Windows
1. Clonar el repositorio o descargarlo en `.zip` y extraerlo
2. Ejecutar el archivo `setup_project.bat` o crear un ambiente virtual e instalar las bibliotecas mencionadas con `pip`
3. Ejecutar el archivo  `execute_code.bat` o ejecutar manualmente `demo.py` desde el ambiente virual

## Advertencias
- El código genera realiza todas las combinaciones posibles con un algoritmo de backtracking, por lo que ingresar muchas materias con muchos grupos puede tomar muchos minutos en generar todas las posibilidad. **Se recomienda altamente restringir el rango de entrada y salida** o no incluir materias con demasiados grupos.
- El código almacena las búsquedas en un archivo caché que ==se debe eliminar tras la nueva publicación de horarios==, de lo contrario se tiene información desactualizada.
- Dado que se obtiene la información de la [página de la facultad](https://www.ssa.ingenieria.unam.mx/horarios.html), en caso de que esta cambie su estructura, el código no podrá buscar las materias

## Implementaciones a futuro
   - Implementación y pruebas en tiempo real
   - Agregar barra de progreso para el generador
   - Agregar blacklist de grupos

## Capturas de horario generado
![Noveno_y_decimo_con_clases_sabado_6](https://github.com/user-attachments/assets/8a9036be-ffed-4432-bf57-7137bea8a704)
![Registro de claves](https://github.com/user-attachments/assets/9ba3647a-04f4-4e89-974d-2661bef35fd5)
![Interfaz de indisponibilidad](https://github.com/user-attachments/assets/baa303b0-0a72-422e-ad41-41a31c823b60)



