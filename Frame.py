import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


class DynamicKeyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Dynamic Key Placeholders")
        self.geometry("600x600")
        self.max_keys = 8  # Maximum number of keys allowed
        self.keys = []  # List to hold references to key entry widgets

        # Create a Frame for input widgets
        self.input_frame = ttk.Frame(self, padding=10)
        self.input_frame.pack(fill="both", expand=True)

        # Add the first key placeholder
        self.add_key_placeholder()

        # Add the Finish button
        self.finish_button = ttk.Button(
            self, text="Finish", command=self.save_and_close
        )
        self.finish_button.pack(side="bottom", pady=20)

    def add_key_placeholder(self):
        """Adds a new key entry placeholder."""
        if len(self.keys) < self.max_keys:
            row_index = len(self.keys)

            # Create a Frame to hold the key entry and delete button
            key_frame = ttk.Frame(self.input_frame)
            key_frame.grid(row=row_index, column=0, sticky="w", pady=5)

            # Key entry widget
            key_entry = ttk.Entry(key_frame, font=("Arial", 14), width=10, justify="center")
            key_entry.grid(row=0, column=0, padx=5)
            key_entry.bind("<Return>", lambda event: self.on_key_submit(key_entry))  # Bind Enter key

            # Delete button for the key
            delete_button = ttk.Button(
                key_frame,
                text="X",
                width=2,
                command=lambda: self.remove_key_placeholder(key_frame),
            )
            delete_button.grid(row=0, column=1)

            # Keep track of the key entry and its container
            self.keys.append(key_frame)

    def remove_key_placeholder(self, key_frame):
        """Removes a key entry placeholder."""
        self.keys.remove(key_frame)
        key_frame.destroy()  # Remove from the UI

    def on_key_submit(self, key_entry):
        """Handles the Enter key event for key submission."""
        key = key_entry.get()
        if len(key) == 4 and key.isdigit():
            print(f"Key accepted: {key}")

            # Clear the current key entry
            key_entry.config(state="disabled")  # Lock the current key
            key_entry.unbind("<Return>")  # Unbind Enter to prevent re-submission

            # Add a new key placeholder if not at max
            self.add_key_placeholder()
        else:
            print("Invalid key. Please enter a 4-digit number.")

    def save_and_close(self):
        """Saves all entered keys to a text file and closes the application."""
        keys = []
        for key_frame in self.keys:
            key_entry = key_frame.winfo_children()[0]  # Get the entry widget
            if key_entry.get().isdigit() and len(key_entry.get()) == 4:
                keys.append(key_entry.get())

        if not keys:
            messagebox.showwarning("No Keys", "No valid keys to save.")
            return

        # Save the keys to a text file
        with open("keys.txt", "w") as file:
            for key in keys:
                file.write(f"{key}\n")

        print("Keys saved to keys.txt")
        self.destroy()  # Close the application


if __name__ == "__main__":
    app = DynamicKeyApp()
    app.mainloop()
