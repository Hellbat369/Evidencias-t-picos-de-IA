import pandas as pd
import numpy as np
import math
import random
import matplotlib.pyplot as plt

def cargar_datos(archivo_costos, archivo_nodos):
    """
    Carga la matriz de costos y los datos de los nodos desde archivos Excel.
    Crea listas con los índices de CDs y tiendas.
    """
    matriz_costos_df = pd.read_excel(archivo_costos, header=None)
    matriz_costos_df = matriz_costos_df.apply(pd.to_numeric, errors='coerce').fillna(0)
    matriz_costos = matriz_costos_df.to_numpy()

    nodos_df = pd.read_excel(archivo_nodos)
    nombres_nodos = list(nodos_df['Nombre'])
    cds = [i for i, nombre in enumerate(nombres_nodos) if 'Centro de Distribución' in nombre]
    tiendas = [i for i, nombre in enumerate(nombres_nodos) if 'Tienda' in nombre]

    print(f"Datos cargados correctamente: {len(cds)} Centros de Distribución y {len(tiendas)} tiendas.")
    return matriz_costos, nombres_nodos, cds, tiendas

def calcular_costo_ruta(ruta, matriz_costos):
    """
    Calcula el costo total de una ruta sumando los costos entre nodos consecutivos.
    """
    costo_total = 0
    for i in range(len(ruta) - 1):
        costo_total += matriz_costos[ruta[i]][ruta[i + 1]]
    return costo_total

def generar_solucion_inicial(cd, tiendas_asignadas):
    """
    Crea una ruta inicial que parte del CD, visita todas sus tiendas y regresa.
    """
    ruta = [cd] + random.sample(tiendas_asignadas, len(tiendas_asignadas)) + [cd]
    return ruta

def generar_vecino(ruta):
    """
    Crea una solución vecina intercambiando dos tiendas aleatorias.
    """
    nueva_ruta = ruta[:]
    idx1, idx2 = random.sample(range(1, len(ruta) - 1), 2)
    nueva_ruta[idx1], nueva_ruta[idx2] = nueva_ruta[idx2], nueva_ruta[idx1]
    return nueva_ruta

def recocido_simulado(matriz_costos, cd, tiendas_asignadas, temp_inicial, tasa_enfriamiento, num_iteraciones):
    """
    Ejecuta el algoritmo de recocido simulado para optimizar la ruta de un CD.
    """
    solucion_actual = generar_solucion_inicial(cd, tiendas_asignadas)
    costo_actual = calcular_costo_ruta(solucion_actual, matriz_costos)
    mejor_solucion = solucion_actual
    mejor_costo = costo_actual
    temperatura = temp_inicial
    historial = [costo_actual]

    for i in range(num_iteraciones):
        vecino = generar_vecino(solucion_actual)
        costo_vecino = calcular_costo_ruta(vecino, matriz_costos)
        delta = costo_vecino - costo_actual

        if delta < 0 or random.random() < math.exp(-delta / temperatura):
            solucion_actual = vecino
            costo_actual = costo_vecino

        if costo_actual < mejor_costo:
            mejor_solucion = solucion_actual
            mejor_costo = costo_actual

        temperatura *= tasa_enfriamiento
        historial.append(mejor_costo)

        if (i + 1) % 5000 == 0:
            print(f"CD {cd} | Iteración {i+1}/{num_iteraciones} | Mejor costo: {mejor_costo:.2f}")

    return mejor_solucion, mejor_costo, historial

def graficar_convergencia(historial_global):
    """
    Grafica la convergencia promedio de todos los CDs.
    """
    plt.figure(figsize=(12, 6))
    plt.plot(historial_global, color='dodgerblue', linewidth=2)
    plt.title('Evolución del costo promedio (todos los CDs)', fontsize=16)
    plt.xlabel('Iteración', fontsize=12)
    plt.ylabel('Costo promedio', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.savefig('grafico_convergencia_global.png')
    print("\nGráfico global guardado como 'grafico_convergencia_global.png'")

# --- PROGRAMA PRINCIPAL ---
if __name__ == '__main__':
    TEMP_INICIAL = 10000
    TASA_ENFRIAMIENTO = 0.999
    NUM_ITERACIONES = 30000

    archivo_matriz_costos = 'matriz_costos_combustible.xlsx'
    archivo_nodos_info = 'datos_distribucion_tiendas.xlsx'

    matriz_costos, nombres, cds, tiendas = cargar_datos(archivo_matriz_costos, archivo_nodos_info)

    # --- Asignar tiendas a cada CD de forma equitativa ---
    asignaciones = np.array_split(tiendas, len(cds))
    resultados = []
    historial_global = []

    for idx, cd in enumerate(cds):
        tiendas_asignadas = list(asignaciones[idx])
        print(f"\nOptimizando rutas para {nombres[cd]} con {len(tiendas_asignadas)} tiendas asignadas...")

        mejor_ruta, mejor_costo, historial = recocido_simulado(
            matriz_costos, cd, tiendas_asignadas,
            TEMP_INICIAL, TASA_ENFRIAMIENTO, NUM_ITERACIONES
        )

        resultados.append((nombres[cd], mejor_costo, mejor_ruta))
        if len(historial_global) < len(historial):
            historial_global = historial
        else:
            historial_global = [min(h1, h2) for h1, h2 in zip(historial_global, historial)]

    # --- Mostrar resultados finales ---
    print("\n" + "="*40)
    print("   RESULTADOS FINALES DE OPTIMIZACIÓN")
    print("="*40)
    costo_total = 0
    for nombre_cd, costo, ruta in resultados:
        costo_total += costo
        print(f"\n{nombre_cd}:")
        ruta_nombres = " -> ".join([nombres[i] for i in ruta])
        print(f"Ruta óptima: {ruta_nombres}")
        print(f"Costo total: {costo:.2f}")

    print(f"\nCosto total global optimizado: {costo_total:.2f}")
    graficar_convergencia(historial_global)
