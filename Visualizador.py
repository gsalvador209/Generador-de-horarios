import tkinter as tk
import tkinter as ttk
import tkinter as messagebox
import pickle
import json
from tkinter import ttk
from bitarray import bitarray

class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.resizable(False, False)
        self.title("Generador de Horarios")
        self.width = 600
        self.height = 650
        self.geometry(f"{self.width}x{self.height}")
        self.frames = {
            "Frame1": MenuClaves(self),
            "Frame2": Indisponibility(self)
        }

        for frame in self.frames.values():
            frame.place(x=0, y=0, relwidth=1, relheight=1)

        self.show_frame("Frame1")

    def show_frame(self, frame_name):
        frame = self.frames[frame_name]
        frame.lift()

class MenuClaves(ttk.Frame):
    def __init__(self,parent):
        super().__init__(parent)
        self.parent = parent
        self.dict_claves = {}
        self.max_claves = 8  # Máximo de claves a ingresar
        self.claves = []  # Lista que contiene los widgets de las claves, no las claves en sí
        self.loading = True
        self.label = ttk.Label(
            self, text="Ingresa las claves de las materias a inscribir", 
            font=("Arial", 12)
        )
        self.label.pack(side="top", pady=10)

        # Frame para las claves
        self.input_frame = ttk.Frame(self, padding=10)
        self.input_frame.pack(fill="both", expand=True)
        
        # Añade los placeholder para las claves
        
        self.load_subject_names()


        if not self.load_claves():
            self.add_key_placeholder()

        if len(self.claves) < self.max_claves:
            self.add_key_placeholder()

        # Add the Finish button
        self.continue_button = ttk.Button(
            self, text="Continuar", command=self.save_and_close
        )
        self.continue_button.pack(side="bottom", pady=20)

    def add_key_placeholder(self, existing_key=""):
        """
        Agrega un placeholder para ingresar una clave. 
        """
        if len(self.claves) < self.max_claves:
            row_index = len(self.claves)

            key_frame = ttk.Frame(self.input_frame) # El placeholder existe como hijo de input_frame
            key_frame.grid(row=row_index, column=0, sticky="w", pady=5)

            # El verdadero espacio donde se escriben las claves
            key_entry = ttk.Entry(key_frame, font=("Arial", 14), width=10, justify="center")
            key_entry.grid(row=0, column=0, padx=5)
            key_entry.focus_set()
            if existing_key != "":
                #print("Existing key:", existing_key)
                key_entry.insert(0, existing_key)
                self.on_key_submit(key_frame)
            else:    
                key_entry.bind("<Return>", lambda event: self.on_key_submit(key_frame))  # Bind Enter key

            #self.claves.append(key_frame)

    def remove_key_placeholder(self, key_frame):
        """Removes a key entry placeholder."""
        self.claves.remove(key_frame)
        key_frame.destroy()  # Remove from the UI
        
        if len(self.claves) == self.max_claves-1:
            self.add_key_placeholder()
        self.update_keyframe_rows()

    def on_key_submit(self, key_frame):
        """
        Crea un nuevo placeholder cuando verifica la clave y se presiona Enter.
        """
        key_entry = key_frame.winfo_children()[0]  # Obtiene el widget del texto
        key = key_entry.get()
        if (len(key) == 4 or  len(key) == 3) and key.isdigit():
            # Bloquea la entrada en este entry
            key_entry.config(state="disabled")
            key_entry.unbind("<Return>")  

            # Se crea el botón de borrar
            delete_button = ttk.Button(
                key_frame,
                text="X",
                width=2,
                command=lambda: self.remove_key_placeholder(key_frame),
            )
            delete_button.grid(row=0, column=1)

            # Se crea el nombre si lo encuentra
            nombre = self.dict_claves.get(key)
            if nombre:
                nombre_label = ttk.Label(key_frame, text=nombre, font=("Arial", 12))
                nombre_label.grid(row=0, column=2, padx=5)

            self.claves.append(key_frame)
            self.update_keyframe_rows()
            # Añade un nuevo placeholder
            if not self.loading:
                self.add_key_placeholder()
        else:
            print("Clave de materia no válida.")

    def save_and_close(self):
        """Saves all entered claves to a text file and closes the application."""
        claves = []
        for key_frame in self.claves:
            key_entry = key_frame.winfo_children()[0]  # Get the entry widget
            if key_entry.get().isdigit() and (len(key_entry.get()) == 4 or len(key_entry.get()) == 3):
                claves.append(key_entry.get())

        # Save the claves to a binary file
        with open("claves.pkl", "wb") as file:
            pickle.dump(claves, file)

        #print("Las claves se guadradon exitosamente.")
        self.parent.show_frame("Frame2")

    def update_keyframe_rows(self):
        """Updates the row index of each key frame."""
        for i, key_frame in enumerate(self.claves):
            key_frame.grid(row=i, column=0, sticky="w", pady=5)

    def load_claves(self):
        """Loads claves from a text file."""
        try:
            with open("claves.pkl", "rb") as file:
                claves = pickle.load(file)

            if not claves:
                self.loading = False
                print("No claves found.")
                return False

            for key in claves:
                self.add_key_placeholder(existing_key=key)
                
            self.loading = False
            return True
        except FileNotFoundError:
            print("No claves file found.")
            return False
        except Exception as e:
            print(f"An error occurred while loading claves: {e}")
            return False
    
    def load_subject_names(self):
        """
        Carga los nombres de las materias desde un archivo JSON.
        """
        try:
            with open("nombres_materias.json", "r") as file:
                self.dict_claves = json.load(file)
                #print(self.dict_claves)
                pass
        except FileNotFoundError:
            print("No se encontró el archivo de nombres de materias.")


class Indisponibility(ttk.Frame):
    """
    Clase que permite la creación de una interfaz gráfica para la creación de horarios de clases.
    """
    def __init__(self, parent):
        super().__init__(parent) 
        self.parent = parent  
        self.OFFSET_X = 60
        self.OFFSET_Y = 30
        self.button_frame_height = 35
        self.text_frame_height = 30
        self.WIDTH = parent.width - self.OFFSET_X
        self.HEIGHT = parent.height - self.OFFSET_Y - self.button_frame_height - self.text_frame_height
        self.color = "LightGoldenrod3"
        self.days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
        self.hours = [f"{h}:00" for h in range(7, 22)] + [f"{h}:30" for h in range(7, 22)]
        self.hours = sorted(self.hours, key=lambda t: (int(t.split(":")[0]), int(t.split(":")[1])))
        
        # Dimensiones y datos iniciales
        self.CELL_WIDTH = self.WIDTH // 6 # Solo 6 porque el offset incluye el espacio para los días
        self.CELL_HEIGHT = (self.HEIGHT) // 30 # 30 bloques de 30 minutos
        self.state = ['waiting']

        # Crear Canvas
        text_frame = ttk.Frame(self, height=self.text_frame_height)
        text_frame.pack(side="top", fill="x", expand=True)

        self.label = ttk.Label(text_frame, text="Selecciona los bloques de tiempo en los que no estás disponible", font=("Arial", 12))
        self.label.pack(side="top")

        self.canvas = tk.Canvas(self, width=self.WIDTH, height=self.HEIGHT, bg="white")
        self.canvas.pack(side="top", fill="both", expand=True)

        self._open_schedule() # Cargar horario guardado
        self._draw_saved_schedule()
        
        self.canvas.bind("<B1-Motion>",self._on_drag)
        self.canvas.bind("<ButtonRelease-1>",self._released_togle)
        # Dibujar cuadrícula inicial
        self._draw_grid()

        # Botones
        button_frame = tk.Canvas(self)
        button_frame.pack(expand=True, fill="both")
        
        button_grid = tk.Frame(button_frame)
        button_grid.pack(expand=True, fill="both")

        button_grid.grid_rowconfigure(0, weight=1)
        button_grid.grid_rowconfigure(2, weight=1)
        button_grid.grid_columnconfigure(0, weight=1)
        button_grid.grid_columnconfigure(3, weight=1)

        reset_button = tk.Button(button_grid ,text="Limpiar hoja", command=self._reset_schedule)
        reset_button.grid(row=1, column=1, padx= 20 ,pady=5)
        
        save_button = tk.Button(button_grid, text="Generar", command=self._save_schedule)
        save_button.grid(row=1, column=2, padx=20 ,pady=5,sticky="nsew")

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
            self.canvas.create_line(x, self.OFFSET_Y, x, self.HEIGHT+self.OFFSET_Y, fill="gray")
        for i in range(len(self.hours) + 1):
            y = i * self.CELL_HEIGHT + self.OFFSET_Y
            self.canvas.create_line(self.OFFSET_X, y, self.WIDTH + self.OFFSET_X, y, fill="gray")

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
        self.parent.destroy() 






# Crear ventana principal
#root = tk.Tk()


#root.mainloop()
