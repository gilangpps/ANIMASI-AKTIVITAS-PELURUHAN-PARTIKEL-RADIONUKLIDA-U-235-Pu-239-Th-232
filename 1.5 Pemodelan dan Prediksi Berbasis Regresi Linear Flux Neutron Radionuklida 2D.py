import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation, FFMpegWriter
import pandas as pd
import os
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# Path ke ffmpeg
FFMPEG_PATH = r"D:\ace\Downloads\ffmpeg-2024-12-19-git-494c961379-full_build\bin\ffmpeg.exe"
os.environ["PATH"] += os.pathsep + os.path.dirname(FFMPEG_PATH)

# Global variables
flux = None
flux_history = None
ani = None
is_running = False
regression_model = None
mse_value = None
accuracy_value = None
colorbar = None

# Fungsi untuk menghitung flux neutron
def calculate_flux(grid_size, time_steps, D, Sigma_a, S):
    dx = 1.0  # Ukuran grid
    dt = 0.01  # Langkah waktu
    flux_history = []
    flux = np.zeros((grid_size, grid_size))
    flux[int(grid_size / 2), int(grid_size / 2)] = 1.0  # Sumber neutron awal

    for _ in range(time_steps):
        flux_new = np.copy(flux)
        for i in range(1, grid_size - 1):
            for j in range(1, grid_size - 1):
                laplacian = (flux[i+1, j] + flux[i-1, j] + flux[i, j+1] + flux[i, j-1] - 4 * flux[i, j]) / dx**2
                flux_new[i, j] += dt * (D * laplacian - Sigma_a * flux[i, j] + S)
        flux = np.copy(flux_new)
        flux_history.append(flux.copy())
    return flux, flux_history

# Fungsi untuk memperbarui tampilan animasi
def update_animation(frame):
    global colorbar
    ax.clear()
    im = ax.imshow(flux_history[frame], cmap='viridis', origin='lower', interpolation='none')
    ax.set_title(f"Flux Neutron pada Langkah Waktu {frame + 1}")
    ax.set_xlabel("Posisi X")
    ax.set_ylabel("Posisi Y")
    im.set_clim(vmin=0, vmax=np.max(flux_history[frame]))  # Update batas warna
    if colorbar is None:
        cbar_ax = fig.add_axes([0.92, 0.1, 0.03, 0.8])  # Posisi colorbar
        colorbar = plt.colorbar(im, cax=cbar_ax)
    else:
        colorbar.update_normal(im)  # Update colorbar sesuai data

# Fungsi untuk memulai animasi
def start_animation():
    global ani, is_running
    if ani is None or not is_running:
        ani = FuncAnimation(fig, update_animation, frames=len(flux_history), interval=50, blit=False)
        is_running = True
        canvas.draw()

# Fungsi untuk menghentikan animasi
def stop_animation():
    global ani, is_running
    if ani is not None and is_running:
        ani.event_source.stop()
        is_running = False

# Fungsi untuk menyimpan animasi
def save_animation():
    global ani
    if ani is None:
        messagebox.showerror("Error", "Tidak ada animasi untuk disimpan.")
        return
    filepath = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")])
    if filepath:
        try:
            writer = FFMpegWriter(fps=20, metadata=dict(artist='Neutron Flux Simulation'), bitrate=1800)
            ani.save(filepath, writer=writer)
            messagebox.showinfo("Berhasil", f"Animasi disimpan di {filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan animasi: {e}")

# Fungsi untuk menyimpan data ke Excel
def save_data():
    global flux
    if flux is None:
        messagebox.showerror("Error", "Tidak ada data untuk disimpan.")
        return
    filepath = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
    if filepath:
        df = pd.DataFrame(flux)
        df.to_excel(filepath, index=False)
        messagebox.showinfo("Berhasil", f"Data disimpan di {filepath}")

# Fungsi untuk menjalankan simulasi
def run_simulation():
    global flux, flux_history, grid_size, D, Sigma_a, S, time_steps
    grid_size = int(grid_size_entry.get())
    D = float(D_entry.get())
    Sigma_a = float(Sigma_a_entry.get())
    S = float(S_entry.get())
    time_steps = int(time_steps_entry.get())

    flux, flux_history = calculate_flux(grid_size, time_steps, D, Sigma_a, S)
    start_animation()

# Fungsi untuk melatih model regresi linear dan menampilkan GUI tambahan
def train_regression_model():
    global flux_history, regression_model, mse_value, accuracy_value
    if flux_history is None:
        messagebox.showerror("Error", "Tidak ada data flux untuk model.")
        return

    # Menyiapkan data untuk regresi
    total_flux = [np.sum(frame) for frame in flux_history]
    time_steps = np.arange(len(total_flux)).reshape(-1, 1)
    
    # Membuat model regresi linear
    regression_model = LinearRegression()
    regression_model.fit(time_steps, total_flux)

    # Prediksi menggunakan model
    flux_predictions = regression_model.predict(time_steps)

    # Menghitung MSE dan R2 Score (akurasi)
    mse_value = mean_squared_error(total_flux, flux_predictions)
    accuracy_value = r2_score(total_flux, flux_predictions)

    # Membuka GUI tambahan
    display_results(total_flux, flux_predictions, mse_value, accuracy_value)

# Fungsi untuk menampilkan GUI tambahan dengan plotting dan tabel
def display_results(total_flux, flux_predictions, mse, accuracy):
    result_window = tk.Toplevel(root)
    result_window.title("Hasil Model Regresi Linear")
    
    # Plotting
    fig_result, ax_result = plt.subplots(figsize=(6, 4))
    ax_result.plot(range(len(total_flux)), total_flux, label="Data Aktual", marker='o')
    ax_result.plot(range(len(flux_predictions)), flux_predictions, label="Prediksi", linestyle='--')
    ax_result.set_title("Hasil Regresi Linear")
    ax_result.set_xlabel("Langkah Waktu")
    ax_result.set_ylabel("Total Flux")
    ax_result.legend()

    canvas_result = FigureCanvasTkAgg(fig_result, master=result_window)
    canvas_result.get_tk_widget().grid(row=0, column=0, padx=10, pady=10)

    # Tabel
    table_frame = ttk.Frame(result_window)
    table_frame.grid(row=0, column=1, padx=10, pady=10)

    columns = ["Waktu", "Flux Aktual", "Flux Prediksi"]
    table = ttk.Treeview(table_frame, columns=columns, show="headings")
    for col in columns:
        table.heading(col, text=col)
        table.column(col, width=100, anchor="center")

    for i, (actual, predicted) in enumerate(zip(total_flux, flux_predictions)):
        table.insert("", "end", values=(i, f"{actual:.2f}", f"{predicted:.2f}"))

    table.grid(row=0, column=0)

    # Menampilkan MSE dan akurasi
    stats_frame = ttk.Frame(result_window)
    stats_frame.grid(row=1, column=0, padx=10, pady=10, columnspan=2)

    ttk.Label(stats_frame, text=f"MSE: {mse:.4f}").grid(row=0, column=0, sticky="w")
    ttk.Label(stats_frame, text=f"Akurasi (R²): {accuracy:.4f}").grid(row=1, column=0, sticky="w")

# GUI utama
root = tk.Tk()
root.title("Simulasi Flux Neutron 2D")

frame = ttk.Frame(root)
frame.grid(row=0, column=0, padx=10, pady=10)

# Input parameter
ttk.Label(frame, text="Grid Size:").grid(row=0, column=0, sticky="w")
grid_size_entry = ttk.Entry(frame)
grid_size_entry.grid(row=0, column=1)
grid_size_entry.insert(0, "50")

ttk.Label(frame, text="D (Difusi):").grid(row=1, column=0, sticky="w")
D_entry = ttk.Entry(frame)
D_entry.grid(row=1, column=1)
D_entry.insert(0, "1.0")

ttk.Label(frame, text="Sigma_a (Absorpsi):").grid(row=2, column=0, sticky="w")
Sigma_a_entry = ttk.Entry(frame)
Sigma_a_entry.grid(row=2, column=1)
Sigma_a_entry.insert(0, "0.1")

ttk.Label(frame, text="S (Sumber):").grid(row=3, column=0, sticky="w")
S_entry = ttk.Entry(frame)
S_entry.grid(row=3, column=1)
S_entry.insert(0, "1.0")

ttk.Label(frame, text="Time Steps:").grid(row=4, column=0, sticky="w")
time_steps_entry = ttk.Entry(frame)
time_steps_entry.grid(row=4, column=1)
time_steps_entry.insert(0, "300")

# Tombol kontrol
ttk.Button(frame, text="Run Simulation", command=run_simulation).grid(row=5, column=0, pady=5, columnspan=2)
ttk.Button(frame, text="Start Animation", command=start_animation).grid(row=6, column=0, pady=5, columnspan=2)
ttk.Button(frame, text="Stop Animation", command=stop_animation).grid(row=7, column=0, pady=5, columnspan=2)
ttk.Button(frame, text="Save Animation", command=save_animation).grid(row=8, column=0, pady=5, columnspan=2)
ttk.Button(frame, text="Save Data", command=save_data).grid(row=9, column=0, pady=5, columnspan=2)
ttk.Button(frame, text="Train Regression Model", command=train_regression_model).grid(row=10, column=0, pady=5, columnspan=2)

# Matplotlib Figure
fig, ax = plt.subplots(figsize=(6, 6))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=0, column=1)

root.mainloop()
