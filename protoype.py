import tkinter as tk
from tkinter import messagebox
import dat1  # Assuming your DAT implementation is saved as dat1.py

# Load the model
model = dat1.Model("model/vectors.txt", "model/vocab.txt")

# Define a function to handle the calculation
def calculate_dat():
    # Collect words from input fields
    words = [entry.get().strip().lower() for entry in entries]
    
    # Calculate the DAT score
    try:
        score = model.dat(words)
        if score is not None:
            result_label.config(text=f"DAT Score: {score:.2f}")
        else:
            messagebox.showerror("Error", "Not enough valid words (minimum 7).")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Create the main application window
root = tk.Tk()
root.title("DAT")

# Instructions
instruction_label = tk.Label(
    root, 
    text="Gib 10 Wörter ein, die möglichst verschieden sind. Drücke 'Fertig', um den DAT Score zu berechnen.",
    wraplength=400,
    justify="left"
)
instruction_label.pack(pady=10)

# Input fields for words
entries = []
for i in range(10):
    frame = tk.Frame(root)
    frame.pack(pady=2)
    label = tk.Label(frame, text=f"Word {i+1}:")
    label.pack(side="left", padx=5)
    entry = tk.Entry(frame, width=20)
    entry.pack(side="left")
    entries.append(entry)

# Submit button
submit_button = tk.Button(root, text="Fertig", command=calculate_dat)
submit_button.pack(pady=10)

# Result display
result_label = tk.Label(root, text="", font=("Arial", 12, "bold"))
result_label.pack(pady=10)

# Start the main event loop
root.mainloop()
