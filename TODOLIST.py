import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Create the main window  
newWindow = tk.Tk()
newWindow.title("To-Do List ")

# Set the window size
newWindow.geometry("800x800+270+200")

# Set the background color
newWindow.configure(bg="#944E63")

# resize images with background color
def resize_image(image_path, size, background_color=(148, 78, 99)):
    with Image.open(image_path) as img:
        img = img.convert("RGBA")
        bg = Image.new('RGBA', img.size, background_color + (255,))
        bg.paste(img, (0, 0), img)
        img = bg.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)

# Resize icons with background color
done_icon = resize_image("done_icon.png", (20, 20), background_color=(148, 78, 99))
delete_icon = resize_image("delete_icon.png", (20, 20), background_color=(148, 78, 99))

#Done function
def mark_as_done(task_label, done_button):
    task_label.config(fg="gray", font=("Helvetica", 18, "overstrike"))#changes the task label text to gray and strikes it out, and disables the "done" button.
    done_button.config(image=done_icon, state=tk.DISABLED, disabledforeground="green")
    update_task_count()


#delete task function
def delete_task(task_frame):
    task_frame.destroy()
    update_serial_numbers()
    update_task_count()

#Adding task 
def add_task(task=None):#adds a new task to the task list, creating a frame for each task with a label and two buttons (Done, Delete).
    if not task:
        task = task_entry.get()
    if task:
        task_frame = tk.Frame(task_container, bg="#AA5486", pady=5)#holds the task label and buttons
        task_number = len(task_container.winfo_children()) + 1
        task_label = tk.Label(task_frame, text=f"{task_number}. {task}", bg="#AA5486", fg="#ffffff", font=("Helvetica", 18))#displays the task with its number
        task_label.pack(side=tk.LEFT, padx=10)

        done_button = tk.Button(task_frame, image=done_icon, command=lambda: mark_as_done(task_label, done_button), bg="#add8e6", fg="#1cbd52", font=("Helvetica", 12))
        done_button.pack(side=tk.RIGHT, padx=5)

        delete_button = tk.Button(task_frame, image=delete_icon, command=lambda: delete_task(task_frame), bg="#ff6347", fg="#e0194b", font=("Helvetica", 12))
        delete_button.pack(side=tk.RIGHT, padx=5)

        task_frame.pack(fill=tk.X, pady=5)
        task_entry.delete(0, tk.END)
        update_serial_numbers()
        update_task_count()
        canvas.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))


#Updating Serial Numbers
def update_serial_numbers():
    for index, task_frame in enumerate(task_container.winfo_children()):
        task_label = task_frame.winfo_children()[0]
        task_text = task_label.cget("text")
        if ". " in task_text:
            task_text = task_text.split(". ", 1)[1]
        task_label.config(text=f"{index + 1}. {task_text}")

#Delete all tasks
def delete_all_tasks():
    for widget in task_container.winfo_children():
        widget.destroy()
    update_task_count()

#Update task count
def update_task_count():
    total_tasks = len(task_container.winfo_children())
    done_tasks = sum(1 for task_frame in task_container.winfo_children() if "overstrike" in task_frame.winfo_children()[0].cget("font"))
    remaining_tasks = total_tasks - done_tasks

    total_tasks_label.config(text=f"Total Tasks: {total_tasks}")
    remaining_tasks_label.config(text=f"Remaining Tasks: {remaining_tasks}")
    done_tasks_label.config(text=f"Completed Tasks: {done_tasks}")
    update_pie_chart(total_tasks, remaining_tasks, done_tasks)

#Update pie chart
def update_pie_chart(total_tasks, remaining_tasks, done_tasks):
    for widget in pie_chart_frame.winfo_children():
        widget.destroy()

    if total_tasks == 0:
        return

    labels = 'Completed Tasks', 'Remaining Tasks'
    sizes = [done_tasks, remaining_tasks]
    colors = ['purple', '#CB9DF0']
    explode = (0.1, 0)

    fig, ax = plt.subplots(figsize=(5, 3), dpi=100)
    fig.patch.set_facecolor('#F0C1E1')

    ax.pie(sizes, explode=explode, colors=colors, autopct='%1.1f%%',
           shadow=True, startangle=140)
    ax.axis('equal')

    ax.legend(labels, loc="best")

    canvas_chart = FigureCanvasTkAgg(fig, master=pie_chart_frame)
    canvas_chart.draw()
    canvas_chart.get_tk_widget().pack()

    plt.close(fig)

#Save task function
def save_tasks():
    with open("tasks.txt", "w") as file:
        for task_frame in task_container.winfo_children():
            task_label = task_frame.winfo_children()[0]
            task_text = task_label.cget("text").split(". ", 1)[1]
            task_done = "1" if "overstrike" in task_label.cget("font") else "0"
            file.write(f"{task_text}|{task_done}\n")
    messagebox.showinfo("Save Tasks", "Tasks have been saved successfully.")

#load task function
def load_tasks():
    try:
        with open("tasks.txt", "r") as file:
            for line in file:
                task_text, task_done = line.strip().split("|")
                add_task(task_text)
                if task_done == "1":
                    task_frame = task_container.winfo_children()[-1]
                    task_label = task_frame.winfo_children()[0]
                    done_button = task_frame.winfo_children()[1]
                    mark_as_done(task_label, done_button)
        update_task_count()
    except FileNotFoundError:
        pass

# Create a canvas to allow scrolling
canvas = tk.Canvas(newWindow, bg="#944E63")
canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Create a scrollbar
scrollbar = tk.Scrollbar(newWindow, orient="vertical", command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill="y")

# Configure the canvas
canvas.configure(yscrollcommand=scrollbar.set)
canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

# Create a frame inside the canvas with adjustable size
task_container = tk.Frame(canvas, bg="#944E63", width=500, height=600)  # Adjust the width and height as needed
canvas.create_window((0, 0), window=task_container, anchor="nw")

# Create a navigation bar heading
nav_frame = tk.Frame(newWindow, bg="#CB80AB")
nav_frame.pack(fill=tk.X)

nav_label = tk.Label(nav_frame, text="To-Do List", bg="#CB80AB", fg="#6C0345", font=("Helvetica", 24, "bold"))
nav_label.pack(pady=10)

# Frame for pie chart
pie_chart_frame = tk.Frame(newWindow, bg="#F0C1E1")
pie_chart_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

# Entry widget and buttons placed on the left side
controls_frame = tk.Frame(newWindow, bg="#F0C1E1")
controls_frame.pack(side=tk.LEFT, padx=0, pady=10)

# Entry widget for adding tasks
task_entry = tk.Entry(controls_frame, width=40, bg="#F0C1E1", fg="#000000", font=("Helvetica", 22))
task_entry.pack(pady=10)

# Button to add tasks
add_task_button = tk.Button(controls_frame, text="Add Task", command=add_task, bg="#ffc6c6", fg="#000000", font=("Helvetica", 12))
add_task_button.pack(pady=5)

# Button to delete all tasks
delete_all_button = tk.Button(controls_frame, text="Delete All Tasks", command=delete_all_tasks, bg="#ffc6c6", fg="#000000", font=("Helvetica", 12))
delete_all_button.pack(pady=5)

# Buttons to save and load tasks
save_button = tk.Button(controls_frame, text="Save Tasks", command=save_tasks, bg="#FFC6C6", fg="#000000", font=("Helvetica", 12))
save_button.pack(pady=5)

load_button = tk.Button(controls_frame, text="Load Tasks", command=load_tasks, bg="#FFC6C6", fg="#000000", font=("Helvetica", 12))
load_button.pack(pady=5)

# Labels to display task counts
total_tasks_label = tk.Label(controls_frame, text="Total Tasks: 0", bg="#CB80AB", fg="#ffffff", font=("Helvetica", 18))
total_tasks_label.pack(pady=2)

remaining_tasks_label = tk.Label(controls_frame, text="Remaining Tasks: 0", bg="#CB80AB", fg="#FFFFFF", font=("Helvetica", 18))
remaining_tasks_label.pack(pady=2)

done_tasks_label = tk.Label(controls_frame, text="Completed Tasks: 0", bg="#CB80AB", fg="#FFFFFF", font=("Helvetica", 18))
done_tasks_label.pack(pady=2)

# Start the main event loop
newWindow.mainloop()
#This starts the Tkinter event loop, allowing the window to remain open and interactive.
