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
import io
import os
import base64

G_transport = nx.Graph()
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

def correct_decimal_placement(value):
    value_str = str(value)
    if '.' in value_str:
        value_str = value_str.split('.')[0]  
    if value < 0:
        return float(value_str[:3] + '.' + value_str[3:])
    else:
        return float(value_str[:2] + '.' + value_str[2:])
    
# Apply the correction to the Latitud and Longitud columns in both dataframes
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

#Calcular la distancia euclidiana entre dos puntos
def euclidean_distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

#Agregar nodos (paraderos) al grafo
for _, row in paraderos_df.iterrows():
    G.add_node(row['Nombre'], pos=(row['Latitud'], row['Longitud']), tipo='paradero')
    
#Añadir nodos de puntos de recarga
for _, row in puntos_recarga_df.iterrows():
    G.add_node(row['Nombre'], pos=(row['Latitud'], row['Longitud']), tipo='punto_recarga', direccion=row['Direccion'], horario=row['Horario'])

#Agregar aristas entre los paraderos usando la distancia como peso
for i, row1 in paraderos_df.iterrows():
    for j, row2 in paraderos_df.iterrows():
        if i < j:
            distancia = euclidean_distance(row1['X'], row1['Y'], row2['X'], row2['Y'])
            G.add_edge(row1['Nombre'], row2['Nombre'], weight=distancia)  

#Calcular la distancia promedio de las aristas
distancias = {edge: data['weight'] for edge, data in G.edges.items()}
promedio_distancia = sum(distancias.values()) / len(distancias)

#Función para mostrar el camino más corto en un mapa
def show_map(path=None):
    # Initialize the map centered around Lima (approximately)
    m = folium.Map(location=[-12.0464, -77.0428], zoom_start=12)

    # Add paraderos (stops) as nodes
    for _, row in paraderos_df.iterrows():
        folium.Marker(
            location=[row['Latitud'], row['Longitud']],
            popup=row['Nombre'],
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)

    # Add puntos de recarga (charging points) as nodes
    for _, row in puntos_recarga_df.iterrows():
        folium.Marker(
            location=[row['Latitud'], row['Longitud']],
            popup=row['Nombre'],
            icon=folium.Icon(color="green", icon="info-sign")
        ).add_to(m)

    # Add path edges to map
    for i in range(len(path) - 1):
        node_start = path[i]
        node_end = path[i + 1]
        start_coords = (graph.nodes[node_start]['Latitud'], graph.nodes[node_start]['Longitud'])
        end_coords = (graph.nodes[node_end]['Latitud'], graph.nodes[node_end]['Longitud'])
        
        # Draw a line between each consecutive nodes in path
        folium.PolyLine(locations=[start_coords, end_coords], color="red", weight=2.5, opacity=1).add_to(m)

    # Save map as HTML
    map_output_path = '/mnt/data/optimized_route_map.html'
    m.save(map_output_path)

    # Open the map in the default web browser
    webbrowser.open(map_output_path)
    mapa_lima = folium.Map(location=[-12.0464, -77.0428], zoom_start=12) #Mapa Centro de Lima
    minimap = MiniMap()
    mapa_lima.add_child(minimap)
    
    #Añadir paraderos al mapa
    for _, row in paraderos_df.iterrows():
        color = 'red' if path and row['Nombre'] in path else 'blue'
        Marker(
            [row['Latitud'], row['Longitud']],
            popup=row['Nombre'],
            icon=folium.Icon(color=color)
        ).add_to(mapa_lima)
    
    #Añadir puntos de recarga al mapa
    for _, row in puntos_recarga_df.iterrows():
        Marker(
            [row['Latitud'], row['Longitud']],
            popup=row['Nombre'],
            icon=folium.Icon(color='green')
        ).add_to(mapa_lima)

#Agregar las líneas (aristas) entre los paraderos
    for (inicio, fin), data in G.edges.items():
        pos_inicio = G.nodes[inicio]['pos']
        pos_fin = G.nodes[fin]['pos']
        
        #Verificar si la arista (inicio, fin) está en el camino mínimo
        if path and inicio in path and fin in path:
            idx_inicio = path.index(inicio)
            color = 'red' if idx_inicio < len(path) - 1 and path[idx_inicio + 1] == fin else 'blue'
        else:
            #Aristas de color azul si están debajo de la distancia promedio, gris en caso contrario
            color = 'blue' if data['weight'] <= promedio_distancia else 'gray'
        
        #Añadir la línea con el color determinado
        PolyLine(
            locations=[(pos_inicio[0], pos_inicio[1]), (pos_fin[0], pos_fin[1])],
            color=color,
            weight=2,
            tooltip=f'Distancia: {data["weight"]:.2f} km'
        ).add_to(mapa_lima)
        
    #Muestra el mapa
    display_map(mapa_lima)

#Algoritmo de Dijkstra para encontrar el camino más corto  
def dijkstra(start, end):
    #Inicializar costos y predecesores para cada nodo
    costs = {node: float('inf') for node in G.nodes}
    predecessors = {node: None for node in G.nodes}
    costs[start] = 0  
    queue = [(0, start)]  #Cola de prioridad para los nodos por visitar

    while queue:
        current_cost, current_node = hq.heappop(queue)  #Extraer el nodo con el menor costo
        if current_node == end:
            break  

        for neighbor in G.neighbors(current_node):
            #Obtener el peso de la arista entre current_node y neighbor
            distance = G[current_node][neighbor].get('weight', float('inf'))
            cost = current_cost + distance  #Calcula el nuevo costo

            #Actualizar costo y predecesor si se encontró un camino más corto
            if cost < costs[neighbor]:
                costs[neighbor] = cost
                predecessors[neighbor] = current_node
                hq.heappush(queue, (cost, neighbor))  #Añadir a la cola de prioridad

    #Construir el camino de salida a partir de los predecesores
    path = []
    step = end
    while step is not None:
        path.append(step)
        step = predecessors[step]
    path.reverse()  #Invertir el camino para ir del inicio al fin

    #Mostrar el mapa con la ruta resaltada
    if costs[end] == float('inf'):
        return None, None
    else:
        show_map(path)  #Muestra el mapa con la ruta
        return path, costs[end]  #Retorna el camino y la distancia total

#Crear un diccionario para almacenar las distancias entre los paraderos y puntos de recarga conectados
distancias = {}
for i, row1 in paraderos_df.iterrows():
    for j, row2 in paraderos_df.iterrows():
        if i < j:
            distancia = euclidean_distance(row1['X'], row1['Y'], row2['X'], row2['Y'])
            distancias[(row1['Nombre'], row2['Nombre'])] = distancia
            distancias[(row2['Nombre'], row1['Nombre'])] = distancia 

#Calcula la distancia promedio
promedio_distancia = sum(distancias.values()) / len(distancias)

#Función para mostrar el mapa en el navegador
def display_map(map_object):
    data = io.BytesIO()  #Crea un buffer en memoria para guardar los datos del mapa
    map_object.save(data, close_file=False)  #Guarda el mapa en el buffer
    encoded_map = base64.b64encode(data.getvalue()).decode('utf-8')  # Codifica el mapa en base64
    html = f"<html><body><iframe src='data:text/html;base64,{encoded_map}' width='100%' height='100%' style='border:none;'></iframe></body></html>"  #Crea una cadena HTML con el mapa
    with open("map.html", "w") as file:
        file.write(html)  #Escribe el HTML en un archivo
    webbrowser.open('file://' + os.path.realpath("map.html"))  #Abre el archivo en el navegador

#Función para mostrar el grafo de paraderos y puntos de recarga
def show_transport_graph():
    G_transport = nx.Graph()
    G_transport = nx.Graph() 
    for _, row in paraderos_df.iterrows():
        G_transport.add_node(row['Nombre'], pos=(row['Latitud'], row['Longitud']), tipo='paradero')
    
    for _, row in puntos_recarga_df.iterrows():
        G_transport.add_node(row['Nombre'], pos=(row['Latitud'], row['Longitud']), tipo='punto_recarga')

#Añadir aristas entre paraderos con las distancias como peso
# Create a complete graph by connecting every node with every other node
for node1 in G_transport.nodes:
    for node2 in G_transport.nodes:
        if node1 != node2:
            distancia = euclidean_distance(G_transport.nodes[node1]['pos'][0], G_transport.nodes[node1]['pos'][1],
                                      G_transport.nodes[node2]['pos'][0], G_transport.nodes[node2]['pos'][1])
            G_transport.add_edge(node1, node2, weight=distancia)
        G_transport.add_edge(inicio, fin, weight=distancia)

    #Obtener posiciones para todos los nodos del grafo
    pos = {node: (data['pos'][1], data['pos'][0]) for node, data in G_transport.nodes(data=True)}
    
    #Configurar el gráfico
    plt.figure(figsize=(14, 12))
    nx.draw(G_transport, pos, with_labels=True, node_color='skyblue', edge_color='gray', node_size=500, font_size=8)
    
    #Añadir etiquetas a las aristas con las distancias
    edge_labels = {edge: f'{data["weight"]:.2f}' for edge, data in G_transport.edges.items()}
    nx.draw_networkx_edge_labels(G_transport, pos, edge_labels=edge_labels, font_color='red', font_size=8)
    plt.title('Grafo de Paraderos y Puntos de Recarga')
    plt.show()

#Función para mostrar el grafo de paraderos y puntos de recarga en un mapa
def show_graph_map():
    mapa_lima = folium.Map(location=[-12.0464, -77.0428], zoom_start=12) 
    minimap = MiniMap() 
    mapa_lima.add_child(minimap)  
    
    #Conjunto para rastrear nodos únicos ya agregados
    nodos_agregados = set()
    nodos_no_agregados = []
    
    #Añadir marcadores para paraderos
    for _, row in paraderos_df.iterrows():
        pos = (row['Latitud'], row['Longitud'])
        if pos not in nodos_agregados:
            try:
                Marker(pos, popup=row['Nombre'], icon=folium.Icon(color='blue')).add_to(mapa_lima)
                nodos_agregados.add(pos)
            except Exception as e:
                nodos_no_agregados.append((row['Nombre'], str(e)))
        else:
            nodos_no_agregados.append((row['Nombre'], "Coordenadas duplicadas, misma latitud y longitud"))

    #Añadir marcadores para puntos de recarga
    for _, row in puntos_recarga_df.iterrows():
        pos = (row['Latitud'], row['Longitud'])
        if pos not in nodos_agregados:
            try:
                Marker(pos, popup=row['Nombre'], icon=folium.Icon(color='green')).add_to(mapa_lima)
                nodos_agregados.add(pos)
            except Exception as e:
                nodos_no_agregados.append((row['Nombre'], str(e)))
        else:
            nodos_no_agregados.append((row['Nombre'], "Coordenadas duplicadas, misma latitud y longitud"))
    
    #Mostrar nodos agregados y errores si existen
    print(f"Nodos agregados: {len(nodos_agregados)}")
    if nodos_no_agregados:
        print("Errores al agregar nodos:")
        for nodo, error in nodos_no_agregados:
            print(f"{nodo}: {error}")

    #Añadir aristas entre paraderos
# Create a complete graph by connecting every node with every other node
for node1 in G_transport.nodes:
    for node2 in G_transport.nodes:
        if node1 != node2:
            distancia = euclidean_distance(G_transport.nodes[node1]['pos'][0], G_transport.nodes[node1]['pos'][1],
                                      G_transport.nodes[node2]['pos'][0], G_transport.nodes[node2]['pos'][1])
            G_transport.add_edge(node1, node2, weight=distancia)
        pos_inicio = (G.nodes[inicio]['pos'][1], G.nodes[inicio]['pos'][0])  #Obtener posición de inicio
        pos_fin = (G.nodes[fin]['pos'][1], G.nodes[fin]['pos'][0])  #Obtener posición de fin
        PolyLine(locations=[pos_inicio, pos_fin], color='blue', weight=2, tooltip=f'Distancia: {distancia:.2f} km').add_to(mapa_lima)
    display_map(mapa_lima)


###################################################################agregar dsp
#Función para actualizar la selección de paradero
def seleccion_paradero(valor, label):
    label.config(text=f"Paradero seleccionado: {valor.get()}")  #Actualiza la etiqueta con el paradero seleccionado
##################################################################

#Función para mostrar el camino mínimo en el grafo del mapa
def show_min_path_graph():
    #Verifica si la variable 'path' está definida y contiene elementos
    if not hasattr(show_min_path_graph, 'path') or show_min_path_graph.path is None:
        messagebox.showwarning("Advertencia", "Primero calcule la distancia mínima.")
        return
    #Llama a la función para mostrar el mapa con el camino mínimo
    show_graph_map(min_path=show_min_path_graph.path)

#Función para agregar un nuevo nodo (paradero o punto de recarga)
def agregar_nuevo_nodo(lat, lon, tipo, nombre, top_level_window):
    nuevo_nodo = nombre  #Nombre para el nuevo nodo
    if tipo == "paradero":
        paraderos_df.loc[len(paraderos_df)] = [nuevo_nodo, lat, lon]  #Añade el nuevo paradero al DataFrame de paraderos
    elif tipo == "punto_recarga":
        puntos_recarga_df.loc[len(puntos_recarga_df)] = [nuevo_nodo, lat, lon, "Direccion", "Horario"]  #Añade el nuevo punto de recarga al DataFrame de puntos de recarga

    #Actualizar grafo
    G.add_node(nuevo_nodo, pos=(lat, lon), tipo=tipo)
    
    #Selecciona nodos aleatorios para conectar el nuevo nodo
    nodos_existentes = list(G.nodes)
    random.shuffle(nodos_existentes)  #Mezcla los nodos existentes
    num_conexiones = random.randint(4, 9)  #Selecciona un número aleatorio de conexiones
    nodos_seleccionados = nodos_existentes[:num_conexiones]
    
    for nodo in nodos_seleccionados:
        if nodo != nuevo_nodo:
            #Calcular distancia euclidiana
            nodo_pos = G.nodes[nodo]['pos']
            distancia = euclidean_distance(lat, lon, nodo_pos[0], nodo_pos[1])
            G.add_edge(nuevo_nodo, nodo, weight=distancia)  #Añade la arista con el peso de la distancia
    
    actualizar_dropdowns()  #Actualiza los menús desplegables
    top_level_window.destroy()  #Cierra la ventana de agregar nodo
    messagebox.showinfo("Confirmación", "Nodo agregado exitosamente")  #Muestra un mensaje de confirmación

# Función para calcular la distancia mínima entre dos nodos (paraderos o puntos de recarga)
def calcular_minima_distancia():
    global path
    start = valor1.get()  #Obtiene el nodo inicial del menú desplegable
    end = valor2.get()  #Obtiene el nodo final del menú desplegable
    
    #Verifica que los nodos seleccionados no sean los mismos
    if start == end:
        messagebox.showinfo("Error", "Selecciona dos nodos diferentes") 
        return
    
    #Calcula el camino y la distancia mínima usando Dijkstra
    path, distance = dijkstra(start, end)
    
    #Verifica si hay una ruta disponible
    if path is None:
        label_distancia.config(text="No hay ruta disponible entre los nodos seleccionados")
    else:
        arista_descriptions = []
        
        #Calcula la descripción de cada arista en el camino
        for i in range(len(path) - 1):
            start_node = path[i]
            end_node = path[i + 1]
            arista = f"{G[start_node][end_node]['weight']:.2f}"
            arista_descriptions.append(arista)
        
        #Construye la descripción de la suma de aristas y distancia
        aristas_sum = " + ".join(arista_descriptions)
        label_distancia.config(
            #Muestra la distancia mínima
            text=f"Ruta: {' -> '.join(path)}\nSuma de las aristas: {aristas_sum}\nDistancia: {distance:.2f} en cientos de kilómetros \nDistancia Real: {distance*100:.2f} km") 
    show_min_path_graph.path = path

#Función para mostrar el grafo en el mapa del nodo agregado (paradero o punto de recarga)
def mostrar_grafo_mapa_nodo_agregado():
    """Muestra el mapa con el último nodo agregado y su nodo más cercano con la arista en rojo."""
    if not hasattr(mostrar_nodo_mas_cercano, 'ultimo_nodo') or not hasattr(mostrar_nodo_mas_cercano, 'nodo_cercano'):
        messagebox.showwarning("Advertencia", "Primero identifique el nodo más cercano al último nodo.")
        return
    mapa_lima = folium.Map(location=[-12.0464, -77.0428], zoom_start=12)
    minimap = MiniMap()
    mapa_lima.add_child(minimap)

    #Obtener las coordenadas del último nodo y del nodo más cercano
    ultimo_nodo = mostrar_nodo_mas_cercano.ultimo_nodo
    nodo_cercano = mostrar_nodo_mas_cercano.nodo_cercano
    ultimas_coords = G.nodes[ultimo_nodo]['pos']
    cercanas_coords = G.nodes[nodo_cercano]['pos']

    #Añadir marcadores para el último nodo y el nodo más cercano
    folium.Marker(ultimas_coords, popup=ultimo_nodo, icon=folium.Icon(color='red')).add_to(mapa_lima)
    folium.Marker(cercanas_coords, popup=nodo_cercano, icon=folium.Icon(color='blue')).add_to(mapa_lima)

    #Calcular la distancia entre el último nodo y el nodo más cercano
    distancia = G[ultimo_nodo][nodo_cercano]['weight']

    #Dibujar una línea roja entre ellos con un tooltip que muestra la distancia
    folium.PolyLine(
        locations=[ultimas_coords, cercanas_coords],
        color='red',
        weight=5,
        tooltip=f'Distancia: {distancia:.2f} cientos de km'
    ).add_to(mapa_lima)
    display_map(mapa_lima)

#Función para solicitar un nuevo nodo (paradero o punto de recarga) con latitud, longitud y nombre
def solicitar_nuevo_nodo(root):
    nuevo_nodo_top = tk.Toplevel(root)
    nuevo_nodo_top.title("Agregar nuevo nodo")
    nuevo_nodo_top.geometry("300x250")

    entry_frame = tk.Frame(nuevo_nodo_top, padx=10, pady=10)
    entry_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    # Entradas para latitud, longitud, tipo y nombre
    tk.Label(entry_frame, text="Latitud:", font=('Helvetica', 12)).grid(row=0, column=0, sticky='w', pady=5)
    lat_entry = tk.Entry(entry_frame, font=('Helvetica', 12), width=25)
    lat_entry.grid(row=0, column=1, pady=5)

    tk.Label(entry_frame, text="Longitud:", font=('Helvetica', 12)).grid(row=1, column=0, sticky='w', pady=5)
    lon_entry = tk.Entry(entry_frame, font=('Helvetica', 12), width=25)
    lon_entry.grid(row=1, column=1, pady=5)

    tk.Label(entry_frame, text="Nombre:", font=('Helvetica', 12)).grid(row=2, column=0, sticky='w', pady=5)
    nombre_entry = tk.Entry(entry_frame, font=('Helvetica', 12), width=25)
    nombre_entry.grid(row=2, column=1, pady=5)

    tk.Label(entry_frame, text="Tipo:", font=('Helvetica', 12)).grid(row=3, column=0, sticky='w', pady=5)
    tipo_combo = ttk.Combobox(entry_frame, font=('Helvetica', 12), values=["paradero", "punto_recarga"])
    tipo_combo.grid(row=3, column=1, pady=5)
    tipo_combo.current(0)

    add_button = tk.Button(entry_frame, text="Agregar", font=('Helvetica', 12),
                           command=lambda: agregar_nuevo_nodo(
                               lat_entry.get(), lon_entry.get(), tipo_combo.get(),
                               nombre_entry.get(), nuevo_nodo_top))
    add_button.grid(row=4, column=0, columnspan=2, pady=10)

def agregar_nuevo_nodo(latitud, longitud, tipo, nombre, window):
    try:
        latitud = float(latitud)
        longitud = float(longitud)

        if not nombre.strip():
            raise ValueError("El nombre no puede estar vacío.")

        # Añade el nodo al grafo
        G.add_node(nombre, pos=(latitud, longitud), tipo=tipo)

        # Muestra un mensaje de éxito y cierra la ventana
        messagebox.showinfo("Éxito", f"Nodo '{nombre}' agregado exitosamente como '{tipo}'.")
        window.destroy()  # Cierra la ventana de entrada

    except ValueError as e:
        messagebox.showerror("Error", f"Datos inválidos: {e}")

#Función para encontrar el nodo más cercano a un nodo dado en el grafo
def encontrar_nodo_mas_cercano(nodo):
    menor_distancia = float('inf')
    nodo_mas_cercano = None
    for vecino in G.neighbors(nodo):
        distancia = G[nodo][vecino]['weight']
        if distancia < menor_distancia:
            menor_distancia = distancia
            nodo_mas_cercano = vecino
    return nodo_mas_cercano

#Función para mostrar el nodo más cercano al último nodo agregado
def mostrar_nodo_mas_cercano():
    ultimo_nodo = list(G.nodes)[-1]  #Asume que el último nodo agregado está al final
    nodo_cercano = encontrar_nodo_mas_cercano(ultimo_nodo)
    mostrar_nodo_mas_cercano.ultimo_nodo = ultimo_nodo
    mostrar_nodo_mas_cercano.nodo_cercano = nodo_cercano
    if nodo_cercano:
        distancia = G[ultimo_nodo][nodo_cercano]['weight']
        label_nodo_cercano.config(
            text=f"Ruta: {nodo_cercano} -> {ultimo_nodo}\nDistancia: {distancia:.2f} en cientos de kilómetros\nDistancia Real: {distancia*100:.2f} km"
        )
    else:
        label_nodo_cercano.config(text="No hay nodos cercanos")

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
    x_entry = tk.Entry(ventana)
    x_entry.place(x=510, y=230)

    ttk.Label(ventana, text="Y:", foreground='white', background='grey').place(x=670, y=230)
    y_entry = tk.Entry(ventana)
    y_entry.place(x=700, y=230)

    # Botón para agregar un nuevo punto
    add_button = tk.Button(
        ventana,
        text="AGREGAR",
        font=("Helvetica", 10),
        bg="#6a994e",
        fg="white",
        command=lambda: solicitar_nuevo_nodo(name_entry.get(), x_entry.get(), y_entry.get())
        )
    add_button.place(x=565, y=270, width=160, height=45)

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