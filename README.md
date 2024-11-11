<h1 align="center">
Repositorio del Trabajo Final del curso de Complejidad Algoritmica

## Índice
Descripción del problema

Descripción del conjunto de datos (dataset)

Propuesta

Referencias bibliográficas



## 1. Descripción del problema

Optimización de Estaciones, Puntos de Venta y Recarga en los Corredores de Transporte de Lima, Perú
La provincia de Lima, con más de 10 millones de habitantes (INEI, 2024) y un parque automotor que crece anualmente, enfrenta serios problemas de tráfico y movilidad urbana. Según la Encuesta Nacional de Hogares (ENAHO, 2022), el 52% de los limeños depende del transporte público para sus desplazamientos diarios. Además, estudios indican que el 50% de limeños pasa entre 1 y 2 horas viajando en el día (Asosiación Movemos, 2023), lo que representa un enorme costo en tiempo y productividad para la población. Asimismo, la encuesta reveló que el 37% de los peruanos siente que el tráfico les reduce el tiempo que pasan con sus familias, siendo más notable en Lima, donde esta cifra asciende al 48%.

El sistema de transporte urbano de Lima incluye corredores de buses complementarios a cargo de la Autoridad de Transporte Urbano para Lima y Callao (ATU), que se extienden por las principales avenidas de área metropolitana. Sin embargo, a pesar de los esfuerzos para mejorar este sistema, existen importantes ineficiencias relacionadas con la congestión vehicular, la falta de optimización en las rutas y la distribución desigual de los puntos de venta y recarga de la tarjeta de transporte "Lima Pass".
Este problema busca abordar la optimización de rutas y estaciones dentro de los corredores de transporte público, con el fin de mejorar la eficiencia de los trayectos, reducir los tiempos de viaje y garantizar un acceso fácil a los puntos de venta y recarga de tarjetas. Esto es crucial en Lima, donde las condiciones del tráfico están entre las más complejas de América Latina. Según el Índice Global de Tráfico (Tom Tom, 2023), Lima ocupa el quinto lugar en el ranking de ciudades más congestionadas del mundo, con un aumento del 42% en los tiempos de viaje durante las horas punta.

### Objetivos

#### Análisis de Datos del Sistema de Transporte:

Explorar y analizar los datos sobre las rutas de los corredores, tiempos de viaje, estaciones, puntos de recarga de tarjetas y patrones de tráfico en Lima.

Comprender la distribución de las estaciones y la accesibilidad de los puntos de recarga en las distintas zonas de la ciudad.

#### Desarrollo del Algoritmo de Optimización:
Implementar el Algoritmo de Dijkstra para modelar la red de transporte público de Lima como un grafo.

El grafo representará las estaciones como nodos y los tiempos de viaje o distancias entre ellas como aristas ponderadas.

El algoritmo buscará optimizar rutas según el tiempo de viaje o la proximidad a puntos de recarga.

#### Diseño del Aplicativo:
Crear una interfaz amigable que permita a los usuarios seleccionar estaciones de origen y destino, así como su criterio de optimización (tiempo o acceso a recargas).

Integrar la visualización de las rutas óptimas en un mapa de Lima, con detalles como paradas intermedias y tiempos estimados de viaje.


## 2. Descripción y visualización del conjunto de datos (dataset)

Para llevar a cabo la optimización de las rutas de transporte en Lima y mejorar el acceso a los puntos de recarga de las tarjetas Lima Pass, utilizaremos dos conjuntos de datos principales:

### 1. Dataset de Paraderos
Este conjunto contiene la información geográfica y de ubicación de los paraderos (estaciones) que forman parte del sistema de corredores de buses en Lima. Contiene información sobre los paraderos de las diferentes rutas de los corredores de Lima, incluidos los corredores como RUTA 201, RUTA 209, RUTA 204, entre otros. Los datos clave incluyen:

X: Coordenada X en el sistema de referencia utilizado.

Y: Coordenada Y en el sistema de referencia utilizado.

Name: Nombre o código del paradero.

Latitud: Coordenada geográfica de latitud.

Longitud: Coordenada geográfica de longitud.


### 2. Dataset de Puntos de Recarga y Venta de Tarjetas Lima Pass
Este conjunto incluye los puntos de venta y recarga de las tarjetas de transporte, esenciales para que los usuarios puedan utilizar el sistema de buses. Contiene información detallada sobre los puntos de venta y recarga de las tarjetas Lima Pass, que son esenciales para que los usuarios accedan al sistema de transporte público. Cada registro incluye:

X: Coordenada X en el sistema de referencia.

Y: Coordenada Y en el sistema de referencia.

Name: Nombre del punto de recarga.

Dirección Comercial: Dirección del punto de venta/recarga.

Horario de Atención: Horario de funcionamiento del punto de recarga.

Latitud: Coordenada geográfica de latitud.

Longitud: Coordenada geográfica de longitud.


### Relación entre los Conjuntos de Datos
La combinación de ambos conjuntos de datos permitirá la creación de un grafo ponderado en el que:
Los nodos representan las estaciones del sistema de transporte público.
Las aristas conectan las estaciones, representando el tiempo de viaje o la distancia.
Los puntos de recarga se añadirán como atributos adicionales de los nodos, permitiendo que los usuarios opten por rutas que incluyan estaciones con puntos de recarga cercanos.
Representación Mediante Grafos

### Origen de los Datos
Datos recopilados del portal virtual de la Autoridad de Transporte Urbano para Lima y Callao (ATU), MAPA DE PUNTOS DE VENTA Y RECARGA.

https://www.google.com/maps/d/viewer?mid=1yAw_GY9R8jQ28znyNOSaeTL5nRcSas-6&g_ep=CAESCjExLjU3LjQ4MDEYAA%3D%3D&shorturl=1&ll=-11.9900588637224%2C-76.98972999999998&z=10 


## 3. Propuesta

### Aplicativo para Optimización de Rutas de Transporte Público en Lima

Lo que proponemos como equipo para resolver esta problemática es el desarrollo de un aplicativo en Python que implemente el Algoritmo de Dijkstra para optimizar las rutas de los corredores de transporte público en Lima, Perú. Este algoritmo permitirá encontrar la ruta más eficiente para los usuarios, optimizando en función de dos criterios: tiempo de viaje o proximidad a puntos de venta y recarga de tarjetas.

Elegimos el Algoritmo de Dijkstra debido a su eficiencia en problemas de rutas mínimas, particularmente en redes donde las aristas tienen pesos variables (como el tiempo de viaje o la distancia). Dijkstra permite explorar todas las rutas posibles entre dos estaciones y siempre encuentra la opción más corta, lo que lo convierte en una herramienta ideal para sistemas de navegación y transporte público, como el de Lima.

Comparado con otros algoritmos de recorrido, como el Búsqueda de Costo Uniforme (UCS), Dijkstra tiene un enfoque más directo para encontrar el camino más corto y es ampliamente utilizado en aplicaciones modernas de navegación. Según Simic (2021), Dijkstra se adapta bien a situaciones donde se requiere optimizar tiempo o distancia en redes de transporte, lo que lo hace adecuado para este tipo de problemática.

### Funcionalidades del Aplicativo

El aplicativo que desarrollaremos permitirá a los usuarios:

#### Seleccionar una estación de origen y destino: 

El usuario podrá ingresar el punto de partida y el punto final de su trayecto dentro de la red de corredores.

#### Escoger el criterio de optimización:

Tiempo de viaje: El sistema mostrará la ruta más rápida, tomando en cuenta el tráfico y los tiempos promedio de viaje.

Acceso a puntos de recarga: Si el usuario necesita recargar su tarjeta, el algoritmo priorizará rutas que incluyan estaciones con puntos de recarga.

#### Visualización de la ruta: 

El aplicativo mostrará la ruta óptima en un mapa de la ciudad, indicando los tiempos estimados y las paradas intermedias.

## 4.	Diseño de aplicativo
    Procesos del Diseño del Aplicativo
    El diseño del aplicativo se enfoca en la optimización de rutas utilizando grafos. Para abordar este problema, hemos implementado un algoritmo de búsqueda de caminos más cortos (Dijkstra) en Python y varias bibliotecas como NetworkX para la creación y manipulación de grafos, y Folium para la visualización geográfica.

    1.	Análisis de Requisitos:
    •	Se identificaron las necesidades del sistema para optimizar rutas entre paraderos y puntos de recarga en una ciudad.
    •	Se consideraron funcionalidades como la visualización de rutas, cálculo de distancias y selección de estaciones mediante una interfaz de usuario.

    2.	Diseño del Sistema:
    •	Se empleó un Grafo no dirigido para modelar los paraderos y puntos de recarga, donde los nodos representan estaciones y las aristas     representan rutas entre ellas.
    •	Las distancias entre nodos se calcularon usando la distancia euclidiana.
    •	La solución del camino más corto entre dos estaciones se resolvió utilizando el algoritmo de Dijkstra, que es eficiente para este tipo de problemas.

    3.	Implementación:
    •	Utilizamos Python y librerías como Pandas para la manipulación de datos, NetworkX para la creación del grafo, Folium para la visualización de mapas, y Tkinter para la interfaz gráfica.
    •	Se desarrolló una función para cargar datos desde archivos Excel y crear los nodos y aristas del grafo.
    •	Se creó una función que muestra un mapa interactivo con los paraderos y rutas utilizando Folium.
    •	Se implementó una interfaz con Tkinter para que los usuarios seleccionen los paraderos de origen y destino.

    Requisitos del Aplicativo

    Requisitos Funcionales:
    •	Cargar y procesar datos desde archivos Excel con información de paraderos y puntos de recarga.
    •	Crear un grafo con nodos (paraderos y puntos de recarga) y aristas (rutas entre paraderos).
    •	Calcular la ruta más corta entre dos paraderos utilizando el algoritmo de Dijkstra.
    •	Visualizar el mapa interactivo con los paraderos, puntos de recarga, y la ruta óptima.
    •	Permitir la selección de paraderos de origen y destino mediante una interfaz gráfica.
    Requisitos No Funcionales:

    •	Eficiencia: El algoritmo de Dijkstra debe calcular rutas de manera rápida, incluso con un número elevado de nodos y aristas.
    •	Usabilidad: La interfaz debe ser intuitiva, permitiendo al usuario seleccionar estaciones de manera sencilla.
    •	Escalabilidad: El sistema debe poder adaptarse a la inclusión de nuevos paraderos y puntos de recarga sin afectar su desempeño.
    •	Portabilidad: El aplicativo debe ser compatible con diferentes sistemas operativos donde se pueda ejecutar Python.
    Diseño de Interfaz de Usuario

    •	Se utilizó Tkinter para crear una interfaz gráfica, incluye:
    •	Un menú desplegable para seleccionar paraderos de origen y destino.
    •	Botones para buscar rutas y mostrar la distancia calculada.
    •	Ventanas emergentes (messagebox) para mostrar resultados al usuario.
    •	Para la visualización del mapa:
    •	Folium se empleó para generar un mapa interactivo que muestra paraderos, puntos de recarga, y la ruta más corta destacada.

## 5.	Validación de datos y pruebas
    Entradas y Salidas:

    •	Entradas:
    o	Archivos Excel (paraderos.xlsx y puntos_recarga.xlsx) que contienen la información de coordenadas, nombres y datos adicionales de paraderos y puntos de recarga.
    o	Selección del paradero de origen y destino por parte del usuario.

    •	Salidas:
    o	Camino más corto entre los paraderos seleccionados.
    o	Distancia total del recorrido.
    o	Mapa interactivo que muestra la ruta en un navegador web.


### Conclusión

El aplicativo optimizará la experiencia de los usuarios del transporte público, permitiéndoles ahorrar tiempo en sus trayectos y facilitar el acceso a puntos de venta y recarga. Esto mejorará la calidad de vida de los limeños al reducir el tiempo que pasan en transporte y facilitar su acceso a recursos importantes, como la recarga de tarjetas.

En resumen, nuestra propuesta es desarrollar un aplicativo en Python basado en el Algoritmo de Dijkstra, enfocado en optimizar las rutas de transporte en Lima, lo que permitirá a los usuarios realizar sus viajes de forma más eficiente.



## 4. Referencias Bibliográficas

Conocer puntos de venta y recarga de tarjetas del Metropolitano y Corredores complementarios. (2021, 25 octubre). Servicio - Autoridad de Transporte Urbano Para Lima y Callao - Plataforma del Estado Peruano. https://www.gob.pe/15049-conocer-puntos-de-venta-y-recarga-de-tarjetas-del-metropolitano-y-corredores-complementarios 

Encuesta Nacional de Hogares (ENAHO) 2022 - [Instituto Nacional de Estadística e Informática – INEI] | Plataforma Nacional de Datos Abiertos. (s. f.). https://www.datosabiertos.gob.pe/dataset/encuesta-nacional-de-hogares-enaho-2022-instituto-nacional-de-estad%C3%ADstica-e-inform%C3%A1tica-%E2%80%93 

Gestión, R. (2023, 3 enero). ¿Cuánto tiempo pasan los limeños viajando en transporte público? Gestión. https://gestion.pe/peru/cuanto-tiempo-pasan-los-limenos-viajando-en-transporte-publico-transporte-publico-trafico-vehicular-noticia/ 

Inei. (s. f.). Instituto Nacional de Estadistica e Informatica. https://m.inei.gob.pe/prensa/noticias/poblacion-de-la-provincia-de-lima-supera-los-10-millones-292-mil-habitantes-14869/

Simic, M. (2021, October 15). Baeldung. Baeldung on Computer Science. https://www.baeldung.com/cs/uniform-cost-search-vs-best-first-search#:~:text=We%20use%20a%20Uniform%2DCost,start%20and%20the%20goal%20states. 

Traffic Index ranking | TomTom Traffic Index. (s. f.). Traffic Index Ranking | TomTom Traffic Index. https://www.tomtom.com/traffic-index/ranking/ 
