import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import folium
from folium.plugins import MarkerCluster
from folium import PolyLine, Marker
import pandas as pd
import networkx as nx
import math
import webbrowser
from PIL import Image, ImageTk

# Función para calcular la distancia euclidiana en km entre dos puntos geográficos
def euclidean_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Radio de la Tierra en km
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# Función para aplicar el punto decimal después del segundo dígito
def format_coordinates(coord):
    try:
        return float(f"{str(int(coord))[:3]}.{str(int(coord))[3:]}")
    except Exception:
        return None

# Procesar datos desde los archivos Excel
def process_data(file_path, lat_col, lon_col, name_col=None, corredor_col=None):
    df = pd.read_excel(file_path)
    columns = [lat_col, lon_col] + ([name_col] if name_col else []) + ([corredor_col] if corredor_col else [])
    df = df[columns].dropna()
    df[lat_col] = df[lat_col].apply(format_coordinates)
    df[lon_col] = df[lon_col].apply(format_coordinates)
    return df.dropna()

# Cargar datos de paraderos y puntos de recarga
paraderos = process_data("paraderos.xlsx", "Latitud", "Longitud", "Nombre", "Corredor")
puntos_recarga = process_data("puntos_recarga.xlsx", "Latitud", "Longitud", "Nombre")

# Función para mostrar mapa vacío
def mostrar_mapa():
    try:
        mapa = folium.Map(location=[-12.0464, -77.0428], zoom_start=12)
        map_file = "map_limpio.html"
        mapa.save(map_file)
        webbrowser.open(map_file)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo mostrar el mapa vacío: {e}")

# Función para mostrar puntos de recarga
def mostrar_puntos_recarga():
    try:
        mapa = folium.Map(location=[-12.0464, -77.0428], zoom_start=12)
        marker_cluster = MarkerCluster().add_to(mapa)
        for _, row in puntos_recarga.iterrows():
            Marker(
                location=[row["Latitud"], row["Longitud"]],
                popup=row["Nombre"],
                icon=folium.Icon(color="green")
            ).add_to(marker_cluster)
        map_file = "map_puntos_recarga.html"
        mapa.save(map_file)
        webbrowser.open(map_file)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo mostrar los puntos de recarga: {e}")

# Función para mostrar solo los nodos de un corredor específico
def mostrar_paraderos_por_color(corredor, color_iconos):
    try:
        paraderos_corredor = paraderos[paraderos["Corredor"] == corredor]
        mapa = folium.Map(location=[-12.0464, -77.0428], zoom_start=12)
        for _, row in paraderos_corredor.iterrows():
            Marker(
                location=[row["Latitud"], row["Longitud"]],
                popup=row["Nombre"],
                icon=folium.Icon(color=color_iconos)
            ).add_to(mapa)
        map_file = f"map_paraderos_{corredor.lower()}.html"
        mapa.save(map_file)
        webbrowser.open(map_file)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo mostrar los paraderos del corredor {corredor}: {e}")

# Función para generar y mostrar el grafo completo de un corredor
def generar_grafo_completo(corredor, color_lineas, color_iconos):
    try:
        paraderos_corredor = paraderos[paraderos["Corredor"] == corredor]
        if paraderos_corredor.empty:
            messagebox.showinfo("Información", f"No hay datos para el corredor {corredor}.")
            return

        # Crear grafo
        grafo = nx.Graph()
        for i, row1 in paraderos_corredor.iterrows():
            for j, row2 in paraderos_corredor.iterrows():
                if i != j:
                    dist = euclidean_distance(row1["Latitud"], row1["Longitud"],
                                              row2["Latitud"], row2["Longitud"])
                    grafo.add_edge(i, j, weight=dist)

        # Crear el mapa
        mapa = folium.Map(location=[-12.0464, -77.0428], zoom_start=12)

        # Agregar nodos al mapa
        for idx, row in paraderos_corredor.iterrows():
            Marker(
                location=[row["Latitud"], row["Longitud"]],
                popup=row["Nombre"],
                icon=folium.Icon(color=color_iconos)
            ).add_to(mapa)

        # Agregar puntos de recarga al mapa
        marker_cluster = MarkerCluster().add_to(mapa)
        for _, row in puntos_recarga.iterrows():
            Marker(
                location=[row["Latitud"], row["Longitud"]],
                popup=row["Nombre"],
                icon=folium.Icon(color="green")
            ).add_to(marker_cluster)

        # Dibujar las conexiones del grafo
        for edge in grafo.edges():
            idx1, idx2 = edge
            row1 = paraderos_corredor.loc[idx1]
            row2 = paraderos_corredor.loc[idx2]
            PolyLine(
                locations=[
                    [row1["Latitud"], row1["Longitud"]],
                    [row2["Latitud"], row2["Longitud"]]
                ],
                color=color_lineas,
                weight=2
            ).add_to(mapa)

        # Guardar y abrir el mapa
        map_file = f"grafo_{corredor.lower()}.html"
        mapa.save(map_file)
        webbrowser.open(map_file)

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el grafo del corredor {corredor}: {e}")

# Función para mostrar ventana de selección de grafo
def mostrar_ventana_seleccion_grafo():
    ventana_grafo = tk.Toplevel()
    ventana_grafo.title("Seleccionar Grafo")
    ventana_grafo.geometry("300x200")

    tk.Label(ventana_grafo, text="Seleccione el grafo a mostrar:").pack(pady=10)

    tk.Button(
        ventana_grafo, text="Grafo Corredor Rojo", bg="#e63946", fg="white",
        command=lambda: [generar_grafo_completo("Rojo", "red", "red"), ventana_grafo.destroy()]
    ).pack(pady=5)

    tk.Button(
        ventana_grafo, text="Grafo Corredor Morado", bg="#9c27b0", fg="white",
        command=lambda: [generar_grafo_completo("Morado", "purple", "purple"), ventana_grafo.destroy()]
    ).pack(pady=5)

    tk.Button(
        ventana_grafo, text="Grafo Corredor Azul", bg="#1e3a8a", fg="white",
        command=lambda: [generar_grafo_completo("Azul", "blue", "blue"), ventana_grafo.destroy()]
    ).pack(pady=5)

#Interfaz
# Crear la interfaz principal
def iniciar_interfaz():
    ventana = tk.Tk()
    ventana.title("Optimización de rutas de transporte")
    ventana.geometry("900x650")

    # Fondo de la interfaz
    background_image = Image.open("fondo1.png") 
    background_image = background_image.resize((900, 650), Image.Resampling.LANCZOS)
    bg_image = ImageTk.PhotoImage(background_image)
    bg_label = tk.Label(ventana, image=bg_image)
    bg_label.place(relwidth=1, relheight=1)

     # Título principal
    titulo_label = tk.Label(
        ventana, text="Bienvenido a Optimización de Rutas", font=("Helvetica", 24, "bold"),
        foreground='white', background='grey'
    )
    titulo_label.place(x=170, y=20)

    frame_campos = tk.Frame(ventana, bg='grey')
    frame_campos.place(relx=0.5, rely=0.15, anchor='n')

    # Etiqueta y ComboBox para el paradero de origen
    ttk.Label(ventana, text="Paradero de origen:", foreground='white', background='grey').place(x=50, y=100)
    origen_combo = ttk.Combobox(ventana, values=paraderos["Nombre"].tolist(), width=35)
    origen_combo.place(x=180, y=100)

    # Etiqueta y ComboBox para el paradero de destino
    ttk.Label(ventana, text="Paradero de destino:", foreground='white', background='grey').place(x=50, y=140)
    destino_combo = ttk.Combobox(ventana, values=paraderos["Nombre"].tolist(), width=35)
    destino_combo.place(x=180, y=140)

    # Botón para encontrar la ruta
    find_route_button = tk.Button(
        ventana,
        text="ENCONTRAR RUTA",
        bg="#0077b6",
        foreground='white',
        font=("Helvetica", 10, "bold"),
        command=lambda: calcular_minima_distancia(origen_combo.get(), destino_combo.get())
    )
    find_route_button.place(x=150, y=190, width=160, height=45)

    # Sección para agregar un nuevo punto
    ttk.Label(ventana, text="Agregar Punto", font=("Helvetica", 14, "bold"), foreground='white', background='grey').place(x=600, y=100)

    # Campos para agregar un nuevo punto
    ttk.Label(ventana, text="Nombre:", foreground='white', background='grey').place(x=520, y=150)
    name_entry = tk.Entry(ventana, width=30)
    name_entry.place(x=580, y=150)

    # Entradas para coordenadas X y Y en una misma línea
    ttk.Label(ventana, text="X:", foreground='white', background='grey').place(x=480, y=170)
    x_entry = tk.Entry(ventana)
    x_entry.place(x=510, y=190)

    ttk.Label(ventana, text="Y:", foreground='white', background='grey').place(x=670, y=170)
    y_entry = tk.Entry(ventana)
    y_entry.place(x=700, y=190)

    # Botón para agregar un nuevo punto
    add_button = tk.Button(
        ventana,
        text="AGREGAR",
        font=("Helvetica", 12),
        bg="#6a994e",
        fg="white",
        command=lambda: solicitar_nuevo_nodo(name_entry.get(), x_entry.get(), y_entry.get())
        )
    add_button.place(x=50, y=400, width=200, height=40)

    # Botones adicionales para otras funcionalidades
    button_frame = tk.Frame(ventana, bg='grey')
    button_frame.place(x=50, y=350, width=800, height=200)

    # Dimensiones para botones
    button_width = 22
    button_height = 2

    # Botones organizados en filas y columnas con colores de fondo correspondientes y sus respectivas funcionalidades
    tk.Button(button_frame, text="MOSTRAR MAPA", bg="#90e0ef", fg="white", width=button_width, height=button_height, command=mostrar_mapa).grid(row=1, column=0, padx=10, pady=10, sticky="ew")
    tk.Button(button_frame, text="MOSTRAR PUNTOS DE RECARGA", bg="#ffd60a", fg="white", width=button_width, height=button_height, command=mostrar_puntos_recarga).grid(row=2, column=0, padx=10, pady=10, sticky="ew")
    tk.Button(button_frame, text="MOSTRAR GRAFO", bg="#ff6b6b", fg="white", width=button_width, height=button_height, command=mostrar_ventana_seleccion_grafo).grid(row=3, column=0, padx=10, pady=10, sticky="ew")
    tk.Button(button_frame, text="PARADEROS MORADO", bg="#9c27b0", fg="white", width=button_width, height=button_height, command=lambda: mostrar_paraderos_por_color("Morado", "purple")).grid(row=1, column=1, padx=10, pady=10, sticky="ew")
    tk.Button(button_frame, text="PARADEROS ROJO", bg="#e63946", fg="white", width=button_width, height=button_height, command=lambda: mostrar_paraderos_por_color("Rojo", "red")).grid(row=2, column=1, padx=10, pady=10, sticky="ew")
    tk.Button(button_frame, text="PARADEROS AZUL", bg="#1e3a8a", fg="white", width=button_width, height=button_height, command=lambda: mostrar_paraderos_por_color("Azul", "blue")).grid(row=3, column=1, padx=10, pady=10, sticky="ew")

    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=1)


    ventana.mainloop()

# Iniciar la aplicación
if __name__ == "__main__":
    iniciar_interfaz()