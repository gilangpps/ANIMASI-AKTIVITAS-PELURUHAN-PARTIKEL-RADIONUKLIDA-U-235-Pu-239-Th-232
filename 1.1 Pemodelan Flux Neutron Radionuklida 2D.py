import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Fungsi untuk menghitung flux neutron 2D menggunakan metode iterasi defisi

def calculate_flux(shape, D, Sigma_a, S, max_iter=500, tol=1e-5):
    nx, ny = shape
    flux = np.zeros((nx, ny))
    for _ in range(max_iter):
        flux_new = np.copy(flux)
        for i in range(1, nx - 1):
            for j in range(1, ny - 1):
                flux_new[i, j] = (S[i, j] + D * (flux[i+1, j] + flux[i-1, j] + flux[i, j+1] + flux[i, j-1])) / (4 * D + Sigma_a[i, j])
        if np.linalg.norm(flux_new - flux) < tol:
            break
        flux = flux_new
    return flux

# Fungsi untuk animasi

def update(frame, im, flux_list):
    im.set_array(flux_list[frame])
    return [im]

# GUI Utama

def main():
    # Parameter Fisik
    nx, ny = 50, 50
    D = 1.0  # Koefisien difusi (cm^2/s)
    Sigma_a = np.full((nx, ny), 0.02)  # Laju absorbsi neutron (/cm)
    S = np.zeros((nx, ny))  # Sumber neutron (neutron/cm^3/s)
    S[nx//2, ny//2] = 1.0  # Sumber di pusat reaktor

    flux = calculate_flux((nx, ny), D, Sigma_a, S)

    # List untuk animasi (flux dari iterasi awal hingga akhir)
    flux_list = [calculate_flux((nx, ny), D, Sigma_a, S, max_iter=i) for i in range(1, 50)]

    # GUI
    root = tk.Tk()
    root.title("Pemodelan Flux Neutron 2D - U-235")

    # Frame untuk grafik
    frame_graph = ttk.Frame(root)
    frame_graph.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    fig, ax = plt.subplots()
    im = ax.imshow(flux, cmap="hot", interpolation="nearest", origin="lower")
    plt.colorbar(im, ax=ax, label="Flux Neutron (1/cm^2/s)")
    ax.set_title("Distribusi Flux Neutron")

    canvas = FigureCanvasTkAgg(fig, master=frame_graph)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(fill=tk.BOTH, expand=True)

    # Animasi
    ani = FuncAnimation(fig, update, frames=len(flux_list), fargs=(im, flux_list), interval=100, blit=True)

    # Frame untuk parameter fisika
    frame_params = ttk.Frame(root)
    frame_params.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10)

    ttk.Label(frame_params, text="Parameter Fisik", font=("Arial", 14, "bold")).pack(anchor=tk.W)

    ttk.Label(frame_params, text=f"Koefisien Difusi (D): {D} cm^2/s").pack(anchor=tk.W)
    ttk.Label(frame_params, text=f"Laju Absorbsi (Sigma_a): {Sigma_a[0, 0]} /cm").pack(anchor=tk.W)
    ttk.Label(frame_params, text=f"Sumber Neutron (S): {S[nx//2, ny//2]} neutron/cm^3/s").pack(anchor=tk.W)

    root.mainloop()

if __name__ == "__main__":
    main()
