"""
Implementación para crear un blocking inicial antes de generar los horarios
"""

import tkinter as tk

def save_schedule():
    print("Horario seleccionado:")
    for key, value in selected_blocks.items():
        print(f"{key}: {sorted(value)}")

def on_drag(event):
    col = event.x // CELL_WIDTH
    row = event.y // CELL_HEIGHT
    if 0 <= row < len(hours) and 0 <= col < len(days):
        block = (days[col], hours[row])
        if block not in selected_blocks[days[col]]:
            selected_blocks[days[col]].append(hours[row])
            canvas.create_rectangle(
                col * CELL_WIDTH, row * CELL_HEIGHT,
                (col + 1) * CELL_WIDTH, (row + 1) * CELL_HEIGHT,
                fill="lightblue", outline="gray"
            )

def reset_schedule():
    canvas.delete("all")
    draw_grid()
    for day in days:
        selected_blocks[day] = []

def draw_grid():
    for i in range(len(days) + 1):
        canvas.create_line(i * CELL_WIDTH, 0, i * CELL_WIDTH, HEIGHT, fill="gray")
    for i in range(len(hours) + 1):
        canvas.create_line(0, i * CELL_HEIGHT, WIDTH, i * CELL_HEIGHT, fill="gray")

# Dimensiones y datos iniciales
CELL_WIDTH = 100
CELL_HEIGHT = 30
WIDTH = 700
HEIGHT = 600

days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
hours = [f"{h}:00" for h in range(7, 22)]

# Estructura para guardar los bloques seleccionados
selected_blocks = {day: [] for day in days}

# Crear ventana principal
root = tk.Tk()
root.title("Gestión de Horarios")

# Crear Canvas
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="white")
canvas.pack()
canvas.bind("<B1-Motion>", on_drag)

# Dibujar cuadrícula inicial
draw_grid()

# Botones
button_frame = tk.Frame(root)
button_frame.pack()

save_button = tk.Button(button_frame, text="Guardar Horario", command=save_schedule)
save_button.pack(side="left", padx=10, pady=10)

reset_button = tk.Button(button_frame, text="Reiniciar", command=reset_schedule)
reset_button.pack(side="left", padx=10, pady=10)

root.mainloop()
