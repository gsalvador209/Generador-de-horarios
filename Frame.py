import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pickle
import json

"""
TODO:
    - Solicitar nombre del horario
    - Ignorar espacios en blanco
"""


class MenuClaves(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Generador de horarios")
        self.geometry("600x600")
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
        
        print(f"Se ha eliminado una clave. Actualmente hay {len(self.claves)} claves.")
        if len(self.claves) == self.max_claves-1:
            self.add_key_placeholder()
        self.update_keyframe_rows()

    def on_key_submit(self, key_frame):
        """
        Crea un nuevo placeholder cuando verifica la clave y se presiona Enter.
        """
        key_entry = key_frame.winfo_children()[0]  # Obtiene el widget del texto
        key = key_entry.get()
        if (len(key) == 4 or  len(key == 3)) and key.isdigit():
            print(f"La clave {key} se ha registrado.")
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

        # if not claves:
        #     messagebox.showwarning("No claves", "No valid claves to save.")
        #     exit()
        #     return

        # Save the claves to a binary file
        with open("claves.pkl", "wb") as file:
            pickle.dump(claves, file)

        print("Las claves se guadradon exitosamente.")
        self.destroy()  # Close the application

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


if __name__ == "__main__":
    app = MenuClaves()
    app.mainloop()
