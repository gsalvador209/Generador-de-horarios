<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/pandas-1.3%2B-blue?logo=pandas&logoColor=white" alt="pandas">
  <img src="https://img.shields.io/badge/numpy-1.20%2B-blue?logo=numpy&logoColor=white" alt="NumPy">
  <img src="https://img.shields.io/badge/bitarray-2.x-orange?logo=python&logoColor=white" alt="bitarray">
  <img src="https://img.shields.io/badge/matplotlib-3.x-blue?logo=matplotlib&logoColor=white" alt="matplotlib">
  <img src="https://img.shields.io/badge/BeautifulSoup4-4.9%2B-blue?logo=python&logoColor=white" alt="BeautifulSoup4">
  <img src="https://img.shields.io/badge/lxml-4.x-blue?logo=xml&logoColor=white" alt="lxml">
  <img src="https://img.shields.io/badge/Selenium-4.x-green?logo=selenium&logoColor=white" alt="Selenium">
  <img src="https://img.shields.io/badge/openpyxl-3.x-blue?logo=python&logoColor=white" alt="openpyxl">
  <img src="https://img.shields.io/badge/Tkinter-8.x-blue?logo=python&logoColor=white" alt="Tkinter">
</p>

<h1 align="center">📚 Generador de Horarios</h1>

## 🌟 Descripción

Generador de Horarios es una herramienta en Python diseñada para automatizar y optimizar la generación de todas las combinaciones posibles de horarios de materias para inscripciones en la Facultad de Ingeniería de la UNAM. Con un algoritmo de backtracking basado en representación bitwise, este proyecto permite recorrer eficientemente todas las opciones viables según las claves de materias y bloques de tiempo definidos por el usuario.

### ✨ Beneficios clave:

- Ahorra horas de trabajo manual en revisar compatibilidad entre grupos.
- Ofrece visualización profesional de cada resultado en gráficos tipo Gantt.
- Se adapta a diferentes sistemas operativos y aprovecha caché cuando es posible.

### 🛠 Tecnologías Utilizadas

- <img src="https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white" alt="Python" width="80"/> **Python 3.8+**  
  Lenguaje principal para lógica, scraping y backtracking.

- <img src="https://img.shields.io/badge/pandas-1.3%2B-blue?logo=pandas&logoColor=white" alt="pandas" width="80"/> **pandas**  
  Manejo de DataFrames y procesamiento de tablas de horarios.

- <img src="https://img.shields.io/badge/numpy-1.20%2B-blue?logo=numpy&logoColor=white" alt="NumPy" width="80"/> **NumPy**  
  Operaciones numéricas y creación de arreglos para bitarrays.

- <img src="https://img.shields.io/badge/bitarray-2.x-orange?logo=python&logoColor=white" alt="bitarray" width="80"/> **bitarray**  
  Representación compacta de disponibilidad en bloques de 30 minutos.

- <img src="https://img.shields.io/badge/matplotlib-3.x-blue?logo=matplotlib&logoColor=white" alt="matplotlib" width="80"/> **matplotlib**  
  Generación de gráficos tipo Gantt para visualizar horarios.

- <img src="https://img.shields.io/badge/BeautifulSoup4-4.9%2B-blue?logo=python&logoColor=white" alt="BeautifulSoup4" width="80"/> **BeautifulSoup4**  
  Parseo y extracción de datos HTML de la web de horarios.

- <img src="https://img.shields.io/badge/lxml-4.x-blue?logo=xml&logoColor=white" alt="lxml" width="80"/> **lxml**  
  Soporte para procesamiento rápido de XML/HTML junto a BeautifulSoup4.

- <img src="https://img.shields.io/badge/Selenium-4.x-green?logo=selenium&logoColor=white" alt="Selenium" width="80"/> **Selenium (Firefox WebDriver)**  
  Automatización de la navegación para obtener datos en tiempo real.

- <img src="https://img.shields.io/badge/openpyxl-3.x-blue?logo=python&logoColor=white" alt="openpyxl" width="80"/> **openpyxl**  
  Lectura y escritura de archivos Excel para cache de planes de estudio.

- <img src="https://img.shields.io/badge/Tkinter-8.x-blue?logo=python&logoColor=white" alt="Tkinter" width="80"/> **Tkinter**  
  Interfaz gráfica para ingresar claves y definir bloques de indisponibilidad.


### 🔧 Instalación y Uso

1. Clonar el repositorio o descargarlo en formato .zip y extraerlo.
2. Crear un entorno virtual (recomendado) e instalar dependencias:
   `python -m venv venv`
   `source venv/bin/activate   # En Windows: venv\\Scripts\\activate`
   `pip install -r requirements.txt`
3. Configurar claves de materias:
4. Ejecutar Visualizador.py para acceder a la interfaz gráfica.
5. Agregar hasta 8 claves de materias y seleccionar bloques de indisponibilidad.
6. Hacer clic en "Generar" para guardar las selecciones.

**Generar horarios:**

1. Ejecutar `execute_code.bat` y monitorear en consola el proceso de búsqueda y generación.
2. Los archivos .jpg se guardarán en la carpeta Horarios_generados, cada uno con un nombre descriptivo.

> 🚀 Para usar datos en tiempo real (sin cache), ajusta real_time=True al instanciar la clase Materias en Generator.py.

### 🔍 Detalles Técnicos del Algoritmo de Backtracking

##### Recolección de datos:

1. La clase Materias lee las claves desde claves.pkl y utiliza Selenium (Firefox WebDriver) para acceder a [la página de horarios de la Facultad](https://www.ssa.ingenieria.unam.mx/horarios.html).
Con BeautifulSoup4 y lxml, parsea las tablas HTML de grupos y sus horarios.
2. Filtra información (sin vacantes, nombres completos y abreviados) y genera un DataFrame.
3. Cada grupo crea una matriz de bits (bitarray) de tamaño 30×6 (bloques de 30 min × 6 días) donde un 1 indica ocupación.

Preparación del DataFrame:

1. Se calcula el número de opciones por materia y se ordena de menor a mayor para **pruning**.
2. Se descartan grupos que colapsan con la indisponibilidad del usuario mediante operación bitwise AND entre el Binary del grupo y el indisp.

Backtracking recursivo (`_combinarMaterias`):
1. Parte con un DataFrame vacío (horario) y la primera materia.
2. Para cada grupo disponible de la materia actual:
3. Verifica compatibilidad con el horario actual operación bitwise AND vs OR para hacerlo muy eficiente.
4. Si no hay traslapes, agrega el grupo temporalmente al horario.
5. Si el total de materias coincide con el número de claves, almacena el horario en la lista de soluciones. Sino, llama recursivamente con la siguiente materia.

Visualización de horarios:

1. Crea un gráfico tipo Gantt con matplotlib (eje X: días; eje Y: horas 7:00–22:30).
2. Asigna colores aleatorios para cada materia/grupo.
3. Agrega etiquetas con nombre abreviado, grupo y profesor.
4. Guarda cada gráfico en Horarios_generados.

Optimización y eficiencia:

La representación por bitarray permite comprobaciones de compatibilidad en O(1) para cada bloque.
El ordenamiento previo reduce drásticamente ramas de exploración
El cache en cache_materias.xlsx acelera la construcción del DataFrame cuando no se requiere recarga de información.

### ⚠️ Advertencias
-El algoritmo genera todas las combinaciones posibles, por lo que muchas materias o grupos pueden hacer que el proceso se prolongue varios minutos.
-El cache se guarda en cache_materias.xlsx. Si hay nuevos horarios disponibles en la página de la Facultad, elimina este archivo para evitar usar datos desactualizados.
-Si la estructura web de la página de horarios cambia, el script no podrá extraer datos correctamente.

### 🌈 Características Destacadas

✅ Bitarray eficiente: Representación de disponibilidad con bloques de 30 minutoss×6 días, permitiendo operaciones bitwise.
✅ Ordenamiento inteligente: Priorización de materias con menos opciones para pruning temprano.
✅ Interfaz gráfica amigable: tkinter para ingresar claves y definir indisponibilidades de manera visual.
✅ Visualización profesional: Gráficos Gantt con colores y etiquetas legibles.
✅ Cache dinámico: Almacenamiento en cache_materias.xlsx para reducir tiempos de petición.
✅ Multiplataforma: Detecta el sistema operativo (Windows, macOS, Linux) para abrir carpetas y ejecutar scripts.

### 📸 Capturas de Pantalla
![Noveno_y_decimo_con_clases_sabado_6](https://github.com/user-attachments/assets/8a9036be-ffed-4432-bf57-7137bea8a704)
![Registro de claves](https://github.com/user-attachments/assets/9ba3647a-04f4-4e89-974d-2661bef35fd5)
![Interfaz de indisponibilidad](https://github.com/user-attachments/assets/baa303b0-0a72-422e-ad41-41a31c823b60)

🚀 Implementaciones a Futuro

🔹 Bloques prioritarios: Definir franjas horarias con mayor prioridad.
🔹 Generación en tiempo real: Actualización automática al publicarse nuevos horarios.
🔹 Caché dinámico: manejo inteligente y automático del caché para actualización automática.
🔹 Barra de progreso: Indicador visual durante el backtracking.
🔹 Selección de grupos preferidos: Permitir indicar grupos favoritos por materia.
🔹 Notificaciones: Alertar al usuario al concluir la generación.
🔹 Exportar a PDF/calendarios: Integrar con calendarios externos o generar PDFs.

`Hecho con ❤️ para mejorar tu experiencia universitaria y ahorrar tiempo en la creación de horarios.`


