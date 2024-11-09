#Librerias
import pandas as pd
import networkx as nx
import math
import folium
import webbrowser

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