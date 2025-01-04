import tkinter as tk
from bitarray import bitarray
import pandas as pd
import numpy as np
from datetime import datetime


def check_compatibility(A,B):
    return not (A & B).any()

def create_matrix(dias_str, horas_str):
    """
    A partir de un horario con formato "Lun, Vie" y "07:00 a 09:00" crea una matriz de bits
    que representa la indisponibilidad en agenda.
    
    ### Parámetros
    - dias_str: str, días de la semana en formato "Dia, Dia"
    - horas_str: str, horas en formato "HH:MM a HH:MM"

    ### Retorno
    - bit_matrix: bitarray, matriz de bits que representa la disponibilidad en agenda
    """
    orden = ['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab'] 
    time_format = "%H:%M"   

    #Extrae los días que esan en formato "Lun, Vie"
    dias_list = dias_str.split(", ")
    dias = ['1' if dia in dias_list else '0' for dia in orden]
    dias = np.array(dias, dtype=int).reshape(1, 6)

    #Extrae las horas que estan en formato "07:00 a 09:00"
    horas_sep = horas_str.split(" a ")
    hora_inicio = datetime.strptime(horas_sep[0], time_format)
    hora_fin = datetime.strptime(horas_sep[1], time_format)
    duration = (hora_fin-hora_inicio).total_seconds()/(60*30) # Obtener la duración en bloques de 30 minutos
    duration = '1'*int(duration) # Crea los bits que indican duración
    inicio_h = hora_inicio.hour - 7   
    inicio_m = hora_inicio.minute//30
    horas = '0'*(inicio_h*2+inicio_m) + duration
    horas = horas.ljust(30,'0')
    horas = np.array(list(horas), dtype=int).reshape(30,1)
 
    # Creación de la matriz
    matriz = np.logical_and(horas, dias)
    flatten = matriz.flatten()
    bit_matrix = bitarray(flatten.tolist()) 
    return bit_matrix

def save_schedule():
    """
    Guarda la matriz generada en un archivo
    """
    with open('indisponibilidad.bin', 'wb') as fh:
        selected_blocks.tofile(fh)
    
def open_schedule():
    """
    Abre la matriz guardada en un archivo
    """
    selected_blocks = bitarray()
    
    try: 
        with open('indisponibilidad.bin', 'rb') as fh:
            selected_blocks.fromfile(fh)
    except FileNotFoundError:
        print("No se encontró una agenda guardada")
        selected_blocks = bitarray(30 * 6)
        selected_blocks.setall(False)

    return selected_blocks

  
def on_drag(event,state):
    #clicked[0] = False
    col = (event.x - OFFSET_X) // CELL_WIDTH
    row = (event.y - OFFSET_Y) // CELL_HEIGHT
    index = row*6 + col

    if 0 <= row < len(hours) and 0 <= col < len(days):
        block = (col,row)
        if (not selected_blocks[index]):    
            if state[0] == 'drawing' or state[0] == 'waiting':
                state[0] = 'drawing'
                selected_blocks[index] = True
                canvas.create_rectangle(
                    col * CELL_WIDTH + OFFSET_X, row * CELL_HEIGHT + OFFSET_Y,
                    (col + 1) * CELL_WIDTH + OFFSET_X, (row + 1) * CELL_HEIGHT + OFFSET_Y,
                    fill="lightblue", outline="gray"
                )
        else:
            if state[0] == 'erasing' or state[0] == 'waiting':
                state[0] = 'erasing'
                selected_blocks[index] = False
                canvas.create_rectangle(
                    col * CELL_WIDTH + OFFSET_X, row * CELL_HEIGHT + OFFSET_Y,
                    (col + 1) * CELL_WIDTH + OFFSET_X, (row + 1) * CELL_HEIGHT + OFFSET_Y,
                    fill="white", outline="gray"
                )


def reset_schedule():
    canvas.delete("all")
    draw_grid()
    selected_blocks.setall(False)

def draw_grid():
    # Crear encabezado de texto
    canvas.create_text(WIDTH // 2, OFFSET_Y // 2, text="Horario de Clases", font=("Arial", 16, "bold"))
    
    # Dibujar encabezados de días
    for i, day in enumerate(days):
        x0 = i * CELL_WIDTH + OFFSET_X
        x1 = (i + 1) * CELL_WIDTH + OFFSET_X
        canvas.create_rectangle(x0, 0, x1, OFFSET_Y, fill="lightgray", outline="black")
        canvas.create_text((x0 + x1) // 2, OFFSET_Y // 2, text=day, font=("Arial", 10))

    # Dibujar encabezados de horas
    for i, hour in enumerate(hours):
        y0 = i * CELL_HEIGHT + OFFSET_Y
        y1 = (i + 1) * CELL_HEIGHT + OFFSET_Y
        canvas.create_rectangle(0, y0, OFFSET_X, y1, fill="lightgray", outline="black")
        canvas.create_text(OFFSET_X // 2, (y0 + y1) // 2, text=hour, font=("Arial", 10))

    # Dibujar líneas de cuadrícula
    for i in range(len(days) + 1):
        x = i * CELL_WIDTH + OFFSET_X
        canvas.create_line(x, OFFSET_Y, x, HEIGHT, fill="gray")
    for i in range(len(hours) + 1):
        y = i * CELL_HEIGHT + OFFSET_Y
        canvas.create_line(OFFSET_X, y, WIDTH, y, fill="gray")

def released_togle(event,state):
    if state[0] != 'waiting':
        state[0] = 'waiting'

def draw_saved_schedule(selected_blocks):
    for i in range(30*6):
        if selected_blocks[i]:
            col = i % 6
            row = i // 6
            canvas.create_rectangle(
                col * CELL_WIDTH + OFFSET_X, row * CELL_HEIGHT + OFFSET_Y,
                (col + 1) * CELL_WIDTH + OFFSET_X, (row + 1) * CELL_HEIGHT + OFFSET_Y,
                fill="lightblue", outline="gray"
            )

# Dimensiones y datos iniciales
CELL_WIDTH = 100
CELL_HEIGHT = 20
OFFSET_X = 60
OFFSET_Y = 30
WIDTH = 600 + OFFSET_X
HEIGHT = 600 + OFFSET_Y

state = ['waiting']
selected_blocks = bitarray(30 * 6)
selected_blocks.setall(False)

days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
hours = [f"{h}:00" for h in range(7, 22)] + [f"{h}:30" for h in range(7, 22)]
hours = sorted(hours, key=lambda t: (int(t.split(":")[0]), int(t.split(":")[1])))

# Crear ventana principal
root = tk.Tk()
root.title("Generador de Horarios")

# Crear Canvas
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="white")
selected_blocks = open_schedule()
draw_saved_schedule(selected_blocks)

canvas.pack()
canvas.bind("<B1-Motion>", lambda event : on_drag(event,state))
canvas.bind("<ButtonRelease-1>",lambda event : released_togle(event,state))
# Dibujar cuadrícula inicial
draw_grid()

# Botones
button_frame = tk.Frame(root)
button_frame.pack()

reset_button = tk.Button(button_frame, text="Limpiar hoja", command=reset_schedule)
reset_button.pack(side="left", padx=10, pady=10)

save_button = tk.Button(button_frame, text="Continuar", command=save_schedule)
save_button.pack(side="left", padx=10, pady=10)


root.mainloop()
