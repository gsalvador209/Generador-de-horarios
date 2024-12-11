import tkinter as tk
from tkinter import ttk

def pintar_horario(matriz):
    # Crear la ventana principal
    root = tk.Tk()
    root.title("Horario Semanal - Pintar")

    # Crear un frame para el horario
    frame_horario = ttk.Frame(root, padding="10")
    frame_horario.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

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

    # Crear los campos para el horario y actualizar el color según la matriz
    horario_labels = []
    for row in range(1, len(horas) + 1):
        row_labels = []
        for col in range(1, len(dias) + 1):
            label = tk.Label(frame_horario, width=10, background="white", borderwidth=1, relief="solid")
            label.grid(row=row, column=col, sticky="nsew")
            if matriz[row-1][col-1] == 1:
                label.config(background="blue")
            row_labels.append(label)
        horario_labels.append(row_labels)

    # Ajustar la disposición de la ventana
    for col in range(len(dias) + 1):
        frame_horario.grid_columnconfigure(col, weight=1)
    for row in range(len(horas) + 1):
        frame_horario.grid_rowconfigure(row, weight=1)

    # Iniciar el bucle de la aplicación
    root.mainloop()

# Ejemplo de uso
matriz_ejemplo = [[0, 1, 0, 1, 0, 1],
                  [1, 0, 1, 0, 1, 0],
                  [0, 1, 0, 1, 0, 1],
                  [1, 0, 1, 0, 1, 0],
                  [0, 1, 0, 1, 0, 1],
                  [1, 0, 1, 0, 1, 0],
                  [0, 1, 0, 1, 0, 1],
                  [1, 0, 1, 0, 1, 0],
                  [0, 1, 0, 1, 0, 1],
                  [1, 0, 1, 0, 1, 0],
                  [0, 1, 0, 1, 0, 1],
                  [1, 0, 1, 0, 1, 0],
                  [0, 1, 0, 1, 0, 1],
                  [1, 0, 1, 0, 1, 0],
                  [0, 1, 0, 1, 0, 1],
                  [1, 0, 1, 0, 1, 0],
                  [0, 1, 0, 1, 0, 1],
                  [1, 0, 1, 0, 1, 0],
                  [0, 1, 0, 1, 0, 1],
                  [1, 0, 1, 0, 1, 0],
                  [0, 1, 0, 1, 0, 1],
                  [1, 0, 1, 0, 1, 0],
                  [0, 1, 0, 1, 0, 1],
                  [1, 0, 1, 0, 1, 0],
                  [0, 1, 0, 1, 0, 1],
                  [1, 0, 1, 0, 1, 0],
                  [0, 1, 0, 1, 0, 1],
                  [1, 0, 1, 0, 1, 0],
                  [0, 1, 0, 1, 0, 1],
                  [1, 0, 1, 0, 1, 0],
                  [0, 1, 0, 1, 0, 1],
                  [1, 0, 1, 0, 1, 0],
                  [0, 1, 0, 1, 0, 1]]

pintar_horario(matriz_ejemplo)
