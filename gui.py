import tkinter as tk
from tkinter import ttk


def crear_interfaz():
    # Crear la ventana principal
    root = tk.Tk()
    root.title("Horario Semanal")

    # Crear un frame para el horario
    frame_horario = ttk.Frame(root, padding="10")
    frame_horario.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    # Crear un frame para los campos de texto y el botón
    frame_campos = ttk.Frame(root, padding="10")
    frame_campos.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

    # Definir los días y las horas
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
    horas = ["{:02d}:{:02d}".format(h, m) for h in range(7, 22) for m in (0, 30)]

    # Crear etiquetas para los días
    for col, dia in enumerate(dias):
        label = ttk.Label(frame_horario, text=dia)
        label.grid(row=0, column=col+1)

    # Crear etiquetas para las horas
    for row, hora in enumerate(horas):
        label = ttk.Label(frame_horario, text=hora)
        label.grid(row=row+1, column=0)

    # Variable para almacenar el estado inicial al hacer clic
    initial_state = None

    # Función para cambiar el color del fondo al hacer clic
    def toggle_color(event):
        nonlocal initial_state
        widget = event.widget
        initial_state = widget.cget("background")
        new_color = "blue" if initial_state == "white" else "white"
        widget.config(background=new_color)

    # Función para cambiar el color del fondo al arrastrar el mouse
    def toggle_color_drag(event):
        nonlocal initial_state
        widget = root.winfo_containing(event.x_root, event.y_root)
        if widget and isinstance(widget, tk.Label) and widget != frame_horario:
            current_color = widget.cget("background")
            new_color = "blue" if initial_state == "white" else "white"
            widget.config(background=new_color)

    # Crear los campos para el horario
    horario_labels = []
    for row in range(1, len(horas) + 1):
        row_labels = []
        for col in range(1, len(dias) + 1):
            label = tk.Label(frame_horario, width=10, background="white", borderwidth=1, relief="solid")
            label.grid(row=row, column=col, sticky="nsew")
            label.bind("<Button-1>", toggle_color)
            label.bind("<B1-Motion>", toggle_color_drag)
            row_labels.append(label)
        horario_labels.append(row_labels)

    # Ajustar la disposición de la ventana
    for col in range(len(dias) + 1):
        frame_horario.grid_columnconfigure(col, weight=1)
    for row in range(len(horas) + 1):
        frame_horario.grid_rowconfigure(row, weight=1)

    # Variable para contar los campos de texto creados
    contador_campos = 0
    campos_texto = []

    # Función para crear un nuevo campo de texto
    def crear_campo():
        nonlocal contador_campos
        if contador_campos < 7:
            entry = ttk.Entry(frame_campos)
            entry.grid(row=contador_campos, column=0, pady=5)
            campos_texto.append(entry)
            contador_campos += 1
            if contador_campos >= 7:
                boton_crear.grid_forget()  # Ocultar el botón "Agregar Campo"
            else:
                boton_crear.grid(row=contador_campos, column=0, pady=5)

    # Crear el botón "Agregar Campo"
    boton_crear = ttk.Button(frame_campos, text="Agregar Campo", command=crear_campo)
    boton_crear.grid(row=contador_campos, column=0, pady=5)

    # Variables para almacenar los resultados
    matriz_resultado = None
    numeros_ingresados = None

    # Función para generar la matriz y la lista
    def generar():
        nonlocal matriz_resultado, numeros_ingresados
        matriz = []
        for row_labels in horario_labels:
            row = [1 if label.cget("background") == "blue" else 0 for label in row_labels]
            matriz.append(row)

        numeros_ingresados = [entry.get() for entry in campos_texto if entry.get().isdigit()]

        matriz_resultado = matriz
        root.quit()  # Cerrar la ventana

    # Crear el botón "Generar" en la esquina inferior derecha
    boton_generar = ttk.Button(frame_campos, text="Generar", command=generar)
    boton_generar.grid(row=8, column=0, pady=10, sticky=tk.SE)

    # Iniciar el bucle de la aplicación
    root.mainloop()

    return matriz_resultado, numeros_ingresados

# Llamar a la función y obtener los resultados
matriz, seleccionados = crear_interfaz()

# Imprimir los resultados
print("Matriz Binaria 30x6:")
for row in matriz:
    print(row)

print("Números ingresados:")
print(seleccionados)
