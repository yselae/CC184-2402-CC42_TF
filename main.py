#Librerias
import pandas as pd
import networkx as nx
import math
import folium
from folium import Marker, PolyLine
from folium.plugins import MiniMap
import webbrowser
import heapq as hq
import io, base64, os
import matplotlib.pyplot as plt

from tkinter import messagebox, ttk
import tkinter as tk
from tkinter import *

#Leer los archivos XLSX
paraderos_path = 'paraderos.xlsx'
puntos_recarga_path = 'puntos_recarga.xlsx'

paraderos_df = pd.read_excel(paraderos_path)
puntos_recarga_df = pd.read_excel(puntos_recarga_path)

#Crear un grafo no dirigido
G = nx.Graph()

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

#Función para mostrar el mapa base
def show_map():
    mapa_Lima = folium.Map(location=[-12.0464, -77.0428], zoom_start=12) 
    minimap = MiniMap()  
    mapa_Lima.add_child(minimap)  
    display_map(mapa_Lima)

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
    for _, row in paraderos_df.iterrows():
        G_transport.add_node(row['Nombre'], pos=(row['Latitud'], row['Longitud']), tipo='paradero')
    
    for _, row in puntos_recarga_df.iterrows():
        G_transport.add_node(row['Nombre'], pos=(row['Latitud'], row['Longitud']), tipo='punto_recarga')

    #Añadir aristas entre paraderos con las distancias como peso
    for (inicio, fin), distancia in distancias.items():
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
    for (inicio, fin), distancia in distancias.items():
        pos_inicio = (G.nodes[inicio]['pos'][1], G.nodes[inicio]['pos'][0])  #Obtener posición de inicio
        pos_fin = (G.nodes[fin]['pos'][1], G.nodes[fin]['pos'][0])  #Obtener posición de fin
        PolyLine(locations=[pos_inicio, pos_fin], color='blue', weight=2, tooltip=f'Distancia: {distancia:.2f} km').add_to(mapa_lima)
    display_map(mapa_lima)







# Interfaz gráfica con tkinter
def run_app():
    def on_find_route():
        start = start_entry.get()
        end = end_entry.get()
        if start and end:
            path, distance = dijkstra(start, end)
            if path:
                messagebox.showinfo("Camino encontrado", f"Camino: {path}\nDistancia: {distance:.2f} km")
        else:
            messagebox.showwarning("Entrada inválida", "Por favor, ingrese los nombres de origen y destino.")

    # Crear ventana principal
    root = tk.Tk()
    root.title("Optimización de rutas de transporte")
    root.geometry("400x200")

    # Etiquetas y entradas
    ttk.Label(root, text="Paradero de origen:").grid(column=0, row=0, padx=10, pady=5)
    start_entry = ttk.Entry(root, width=30)
    start_entry.grid(column=1, row=0)

    ttk.Label(root, text="Paradero de destino:").grid(column=0, row=1, padx=10, pady=5)
    end_entry = ttk.Entry(root, width=30)
    end_entry.grid(column=1, row=1)

    # Botón para encontrar la ruta
    find_route_button = ttk.Button(root, text="Encontrar ruta", command=on_find_route)
    find_route_button.grid(column=1, row=2, pady=10)

    root.mainloop()

# Ejecutar la aplicación
run_app()