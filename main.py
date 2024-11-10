#Librerias
import pandas as pd
import networkx as nx
import math
import folium
from folium import Marker, PolyLine
from folium.plugins import MiniMap
import webbrowser
import heapq as hq


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

#Función para mostrar el camino más corto en un mapa
def show_map(path=None):
    mapa_lima = folium.Map(location=[-12.0464, -77.0428], zoom_start=12) #Mapa Centro de Lima
    minimap = MiniMap()
    mapa_lima.add_child(minimap)
    
    #Añadir paraderos al mapa
    for _, row in paraderos_df.iterrows():
        color = 'red' if path and row['Nombre'] in path else 'blue'
        Marker([row['Latitud'], row['Longitud']], popup=row['Nombre'], icon=folium.Icon(color=color)).add_to(mapa_lima)
    
    #Añadir puntos de recarga al mapa
    for _, row in puntos_recarga_df.iterrows():
        Marker([row['Latitud'], row['Longitud']], popup=row['Nombre'], icon=folium.Icon(color='green')).add_to(mapa_lima)

#Agregar las líneas (aristas) entre los paraderos
    for (inicio, fin), data in G.edges.items():
        pos_inicio = G.nodes[inicio]['pos']
        pos_fin = G.nodes[fin]['pos']
        
        #Verificar si la arista (inicio, fin) está en el camino mínimo
        if path and inicio in path and fin in path:
            idx_inicio = path.index(inicio)
            if idx_inicio < len(path) - 1 and path[idx_inicio + 1] == fin:
                color = 'red'
            else:
                color = 'blue'
        else:
            color = 'blue'
        
        #Añadir la línea con el color determinado
        PolyLine(locations=[(pos_inicio.x, pos_inicio.y), (pos_fin.x, pos_fin.y)], 
                 color=color, weight=2, tooltip=f'distancia: {data["weight"]:.2f} km').add_to(mapa_lima)
    
    #Comentar para implementar despues
    #display_map(mapa_lima)

#Algoritmo de Dijkstra para encontrar el camino más corto  

def find_shortest_path(start, end):
    # Inicializar costos y predecesores para cada nodo
    costs = {node: float('inf') for node in G.nodes}
    predecessors = {node: None for node in G.nodes}
    costs[start] = 0  # El costo del nodo de inicio es 0
    queue = [(0, start)]  # Cola de prioridad para los nodos por visitar

    while queue:
        current_cost, current_node = hq.heappop(queue)  # Extraer el nodo con el menor costo
        if current_node == end:
            break  # Si se llega al nodo de destino, termina el algoritmo

        for neighbor in G.neighbors(current_node):
            # Obtener el peso de la arista entre current_node y neighbor
            distance = G[current_node][neighbor].get('weight', float('inf'))
            cost = current_cost + distance  # Calcula el nuevo costo

            # Actualizar costo y predecesor si se encontró un camino más corto
            if cost < costs[neighbor]:
                costs[neighbor] = cost
                predecessors[neighbor] = current_node
                hq.heappush(queue, (cost, neighbor))  # Añadir a la cola de prioridad

    # Construir el camino de salida a partir de los predecesores
    path = []
    step = end
    while step is not None:
        path.append(step)
        step = predecessors[step]
    path.reverse()  # Invertir el camino para ir del inicio al fin

    # Mostrar el mapa con la ruta resaltada
    if costs[end] == float('inf'):
        messagebox.showinfo("Sin Camino", f"No hay camino entre {start} y {end}.")
        return None, None
    else:
        show_map(path)  # Muestra el mapa con la ruta
        return path, costs[end]  # Retorna el camino y la distancia total
