import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import random
from PIL import Image

# Konstanta untuk bahan radioaktif
radioactive_data = {
    "U-235": {"half_life": 7.04e8 * 365 * 24 * 3600, "mass_to_atoms": 2.56e21, "dose_factor": 0.01},
    "Pu-239": {"half_life": 2.41e4 * 365 * 24 * 3600, "mass_to_atoms": 2.53e21, "dose_factor": 0.02},
    "Th-232": {"half_life": 1.41e10 * 365 * 24 * 3600, "mass_to_atoms": 2.40e21, "dose_factor": 0.015},
}

def decay_animation():
    """Membuat animasi peluruhan partikel radioaktif dan plotting dosis radiasi serapan."""
    material = material_var.get()
    mass = float(mass_slider.get())
    num_particles = int(mass * 100)  # Jumlah partikel sesuai massa (arbitrary scaling)
    
    data = radioactive_data[material]
    half_life = data["half_life"]
    decay_constant = math.log(2) / half_life
    dose_factor = data["dose_factor"]  # Faktor dosis berdasarkan material
    
    # Posisi awal partikel
    x_positions = [random.uniform(0, 1) for _ in range(num_particles)]
    y_positions = [random.uniform(0, 1) for _ in range(num_particles)]
    alive_status = [1] * num_particles  # 1 jika partikel masih hidup, 0 jika meluruh
    
    cumulative_doses = [0]  # List untuk dosis serapan sepanjang waktu
    time_steps = [0]  # List untuk waktu (dalam detik)

    # Membuat tab animasi
    for widget in plot_frame.winfo_children():
        widget.destroy()
    
    notebook = ttk.Notebook(plot_frame)
    notebook.pack(expand=True, fill="both")
    
    # Plot animasi peluruhan
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title(f"Animasi Peluruhan - {material}")
    ax.axis("off")
    
    scatter = ax.scatter(x_positions, y_positions, c="blue", s=10, label="Partikel Aktif")
    legend = ax.legend(loc="upper right")
    
    # Plot dosis radiasi serapan
    dose_fig, dose_ax = plt.subplots(figsize=(5, 4))
    dose_ax.set_xlabel("Waktu (detik)")
    dose_ax.set_ylabel("Dosis Serapan Radiasi (mSv)")
    dose_ax.set_title(f"Dosis Serapan Radiasi - {material}")
    
    dose_line, = dose_ax.plot([], [], label="Dosis Serapan", color="red")
    dose_ax.legend(loc="upper right")
    
    # Menyimpan setiap frame untuk membuat GIF
    frames = []

    def update(frame):
        nonlocal alive_status, x_positions, y_positions, cumulative_doses, time_steps
        
        decay_prob = decay_constant * frame / 200  # Probabilitas peluruhan per frame
        
        # Menghitung dosis yang diterima manusia berdasarkan peluruhan partikel
        dose_increment = 0
        for i in range(num_particles):
            if alive_status[i] == 1:
                # Gerakan acak yang lebih luas untuk partikel aktif
                x_positions[i] += random.uniform(-0.05, 0.05)
                y_positions[i] += random.uniform(-0.05, 0.05)
                
                # Membatasi gerakan dalam batas (0, 1)
                x_positions[i] = min(max(x_positions[i], 0), 1)
                y_positions[i] = min(max(y_positions[i], 0), 1)
                
                # Partikel meluruh dengan probabilitas tertentu
                if random.uniform(0, 1) < decay_prob:
                    alive_status[i] = 0
                    dose_increment += dose_factor * mass * 0.01

        cumulative_doses.append(cumulative_doses[-1] + dose_increment)
        time_steps.append(frame)

        # Perbarui warna dan posisi partikel
        colors = ["blue" if status == 1 else "gray" for status in alive_status]
        scatter.set_offsets(list(zip(x_positions, y_positions)))
        scatter.set_color(colors)
        
        # Update dosis serapan radiasi di plot
        dose_line.set_data(time_steps, cumulative_doses)
        dose_ax.relim()
        dose_ax.autoscale_view()

        # Simpan frame untuk GIF
        fig.canvas.draw()
        image = Image.frombytes("RGB", fig.canvas.get_width_height(), fig.canvas.tostring_rgb())
        frames.append(image)

        return scatter, dose_line,

    anim = FuncAnimation(fig, update, frames=200, interval=50, blit=True)

    # Menambahkan ke GUI
    animation_tab = ttk.Frame(notebook)
    canvas = FigureCanvasTkAgg(fig, master=animation_tab)
    canvas.get_tk_widget().pack()
    canvas.draw()
    notebook.add(animation_tab, text="Animasi Peluruhan")
    
    dose_tab = ttk.Frame(notebook)
    dose_canvas = FigureCanvasTkAgg(dose_fig, master=dose_tab)
    dose_canvas.get_tk_widget().pack()
    dose_canvas.draw()
    notebook.add(dose_tab, text="Dosis Serapan Radiasi")

    return anim, frames

def save_gif(frames):
    """Menyimpan animasi sebagai GIF."""
    try:
        gif_filename = "decay_animation.gif"
        frames[0].save(
            gif_filename,
            save_all=True,
            append_images=frames[1:],
            optimize=False,
            duration=100,
            loop=0
        )
        messagebox.showinfo("Sukses", f"Animasi berhasil disimpan sebagai {gif_filename}")
    except Exception as e:
        messagebox.showerror("Error", f"Gagal menyimpan animasi: {e}")

# GUI
root = tk.Tk()
root.title("Simulasi Geiger-Muller Counter dengan Animasi Peluruhan")

material_var = tk.StringVar(value="U-235")
material_label = tk.Label(root, text="Pilih Material Radioaktif:")
material_label.pack()
material_dropdown = ttk.Combobox(root, textvariable=material_var, values=list(radioactive_data.keys()))
material_dropdown.pack()

mass_label = tk.Label(root, text="Massa Bahan (gram):")
mass_label.pack()
mass_slider = tk.Scale(root, from_=0.1, to=100, resolution=0.1, orient="horizontal")
mass_slider.pack()

def on_animation_button_click():
    global_animation["anim"], global_animation["frames"] = decay_animation()

animation_button = tk.Button(root, text="Tampilkan Animasi Peluruhan", command=on_animation_button_click)
animation_button.pack()

def on_save_gif_button_click():
    if "frames" in global_animation:
        save_gif(global_animation["frames"])
    else:
        messagebox.showerror("Error", "Animasi belum dibuat.")

save_gif_button = tk.Button(root, text="Simpan Animasi (GIF)", command=on_save_gif_button_click)
save_gif_button.pack()

plot_frame = tk.Frame(root)
plot_frame.pack()

global_animation = {}

root.mainloop()
