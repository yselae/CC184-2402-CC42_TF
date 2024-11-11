#Librerias
import pandas as pd
import networkx as nx
import math
import folium
from folium import Marker, PolyLine
from folium.plugins import MiniMap
import webbrowser
import heapq as hq
import io, base64, os, random
import matplotlib.pyplot as plt

from tkinter import messagebox, ttk
import tkinter as tk
from tkinter import *

#Leer los archivos XLSX
paraderos_path = 'paraderos.xlsx'
puntos_recarga_path = 'puntos_recarga.xlsx'

paraderos_df = pd.read_excel(paraderos_path).head(30)  # Tomamos solo los primeros 25 paraderos
puntos_recarga_df = pd.read_excel(puntos_recarga_path).head(30)

def correct_decimal_placement(value):
    value_str = str(value)
    if '.' in value_str:
        value_str = value_str.split('.')[0]  
    if value < 0:
        return float(value_str[:3] + '.' + value_str[3:])
    else:
        return float(value_str[:2] + '.' + value_str[2:])


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
def solicitar_nuevo_nodo():
    nuevo_nodo_top = tk.Toplevel(root)
    nuevo_nodo_top.title("Agregar nuevo nodo")
    nuevo_nodo_top.geometry("300x250")

    entry_frame = tk.Frame(nuevo_nodo_top, padx=10, pady=10)
    entry_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    #Entradas para latitud, longitud, tipo y nombre
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
                               float(lat_entry.get()), float(lon_entry.get()), tipo_combo.get(),
                               nombre_entry.get(), nuevo_nodo_top))
    add_button.grid(row=4, column=0, columnspan=2, pady=10)

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


##################################################################

#ffalta agregar root, label_nodo_cercano, label_distancia, valor1, valor2

##################################################################








##################################################################

#Función para actualizar los menús desplegables
def actualizar_dropdowns():
    #Obtener los nombres de todos los paraderos y puntos de recarga
    nodos = list(paraderos_df['Nombre']) + list(puntos_recarga_df['Nombre'])
    
    # Actualizar los valores de los menús desplegables
    drop1['values'] = nodos  # Actualiza los valores del primer menú desplegable
    drop2['values'] = nodos  # Actualiza los valores del segundo menú desplegable
    
    # Seleccionar el primer nodo por defecto en ambos menús desplegables, si existen nodos
    if nodos:
        valor1.set(nodos[0])  # Selecciona el primer nodo por defecto en el primer menú desplegable
        valor2.set(nodos[0])  # Selecciona el primer nodo por defecto en el segundo menú desplegable


#Función para cerrar la aplicación
def on_closing():
    if messagebox.askokcancel("Salir", "¿Quieres salir del programa?"):
        root.destroy() 

##################################################################








# Interfaz gráfica con tkinter
def run_app():
    def on_find_route():
        start = start_combobox.get()
        end = end_combobox.get()
        if start and end:
            path, distance = dijkstra(start, end)
            if path:
                messagebox.showinfo("Camino encontrado", f"Camino: {' -> '.join(path)}\nDistancia: {distance:.2f} km")
            else:
                messagebox.showwarning("Camino no encontrado", "No se pudo encontrar una ruta entre los paraderos seleccionados.")
        else:
            messagebox.showwarning("Entrada inválida", "Por favor, seleccione los paraderos de origen y destino.")

    # Funciones para los otros botones
    def mostrar_paraderos():
        messagebox.showinfo("Paraderos", "Mostrando todos los paraderos disponibles en el mapa.")

    def mostrar_puntos_recarga():
        messagebox.showinfo("Puntos de Recarga", "Mostrando todos los puntos de recarga disponibles.")

    def mostrar_corredores():
        messagebox.showinfo("Corredores", "Mostrando todos los corredores en el mapa.")

    def agregar_paradero():
        messagebox.showinfo("Agregar Paradero", "Función para agregar un nuevo paradero.")

    def filtrar_paraderos_cercanos():
        messagebox.showinfo("Paraderos Cercanos", "Mostrando paraderos cercanos al punto seleccionado.")
    
    # Crear ventana principal
    root = tk.Tk()
    root.title("Optimización de rutas de transporte")
    root.geometry("600x400")
    root.configure(bg="lightgray")

    # Etiqueta de bienvenida
    ttk.Label(root, text="Bienvenido a Optimización de Rutas", font=("Helvetica", 16, "bold")).grid(column=0, row=0, columnspan=3, pady=20)

    # Etiquetas y entradas para paraderos de origen y destino
    ttk.Label(root, text="Paradero de origen:").grid(column=0, row=1, padx=10, pady=5, sticky="e")
    start_combobox = ttk.Combobox(root, values=paraderos_df['Nombre'].tolist(), width=35)
    start_combobox.grid(column=1, row=1, padx=10, pady=5, sticky="w")

    ttk.Label(root, text="Paradero de destino:").grid(column=0, row=2, padx=10, pady=5, sticky="e")
    end_combobox = ttk.Combobox(root, values=paraderos_df['Nombre'].tolist(), width=35)
    end_combobox.grid(column=1, row=2, padx=10, pady=5, sticky="w")

    # Botón para encontrar la ruta
    find_route_button = ttk.Button(root, text="Encontrar ruta", command=on_find_route)
    find_route_button.grid(column=1, row=3, pady=15, sticky="ew")

    # Separador
    ttk.Separator(root, orient="horizontal").grid(row=4, column=0, columnspan=3, sticky="ew", padx=10, pady=15)

    # Botones adicionales para otras funcionalidades
    button_frame = tk.Frame(root, bg="lightgray")
    button_frame.grid(row=5, column=0, columnspan=3, pady=10)

    ttk.Button(button_frame, text="Mostrar Todos los Paraderos", command=mostrar_paraderos).grid(row=0, column=0, padx=10, pady=5, sticky="ew")
    ttk.Button(button_frame, text="Mostrar Puntos de Recarga", command=mostrar_puntos_recarga).grid(row=0, column=1, padx=10, pady=5, sticky="ew")
    ttk.Button(button_frame, text="Mostrar Todos los Corredores", command=mostrar_corredores).grid(row=0, column=2, padx=10, pady=5, sticky="ew")

    ttk.Button(button_frame, text="Agregar Paradero o Punto de Recarga", command=agregar_paradero).grid(row=1, column=0, padx=10, pady=5, sticky="ew")
    ttk.Button(button_frame, text="Filtrar Paraderos Cercanos", command=filtrar_paraderos_cercanos).grid(row=1, column=1, padx=10, pady=5, sticky="ew")

    # Ajustar la columna para que los botones ocupen el espacio disponible
    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=1)
    button_frame.grid_columnconfigure(2, weight=1)

    root.mainloop()

# Ejecutar la aplicación
run_app()