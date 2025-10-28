# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 11:54:49 2024

@author: sh23q253
"""
import tkinter as tk
from tkinter import messagebox
import dat1  # Assuming your DAT implementation is saved as dat1.py

# Load the model
model = dat1.Model("model/vectors_glove_de_wiki.txt", "model/vocab_glove_de_wiki.txt")

# Define a function to handle the calculation
def calculate_dat():
    """Calculate DAT score based on user input words"""

    # Collect words from input fields and reset their background color
    words = []
    for ent in entries:
        ent.config(bg="white")  # Reset background to default
        word = ent.get().strip().lower()
        words.append(word)

    # Check word validity and highlight invalid words
    valid_words = []
    for i, word in enumerate(words):
        if model.validate(word) is not None:
            valid_words.append(word)
        else:
            entries[i].config(bg="red")  # Highlight invalid words in red

    # Calculate the DAT score if enough valid words are provided
    if len(valid_words) >= 7:
        try:
            score = model.dat(valid_words)
            result_label.config(text=f"DAT Score: {score:.2f}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    else:
        messagebox.showerror("Error", "Not enough valid words (minimum 7).")

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
