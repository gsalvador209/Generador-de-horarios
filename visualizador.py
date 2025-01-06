import tkinter as tk
from tkinter import ttk
from bitarray import bitarray

class GUI:
    """
    Clase que permite la creación de una interfaz gráfica para la creación de horarios de clases.
    """
    def __init__(self, root, width=600, height=600):
        
        self.color = "LightGoldenrod3"
        self.days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
        self.hours = [f"{h}:00" for h in range(7, 22)] + [f"{h}:30" for h in range(7, 22)]
        self.hours = sorted(self.hours, key=lambda t: (int(t.split(":")[0]), int(t.split(":")[1])))
        # Dimensiones y datos iniciales
        self.CELL_WIDTH = 100
        self.CELL_HEIGHT = 20
        self.OFFSET_X = 60
        self.OFFSET_Y = 30
        self.WIDTH = width + self.OFFSET_X
        self.HEIGHT = height + self.OFFSET_Y
        self.state = ['waiting']

        self.root = root
        self.root.title("Generador de Horarios")

        # Crear Canvas
        self.canvas = tk.Canvas(self.root, width=self.WIDTH, height=self.HEIGHT, bg="white")
        self._open_schedule() # Cargar horario guardado
        self._draw_saved_schedule()

        self.canvas.pack()
        self.canvas.bind("<B1-Motion>",self._on_drag)
        self.canvas.bind("<ButtonRelease-1>",self._released_togle)
        # Dibujar cuadrícula inicial
        self._draw_grid()

        # Botones
        button_frame = tk.Frame(self.root)
        button_frame.pack()

        self.reset_button = ttk.Button(button_frame ,text="Limpiar hoja", command=self._reset_schedule)
        self.reset_button.pack(side="left", padx=10, pady=10)

        self.save_button = ttk.Button(button_frame, text="Generar", command=self._save_schedule)
        self.save_button.pack(side="left", padx=10, pady=10)

    def _open_schedule(self):
        """
        Abre la matriz guardada en un archivo
        """
        selected_blocks = bitarray()

        try: 
            with open('indisponibilidad.bin', 'rb') as fh:
                selected_blocks.fromfile(fh)
                selected_blocks = selected_blocks[:30*6]
        except FileNotFoundError:
            print("No se encontró una agenda guardada")
            selected_blocks = bitarray(30 * 6)
            selected_blocks.setall(False)

        self.selected_blocks = selected_blocks

    def _save_schedule(self):
        """
        Guarda la matriz generada en un archivo
        """
        with open('indisponibilidad.bin', 'wb') as fh:
            self.selected_blocks.tofile(fh)

        self.selected_blocks = self.selected_blocks
        self.close()
        

    
    def _on_drag(self,event):
        """
        Se encarga de pintar los bloques seleccionados o despintarlos
        """

        col = (event.x - self.OFFSET_X) // self.CELL_WIDTH
        row = (event.y - self.OFFSET_Y) // self.CELL_HEIGHT
        index = row*6 + col

        if 0 <= row < len(self.hours) and 0 <= col < len(self.days):
            #block = (col,row)
            if (not self.selected_blocks[index]):    
                if self.state[0] == 'drawing' or self.state[0] == 'waiting':
                    self.state[0] = 'drawing'
                    self.selected_blocks[index] = True
                    self.canvas.create_rectangle(
                        col * self.CELL_WIDTH + self.OFFSET_X, row *self. CELL_HEIGHT + self.OFFSET_Y,
                        (col + 1) * self.CELL_WIDTH + self.OFFSET_X, (row + 1) * self.CELL_HEIGHT + self.OFFSET_Y,
                        fill=self.color, outline="gray"
                    )
            else:
                if self.state[0] == 'erasing' or self.state[0] == 'waiting':
                    self.state[0] = 'erasing'
                    self.selected_blocks[index] = False
                    self.canvas.create_rectangle(
                        col * self.CELL_WIDTH + self.OFFSET_X, row * self.CELL_HEIGHT + self.OFFSET_Y,
                        (col + 1) * self.CELL_WIDTH + self.OFFSET_X, (row + 1) * self.CELL_HEIGHT + self.OFFSET_Y,
                        fill="white", outline="gray"
                    )

    def _draw_grid(self):
        # Crear encabezado de texto
        self.canvas.create_text(self.WIDTH // 2, self.OFFSET_Y // 2, text="Horario de Clases", font=("Arial", 16, "bold"))
        
        # Dibujar encabezados de días
        for i, day in enumerate(self.days):
            x0 = i * self.CELL_WIDTH + self.OFFSET_X
            x1 = (i + 1) * self.CELL_WIDTH + self.OFFSET_X
            self.canvas.create_rectangle(x0, 0, x1, self.OFFSET_Y, fill="lightgray", outline="black")
            self.canvas.create_text((x0 + x1) // 2, self.OFFSET_Y // 2, text=day, font=("Arial", 10))

        # Dibujar encabezados de horas
        for i, hour in enumerate(self.hours):
            y0 = i * self.CELL_HEIGHT + self.OFFSET_Y
            y1 = (i + 1) * self.CELL_HEIGHT + self.OFFSET_Y
            self.canvas.create_rectangle(0, y0, self.OFFSET_X, y1, fill="lightgray", outline="black")
            self.canvas.create_text(self.OFFSET_X // 2, (y0 + y1) // 2, text=hour, font=("Arial", 10))

        # Dibujar líneas de cuadrícula
        for i in range(len(self.days) + 1):
            x = i * self.CELL_WIDTH + self.OFFSET_X
            self.canvas.create_line(x, self.OFFSET_Y, x, self.HEIGHT, fill="gray")
        for i in range(len(self.hours) + 1):
            y = i * self.CELL_HEIGHT + self.OFFSET_Y
            self.canvas.create_line(self.OFFSET_X, y, self.WIDTH, y, fill="gray")

    def _released_togle(self,event):
        if self.state[0] != 'waiting':
            self.state[0] = 'waiting'

    def _draw_saved_schedule(self):
        for i in range(30*6):
            if self.selected_blocks[i]:
                col = i % 6
                row = i // 6
                self.canvas.create_rectangle(
                    col * self.CELL_WIDTH + self.OFFSET_X, row * self.CELL_HEIGHT +self.OFFSET_Y,
                    (col + 1) * self.CELL_WIDTH + self.OFFSET_X, (row + 1) * self.CELL_HEIGHT + self.OFFSET_Y,
                    fill=self.color, outline="gray"
                )

    def _reset_schedule(self):
        self.canvas.delete("all")
        self._draw_grid()
        self.selected_blocks.setall(False)

    def close(self):
        self.root.destroy() 






# Crear ventana principal
#root = tk.Tk()


#root.mainloop()
