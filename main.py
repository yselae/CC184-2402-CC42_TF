#Librerias
import heapq as hq
import pandas as pd
import networkx as nx
import math
import folium
from folium import Marker, PolyLine
from folium.plugins import MiniMap
from folium.plugins import MarkerCluster
import webbrowser
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter import messagebox, ttk

# Function to correct decimal placement in coordinates
def correct_decimal_placement(value):
    value_str = str(value)
    if '.' in value_str:
        value_str = value_str.split('.')[0]
    if value < 0:
        return float(value_str[:3] + '.' + value_str[3:])
    else:
        return float(value_str[:2] + '.' + value_str[2:])

#Leer los archivos XLSX
paraderos_path = 'paraderos.xlsx'
puntos_recarga_path = 'puntos_recarga.xlsx'

paraderos_df = pd.read_excel(paraderos_path).head(50)
puntos_recarga_df = pd.read_excel(puntos_recarga_path).head(50)
paraderos_df['Latitud'] = paraderos_df['Latitud'].apply(correct_decimal_placement)
paraderos_df['Longitud'] = paraderos_df['Longitud'].apply(correct_decimal_placement)
puntos_recarga_df['Latitud'] = puntos_recarga_df['Latitud'].apply(correct_decimal_placement)
puntos_recarga_df['Longitud'] = puntos_recarga_df['Longitud'].apply(correct_decimal_placement)

#Crear un grafo no dirigido
G = nx.Graph()

# Función para calcular la distancia euclidiana en km entre dos puntos geográficos
def euclidean_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Radio de la Tierra en km
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    a = min(1, max(0, a))  # Asegurar que 'a' esté entre 0 y 1
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

# Agregar nodos y aristas al grafo
for _, row in paraderos_df.iterrows():
    G.add_node(row['Nombre'], pos=(row['Latitud'], row['Longitud']), tipo='paradero')

for _, row in puntos_recarga_df.iterrows():
    G.add_node(row['Nombre'], pos=(row['Latitud'], row['Longitud']), tipo='punto_recarga')

for node1, data1 in G.nodes(data=True):
    for node2, data2 in G.nodes(data=True):
        if node1 != node2:
            dist = euclidean_distance(data1['pos'][0], data1['pos'][1], data2['pos'][0], data2['pos'][1])
            G.add_edge(node1, node2, weight=dist)

# Algoritmo de Dijkstra
def dijkstra(start, end):
    if start not in G.nodes or end not in G.nodes:
        messagebox.showerror("Error", "Uno o ambos nodos no existen en el grafo.")
        return None, None

    distances = {node: float('inf') for node in G.nodes}
    distances[start] = 0
    previous_nodes = {node: None for node in G.nodes}
    priority_queue = [(0, start)]

    while priority_queue:
        current_distance, current_node = hq.heappop(priority_queue)
        if current_node == end:
            break

        for neighbor in G.neighbors(current_node):
            edge_weight = G[current_node][neighbor]['weight']
            new_distance = current_distance + edge_weight

            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous_nodes[neighbor] = current_node
                hq.heappush(priority_queue, (new_distance, neighbor))

    # Reconstruir el camino
    path = []
    current = end
    while current is not None:
        path.insert(0, current)
        current = previous_nodes[current]

    if distances[end] == float('inf'):
        messagebox.showinfo("Sin Ruta", "No hay una ruta disponible entre los nodos seleccionados.")
        return None, None

    return path, distances[end]

# Función para mostrar el mapa con una ruta
def mostrar_ruta(path):
    # Crear el mapa centrado en Lima
    mapa = folium.Map(location=[-12.0464, -77.0428], zoom_start=12)

    # Agregar un clúster para los marcadores
    marker_cluster = MarkerCluster().add_to(mapa)

    # Agregar nodos del camino al clúster
    for node in path:
        data = G.nodes[node]
        Marker(
            data['pos'], 
            popup=f"{node}", 
            icon=folium.Icon(color='blue')
        ).add_to(marker_cluster)

    # Dibujar líneas entre los nodos del camino y agregar tooltips con distancias
    for i in range(len(path) - 1):
        start, end = path[i], path[i + 1]
        start_coords = G.nodes[start]['pos']
        end_coords = G.nodes[end]['pos']
        distance = G[start][end]['weight']
        PolyLine(
            [start_coords, end_coords],
            color='red',
            tooltip=f"Distancia: {distance:.2f} km"
        ).add_to(mapa)

    # Agregar puntos de recarga al clúster
    for _, row in puntos_recarga_df.iterrows():
        Marker(
            location=[row["Latitud"], row["Longitud"]],
            popup=row["Nombre"],
            icon=folium.Icon(color="green")
        ).add_to(marker_cluster)

    # Guardar el mapa y abrirlo en el navegador
    mapa.save("ruta_optima.html")
    webbrowser.open("ruta_optima.html")

# Función para calcular la distancia mínima entre dos nodos (paraderos o puntos de recarga)
def calcular_minima_distancia(start, end):
    if start == end:
        messagebox.showinfo("Error", "Seleccione nodos diferentes.")
        return
    path, distance = dijkstra(start, end)
    if path:
        mostrar_ruta(path)
        messagebox.showinfo("Ruta", f"Ruta: {' -> '.join(path)}\nDistancia total: {distance:.2f} km")

# Función para agregar un nuevo nodo
def agregar_nuevo_nodo(latitud, longitud, tipo, nombre, corredor=""):
    try:
        # Validar y convertir las entradas
        latitud = float(latitud)
        longitud = float(longitud)

        if not nombre.strip():
            raise ValueError("El nombre no puede estar vacío.")

        if nombre in G.nodes:
            raise ValueError(f"El nodo '{nombre}' ya existe en el grafo.")

        # Agregar el nuevo nodo al grafo
        G.add_node(nombre, pos=(latitud, longitud), tipo=tipo)

        # Conectar el nuevo nodo con los existentes
        for nodo in G.nodes:
            if nodo != nombre:
                distancia = euclidean_distance(latitud, longitud, G.nodes[nodo]['pos'][0], G.nodes[nodo]['pos'][1])
                G.add_edge(nombre, nodo, weight=distancia)

        # Asegurarse de que las columnas coincidan con el DataFrame
        global paraderos_df
        expected_columns = ["X", "Y", "Nombre", "Latitud", "Longitud", "Corredor"]
        nuevo_paradero = pd.DataFrame([["", "", nombre, latitud, longitud, corredor]], columns=expected_columns)

        # Agregar al DataFrame y sobrescribir el archivo
        paraderos_df = pd.concat([paraderos_df, nuevo_paradero], ignore_index=True)
        paraderos_df.to_excel(paraderos_path, index=False)

        # Confirmar éxito
        messagebox.showinfo("Éxito", f"Nodo '{nombre}' agregado exitosamente.")

    except ValueError as e:
        messagebox.showerror("Error de Validación", f"Datos inválidos: {e}")
    except Exception as e:
        messagebox.showerror("Error Inesperado", f"Se produjo un error: {e}")

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
    background_image = Image.open("fondo.png") 
    background_image = background_image.resize((900, 650), Image.Resampling.LANCZOS)
    bg_image = ImageTk.PhotoImage(background_image)
    bg_label = tk.Label(ventana, image=bg_image)
    bg_label.place(relwidth=1, relheight=1)

     # Título principal
    titulo_label = tk.Label(
        ventana, text="Bienvenido a Optimización de Rutas", font=("Helvetica", 24, "bold"),
        foreground='white', background='grey'
    )
    titulo_label.place(x=170, y=60)

    frame_campos = tk.Frame(ventana, bg='grey')
    frame_campos.place(relx=0.5, rely=0.15, anchor='n')

    # Etiqueta y ComboBox para el paradero de origen
    ttk.Label(ventana, text="Paradero de origen:", foreground='white', background='grey').place(x=50, y=185)
    origen_combo = ttk.Combobox(ventana, values=paraderos["Nombre"].tolist(), width=35)
    origen_combo.place(x=180, y=180)

    # Etiqueta y ComboBox para el paradero de destino
    ttk.Label(ventana, text="Paradero de destino:", foreground='white', background='grey').place(x=50, y=230)
    destino_combo = ttk.Combobox(ventana, values=paraderos["Nombre"].tolist(), width=35)
    destino_combo.place(x=180, y=230)

    # Botón para encontrar la ruta
    find_route_button = tk.Button(
        ventana,
        text="ENCONTRAR RUTA",
        bg="#0077b6",
        foreground='white',
        font=("Helvetica", 10, "bold"),
        command=lambda: calcular_minima_distancia(origen_combo.get(), destino_combo.get())
    )
    find_route_button.place(x=150, y=270, width=160, height=45)

    # Sección para agregar un nuevo punto
    ttk.Label(ventana, text="Agregar Punto", font=("Helvetica", 14, "bold"), foreground='white', background='grey').place(x=570, y=140)

    # Campos para agregar un nuevo punto
    ttk.Label(ventana, text="Nombre:", foreground='white', background='grey').place(x=520, y=190)
    name_entry = tk.Entry(ventana, width=30)
    name_entry.place(x=580, y=190)

    # Entradas para coordenadas X y Y en una misma línea
    ttk.Label(ventana, text="X:", foreground='white', background='grey').place(x=480, y=230)
    lat_entry = tk.Entry(ventana)
    lat_entry.place(x=510, y=230)

    ttk.Label(ventana, text="Y:", foreground='white', background='grey').place(x=670, y=230)
    lon_entry = tk.Entry(ventana)
    lon_entry.place(x=700, y=230)

    # Botón para agregar un nuevo punto
    tk.Button(
        ventana,
        text="AGREGAR",
        font=("Helvetica", 10),
        bg="#6a994e",
        fg="white",
        command=lambda: agregar_nuevo_nodo(lat_entry.get(), lon_entry.get(), "paradero", name_entry.get())
        ).place(x=565, y=270, width=160, height=45)

    # Botones adicionales para otras funcionalidades
    button_frame = tk.Frame(ventana, bg='grey')
    button_frame.place(x=50, y=350, width=800, height=200)

    # Dimensiones para botones
    button_width = 22
    button_height = 2

    # Botones organizados en filas y columnas con colores de fondo correspondientes y sus respectivas funcionalidades
    tk.Button(button_frame, text="MOSTRAR MAPA", bg="Steel Blue", fg="white", width=button_width, height=button_height, command=mostrar_mapa).grid(row=1, column=0, padx=10, pady=10, sticky="ew")
    tk.Button(button_frame, text="MOSTRAR PUNTOS DE RECARGA", bg="Dark Green", fg="white", width=button_width, height=button_height, command=mostrar_puntos_recarga).grid(row=2, column=0, padx=10, pady=10, sticky="ew")
    tk.Button(button_frame, text="MOSTRAR GRAFO", bg="Firebrick", fg="white", width=button_width, height=button_height, command=mostrar_ventana_seleccion_grafo).grid(row=3, column=0, padx=10, pady=10, sticky="ew")
    tk.Button(button_frame, text="PARADEROS MORADO", bg="Indigo", fg="white", width=button_width, height=button_height, command=lambda: mostrar_paraderos_por_color("Morado", "purple")).grid(row=1, column=1, padx=10, pady=10, sticky="ew")
    tk.Button(button_frame, text="PARADEROS ROJO", bg="Dark Red", fg="white", width=button_width, height=button_height, command=lambda: mostrar_paraderos_por_color("Rojo", "red")).grid(row=2, column=1, padx=10, pady=10, sticky="ew")
    tk.Button(button_frame, text="PARADEROS AZUL", bg="Midnight Blue", fg="white", width=button_width, height=button_height, command=lambda: mostrar_paraderos_por_color("Azul", "blue")).grid(row=3, column=1, padx=10, pady=10, sticky="ew")

    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=1)

    ventana.mainloop()

# Iniciar la aplicación
if __name__ == "__main__":
    iniciar_interfaz()