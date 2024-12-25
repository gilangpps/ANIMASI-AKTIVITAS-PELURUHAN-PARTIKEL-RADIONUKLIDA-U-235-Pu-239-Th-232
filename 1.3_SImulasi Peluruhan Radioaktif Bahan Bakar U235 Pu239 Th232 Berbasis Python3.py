import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation, FFMpegWriter
import random

# Konstanta untuk bahan radioaktif
radioactive_data = {
    "U-235": {"half_life": 7.04e8 * 365 * 24 * 3600, "mass_to_atoms": 2.56e21},
    "Pu-239": {"half_life": 2.41e4 * 365 * 24 * 3600, "mass_to_atoms": 2.53e21},
    "Th-232": {"half_life": 1.41e10 * 365 * 24 * 3600, "mass_to_atoms": 2.40e21},
}

def decay_animation():
    """Membuat animasi peluruhan partikel radioaktif dengan pergerakan acak yang lebih luas."""
    material = material_var.get()
    mass = float(mass_slider.get())
    num_particles = int(mass * 100)  # Jumlah partikel sesuai massa (arbitrary scaling)
    
    data = radioactive_data[material]
    half_life = data["half_life"]
    decay_constant = math.log(2) / half_life
    
    # Posisi awal partikel
    x_positions = [random.uniform(0, 1) for _ in range(num_particles)]
    y_positions = [random.uniform(0, 1) for _ in range(num_particles)]
    alive_status = [1] * num_particles  # 1 jika partikel masih hidup, 0 jika meluruh
    
    # Membuat tab animasi
    for widget in plot_frame.winfo_children():
        widget.destroy()
    
    notebook = ttk.Notebook(plot_frame)
    notebook.pack(expand=True, fill="both")
    
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title(f"Animasi Peluruhan - {material}")
    ax.axis("off")
    
    scatter = ax.scatter(x_positions, y_positions, c="blue", s=10, label="Partikel Aktif")
    legend = ax.legend(loc="upper right")
    
    # Fungsi update untuk animasi
    def update(frame):
        nonlocal alive_status, x_positions, y_positions
        decay_prob = decay_constant * frame / 200  # Probabilitas peluruhan per frame
        
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
        
        # Perbarui warna dan posisi partikel
        colors = ["blue" if status == 1 else "gray" for status in alive_status]
        scatter.set_offsets(list(zip(x_positions, y_positions)))
        scatter.set_color(colors)
        return scatter,

    # Membuat animasi
    anim = FuncAnimation(fig, update, frames=200, interval=50, blit=True)
    
    # Menambahkan ke GUI
    animation_tab = ttk.Frame(notebook)
    canvas = FigureCanvasTkAgg(fig, master=animation_tab)
    canvas.get_tk_widget().pack()
    canvas.draw()
    notebook.add(animation_tab, text="Animasi Peluruhan")
    
    return anim, fig

def save_video(anim, fig):
    """Menyimpan animasi sebagai video (format MP4)."""
    writer = FFMpegWriter(fps=30, metadata=dict(artist='Matplotlib'), bitrate=1800)
    try:
        video_filename = "decay_animation.mp4"
        anim.save(video_filename, writer=writer)
        messagebox.showinfo("Sukses", f"Video berhasil disimpan sebagai {video_filename}")
    except Exception as e:
        messagebox.showerror("Error", f"Gagal menyimpan video: {e}")

# GUI
root = tk.Tk()
root.title("Simulasi Geiger-Muller Counter dengan Animasi Peluruhan")

# Dropdown untuk bahan radioaktif
material_var = tk.StringVar(value="U-235")
material_label = tk.Label(root, text="Pilih Material Radioaktif:")
material_label.pack()
material_dropdown = ttk.Combobox(root, textvariable=material_var, values=list(radioactive_data.keys()))
material_dropdown.pack()

# Slider untuk massa bahan
mass_label = tk.Label(root, text="Massa Bahan (gram):")
mass_label.pack()
mass_slider = tk.Scale(root, from_=0.1, to=100, resolution=0.1, orient="horizontal")
mass_slider.pack()

# Tombol untuk animasi
def on_animation_button_click():
    """Fungsi untuk memulai animasi dan menyimpan animasi ke dalam global dictionary."""
    anim, fig = decay_animation()
    global_animation["anim"] = anim
    global_animation["fig"] = fig

animation_button = tk.Button(root, text="Tampilkan Animasi Peluruhan", command=on_animation_button_click)
animation_button.pack()

# Tombol untuk menyimpan video
def on_save_video_button_click():
    """Fungsi untuk menyimpan video animasi."""
    if "anim" in global_animation:
        save_video(global_animation["anim"], global_animation["fig"])
    else:
        messagebox.showerror("Error", "Animasi belum ditampilkan. Silakan buat animasi terlebih dahulu.")

save_video_button = tk.Button(root, text="Simpan Video", command=on_save_video_button_click)
save_video_button.pack()

# Frame untuk animasi dan plot
plot_frame = tk.Frame(root)
plot_frame.pack()

# Global variable untuk menyimpan animasi
global_animation = {}

# Jalankan aplikasi
root.mainloop()
