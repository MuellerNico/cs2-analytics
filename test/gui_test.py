import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageTk

# Function to draw a dot at user-specified coordinates
def draw_dot():
    try:
        x = int(entry_x.get())
        y = int(entry_y.get())
        canvas.create_oval(x-2, y-2, x+2, y+2, fill="red")  # Drawing a small red dot
    except ValueError:
        print("Please enter valid coordinates.")

# Initialize the tkinter window
root = tk.Tk()
root.title("Image with Dot")

# Load and display the image
image_path = "minimaps/de_inferno.png"  # Replace with your image path
image = Image.open(image_path)
bg_image = ImageTk.PhotoImage(image)

# Set the window size to match the image size
window_width = 200
window_height = 200
root.geometry(f"{window_width}x{window_height}")

# Create a canvas to hold the image
canvas = Canvas(root, width=window_width, height=window_height)
canvas.pack()

# Display the image as background
canvas.create_image(0, 0, anchor="nw", image=bg_image)

# User input for coordinates
frame = tk.Frame(root)
frame.pack(side=tk.BOTTOM, pady=10)

tk.Label(frame, text="X:").pack(side=tk.LEFT)
entry_x = tk.Entry(frame, width=5)
entry_x.pack(side=tk.LEFT)

tk.Label(frame, text="Y:").pack(side=tk.LEFT)
entry_y = tk.Entry(frame, width=5)
entry_y.pack(side=tk.LEFT)

draw_button = tk.Button(frame, text="Draw Dot", command=draw_dot)
draw_button.pack(side=tk.LEFT)

# Start the tkinter loop
root.mainloop()
