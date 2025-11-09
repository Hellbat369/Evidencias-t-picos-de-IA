#!/usr/bin/env python
# -*- coding: utf-8 -*-

# --- IMPORTACIONES ---
import random
import numpy as np
import pandas as pd
import operator
import matplotlib.pyplot as plt  # Para graficar la ruta

# --- CLASE 1: MUNICIPIO ---
# Propósito: Representar una "ciudad" o "nodo" en el mapa.
class municipio:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    # Calcula la distancia euclidiana a otro municipio
    def distancia(self, municipio):
        xDis = abs(self.x - municipio.x)
        yDis = abs(self.y - municipio.y)
        distancia = np.sqrt((xDis ** 2) + (yDis ** 2))
        return distancia

    # Representación en string (para imprimir la ruta)
    def __repr__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"


# --- CLASE 2: APTITUD (Fitness) ---
# Propósito: Evaluar qué tan "buena" es una ruta (un "individuo").
class Aptitud:
    def __init__(self, ruta):
        self.ruta = ruta
        self.distancia = 0
        self.f_aptitud = 0.0
    
    # Calcula la distancia total de la ruta
    def distanciaRuta(self):
        if self.distancia == 0:
            distanciaRelativa = 0
            for i in range(0, len(self.ruta)):
                puntoInicial = self.ruta[i]
                puntoFinal = None
                
                # Conectar el último municipio con el primero
                if i + 1 < len(self.ruta):
                    puntoFinal = self.ruta[i + 1]
                else:
                    puntoFinal = self.ruta[0]
                
                distanciaRelativa += puntoInicial.distancia(puntoFinal)
            self.distancia = distanciaRelativa
        return self.distancia

    # Calcula la aptitud (Fitness = 1 / Distancia)
    def rutaApta(self):
        if self.f_aptitud == 0:
            self.f_aptitud = 1 / float(self.distanciaRuta())
        return self.f_aptitud


# --- FUNCIONES DEL ALGORITMO GENÉTICO ---

# --- ETAPA 1: INICIALIZACIÓN ---
def crearRuta(listaMunicipios):
    # Crea una permutación aleatoria de la lista de municipios
    ruta = random.sample(listaMunicipios, len(listaMunicipios))
    return ruta

def poblacionInicial(tamanoPob, listaMunicipios):
    poblacion = []
    for i in range(0, tamanoPob):
        poblacion.append(crearRuta(listaMunicipios))
    return poblacion


# --- ETAPA 2: EVALUACIÓN Y SELECCIÓN ---
def clasificacionRutas(poblacion):
    # Evalúa y clasifica todas las rutas de mejor a peor
    fitnessResults = {}
    for i in range(0, len(poblacion)):
        fitnessResults[i] = Aptitud(poblacion[i]).rutaApta()
    
    return sorted(fitnessResults.items(), key = operator.itemgetter(1), reverse = True)

def seleccionRutas(popRanked, indivSelecionados):
    # Combina Elitismo (conserva los N mejores)
    # y Selección por Ruleta (para el resto)
    resultadosSeleccion = []
    
    # Elitismo
    for i in range(0, indivSelecionados):
        resultadosSeleccion.append(popRanked[i][0])
    
    # Selección por Ruleta
    df = pd.DataFrame(np.array(popRanked), columns=["Indice","Aptitud"])
    df['cum_sum'] = df.Aptitud.cumsum()
    df['cum_perc'] = 100 * df.cum_sum / df.Aptitud.sum()
    
    for i in range(0, len(popRanked) - indivSelecionados):
        seleccion = 100 * random.random()
        for i in range(0, len(popRanked)):
            if seleccion <= df.iat[i, 3]:
                resultadosSeleccion.append(popRanked[i][0])
                break
    return resultadosSeleccion

def grupoApareamiento(poblacion, resultadosSeleccion):
    # Obtiene las rutas completas a partir de los índices seleccionados
    grupoApareamiento = []
    for i in range(0, len(resultadosSeleccion)):
        index = resultadosSeleccion[i]
        grupoApareamiento.append(poblacion[index])
    return grupoApareamiento


# --- ETAPA 3: REPRODUCCIÓN (CRUCE) ---
def reproduccion(progenitor1, progenitor2):
    # "Ordered Crossover"
    hijo = []
    hijoP1 = []
    hijoP2 = []
    
    genX = int(random.random() * len(progenitor1))
    genY = int(random.random() * len(progenitor1))
    genInicial = min(genX, genY)
    genFinal = max(genX, genY)

    for i in range(genInicial, genFinal):
        hijoP1.append(progenitor1[i])
        
    hijoP2 = [item for item in progenitor2 if item not in hijoP1]

    hijo = hijoP1 + hijoP2
    return hijo

def reproduccionPoblacion(grupoApareamiento, indivSelecionados):
    hijos = []
    tamano = len(grupoApareamiento) - indivSelecionados
    espacio = random.sample(grupoApareamiento, len(grupoApareamiento))

    # Los individuos de élite pasan sin cambios
    for i in range(0, indivSelecionados):
        hijos.append(grupoApareamiento[i])
    
    # Cruza al resto del grupo
    for i in range(0, tamano):
        hijo = reproduccion(espacio[i], espacio[len(grupoApareamiento)-i-1])
        hijos.append(hijo)
    
    return hijos


# --- ETAPA 4: MUTACIÓN ---
def mutacion(individuo, razonMutacion):
    # "Mutación por Intercambio" (Swap Mutation)
    for swapped in range(len(individuo)):
        if(random.random() < razonMutacion):
            swapWith = int(random.random() * len(individuo))
            
            lugar1 = individuo[swapped]
            lugar2 = individuo[swapWith]
            
            individuo[swapped] = lugar2
            individuo[swapWith] = lugar1
    return individuo

def mutacionPoblacion(poblacion, razonMutacion):
    pobMutada = []
    for ind in range(0, len(poblacion)):
        individuoMutar = mutacion(poblacion[ind], razonMutacion)
        pobMutada.append(individuoMutar)
    return pobMutada


# --- FUNCIÓN DE CICLO: NUEVA GENERACIÓN ---
def nuevaGeneracion(generacionActual, indivSelecionados, razonMutacion):
    # Ejecuta un ciclo completo de evolución
    popRanked = clasificacionRutas(generacionActual)
    selectionResults = seleccionRutas(popRanked, indivSelecionados)
    grupoApa = grupoApareamiento(generacionActual, selectionResults)
    hijos = reproduccionPoblacion(grupoApa, indivSelecionados)
    nuevaGeneracion = mutacionPoblacion(hijos, razonMutacion)
    return nuevaGeneracion


# --- FUNCIÓN PRINCIPAL: EL ALGORITMO GENÉTICO ---
def algoritmoGenetico(poblacion, tamanoPoblacion, indivSelecionados, razonMutacion, generaciones):
    
    # 1. Crear la población inicial
    pop = poblacionInicial(tamanoPoblacion, poblacion)
    
    distanciaInicial = 1 / clasificacionRutas(pop)[0][1]
    print(f"Distancia Inicial: {distanciaInicial:.4f}")
    
    mejorDistanciaGlobal = distanciaInicial

    # 2. El ciclo evolutivo
    for i in range(0, generaciones):
        pop = nuevaGeneracion(pop, indivSelecionados, razonMutacion)
        
        # --- MODIFICACIÓN: Mostrar Progreso ---
        # Muestra el progreso cada 50 generaciones
        if (i + 1) % 50 == 0 or i == 0:
            distanciaActual = 1 / clasificacionRutas(pop)[0][1]
            
            if distanciaActual < mejorDistanciaGlobal:
                mejorDistanciaGlobal = distanciaActual
            
            print(f"Generación {i + 1}: Mejor distancia actual = {distanciaActual:.4f} | Mejor global = {mejorDistanciaGlobal:.4f}")
        # --- FIN DE LA MODIFICACIÓN ---

    # 3. Imprimir resultados finales
    distanciaFinal = 1 / clasificacionRutas(pop)[0][1]
    print(f"\nDistancia Final: {distanciaFinal:.4f}")
    
    # 4. Devolver la mejor ruta encontrada
    bestRouteIndex = clasificacionRutas(pop)[0][0]
    mejorRuta = pop[bestRouteIndex]
    return mejorRuta


# --- FUNCIÓN DE GRÁFICOS (NUEVA) ---
def graficarRuta(listaMunicipios, mejorRuta):
    print("\nGraficando ruta...")
    
    # Extraer todas las coordenadas X e Y de todos los municipios
    todos_x = [municipio.x for municipio in listaMunicipios]
    todos_y = [municipio.y for municipio in listaMunicipios]
    
    # Extraer las coordenadas X e Y de la MEJOR RUTA
    ruta_x = [municipio.x for municipio in mejorRuta]
    ruta_y = [municipio.y for municipio in mejorRuta]
    
    # Añadir el primer punto al final para cerrar el ciclo
    ruta_x.append(mejorRuta[0].x)
    ruta_y.append(mejorRuta[0].y)

    plt.figure(figsize=(10, 7)) # Tamaño de la ventana
    
    # 1. Dibujar las líneas de la ruta (verde)
    plt.plot(ruta_x, ruta_y, 'g-', label='Ruta Optimizada')
    
    # 2. Dibujar los puntos de las ciudades (azul)
    plt.scatter(todos_x, todos_y, color='blue', s=100, label='Municipios')
    
    # 3. Poner un punto rojo grande para el inicio
    plt.scatter(mejorRuta[0].x, mejorRuta[0].y, color='red', s=150, label='Inicio/Fin')

    # Añadir números a las ciudades
    for i, municipio in enumerate(listaMunicipios):
        plt.annotate(f' {i}', (municipio.x, municipio.y), textcoords="offset points", xytext=(0,10), ha='center')

    # Títulos y etiquetas
    plt.title('Ruta Optimizada - Algoritmo Genético')
    plt.xlabel('Coordenada X')
    plt.ylabel('Coordenada Y')
    plt.legend()
    plt.grid(True)
    
    # Mostrar el gráfico
    plt.show()


# --- BLOQUE DE EJECUCIÓN ---
if __name__ == "__main__":
    
    # 1. Definir los datos de los municipios (x, y)
    ciudades_data = [
        (40.4168, -3.7038), # Madrid (0)
        (41.3784, 2.1925),  # Barcelona (1)
        (39.4699, -0.3763), # Valencia (2)
        (37.3891, -5.9845), # Sevilla (3)
        (41.6488, -0.8891), # Zaragoza (4)
        (43.3623, -5.8450)  # Oviedo (5)
    ]

    # 2. Convertir los datos en una lista de objetos 'municipio'
    listaMunicipios = []
    for x, y in ciudades_data:
        listaMunicipios.append( municipio(x, y) )

    # 3. Ejecutar el algoritmo genético
    mejor_ruta = algoritmoGenetico(
        poblacion=listaMunicipios,      # La lista de todos los municipios
        tamanoPoblacion=100,            # 100 individuos (rutas) por generación
        indivSelecionados=20,           # 20 individuos de élite (20%)
        razonMutacion=0.01,             # 1% de probabilidad de que un gen mute
        generaciones=500                # Número de ciclos evolutivos
    )

    # 4. Imprimir la mejor ruta encontrada
    print("\nMejor ruta encontrada: ")
    print(mejor_ruta)

    # 5. Graficar la mejor ruta
    graficarRuta(listaMunicipios, mejor_ruta)