import tkinter as tk

def save_schedule():
    """
    Obtiene un dataframe que contiene los horarios seleccionados
    """
    print("Horario seleccionado:")
    

    for key, value in selected_blocks.items():
        print(f"{key}: {sorted(value)}")

def on_drag(event,state):
    #clicked[0] = False
    col = (event.x - OFFSET_X) // CELL_WIDTH
    row = (event.y - OFFSET_Y) // CELL_HEIGHT
    if 0 <= row < len(hours) and 0 <= col < len(days):
        block = (days[col], hours[row])
        if ((block[1] not in selected_blocks[days[col]])):
            if state[0] == 'drawing' or state[0] == 'waiting':
                state[0] = 'drawing'
                selected_blocks[days[col]].append(hours[row])
                canvas.create_rectangle(
                    col * CELL_WIDTH + OFFSET_X, row * CELL_HEIGHT + OFFSET_Y,
                    (col + 1) * CELL_WIDTH + OFFSET_X, (row + 1) * CELL_HEIGHT + OFFSET_Y,
                    fill="lightblue", outline="gray"
                )
        else:
            if state[0] == 'erasing' or state[0] == 'waiting':
                state[0] = 'erasing'
                selected_blocks[days[col]].remove(hours[row])
                canvas.create_rectangle(
                    col * CELL_WIDTH + OFFSET_X, row * CELL_HEIGHT + OFFSET_Y,
                    (col + 1) * CELL_WIDTH + OFFSET_X, (row + 1) * CELL_HEIGHT + OFFSET_Y,
                    fill="white", outline="gray"
                )



def reset_schedule():
    canvas.delete("all")
    draw_grid()
    for day in days:
        selected_blocks[day] = []

def draw_grid():
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

# Dimensiones y datos iniciales
CELL_WIDTH = 100
CELL_HEIGHT = 30
OFFSET_X = 60
OFFSET_Y = 30
WIDTH = 600 + OFFSET_X
HEIGHT = 450 + OFFSET_Y

state = ['waiting']

days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
hours = [f"{h}:00" for h in range(7, 22)] + [f"{h}:30" for h in range(7, 22)]
hours = sorted(hours, key=lambda t: (int(t.split(":")[0]), int(t.split(":")[1])))

# Estructura para guardar los bloques seleccionados
selected_blocks = {day: [] for day in days}

# Crear ventana principal
root = tk.Tk()
root.title("Generador de Horarios")

# Crear Canvas
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="white")
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

save_button = tk.Button(button_frame, text="Guardar Horario", command=save_schedule)
save_button.pack(side="left", padx=10, pady=10)


root.mainloop()
