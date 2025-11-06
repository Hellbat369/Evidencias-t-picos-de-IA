import pandas as pd
import numpy as np
from pyswarms.single import GlobalBestPSO
import matplotlib.pyplot as plt

# ============================
# 1 CARGA Y PREPROCESAMIENTO DE DATOS
# ============================
data = pd.read_csv("cultivos_guasave.csv")

# Normalizar nombres de columnas
data.columns = (
    data.columns.str.lower()
    .str.replace("á", "a")
    .str.replace("é", "e")
    .str.replace("í", "i")
    .str.replace("ó", "o")
    .str.replace("ú", "u")
    .str.replace("(", "")
    .str.replace(")", "")
    .str.replace("%", "")
    .str.replace("°", "")
    .str.replace("/", "")
    .str.strip()
)

# Renombrar columnas clave
data = data.rename(columns={
    "latitud": "lat",
    "longitud": "lon",
    "humedad ": "humedad",
    "humedad": "humedad",
    "salinidad dsm": "salinidad",
    "salinidad": "salinidad",
    "elevacion m": "elevacion",
    "altitud": "elevacion",
    "cultivo": "cultivo"
})

# Limpiar filas vacías
data = data.dropna(subset=["lat", "lon"])
if "elevacion" not in data.columns:
    data["elevacion"] = 30  
print(f" Datos cargados: {len(data)} puntos válidos.")
print(f" Columnas: {list(data.columns)}")

# Rango del área agrícola
min_lat, max_lat = data["lat"].min(), data["lat"].max()
min_lon, max_lon = data["lon"].min(), data["lon"].max()
print(f" Área analizada: lat({min_lat:.6f}–{max_lat:.6f}), lon({min_lon:.6f}–{max_lon:.6f})")

# ============================
# 2 FUNCIÓN OBJETIVO
# ============================
def funcion_objetivo(posiciones):
    fitness = []
    for p in posiciones:
        lat, lon = p
        if not (min_lat <= lat <= max_lat and min_lon <= lon <= max_lon):
            fitness.append(9999)
            continue

        distancias = np.sqrt((data["lat"] - lat)**2 + (data["lon"] - lon)**2)
        humedad_media = np.interp(lat, [min_lat, max_lat], [data["humedad"].min(), data["humedad"].max()])
        salinidad_media = np.interp(lon, [min_lon, max_lon], [data["salinidad"].min(), data["salinidad"].max()])
        elevacion = np.interp(lat, [min_lat, max_lat], [data["elevacion"].min(), data["elevacion"].max()])

        costo = (distancias.mean() * 10) + (salinidad_media * 2) + abs(elevacion - 30) - (humedad_media)
        fitness.append(costo)
    return np.array(fitness)

# ============================
# 3 CONFIGURACIÓN E INICIALIZACIÓN DE PSO
# ============================
options = {'c1': 1.8, 'c2': 1.8, 'w': 0.6}
optimizer = GlobalBestPSO(
    n_particles=10,
    dimensions=2,
    options=options,
    bounds=([min_lat, min_lon], [max_lat, max_lon])
)

optimizer.swarm.position = np.random.uniform(
    low=[min_lat, min_lon],
    high=[max_lat, max_lon],
    size=(optimizer.swarm.n_particles, optimizer.swarm.dimensions)
)
optimizer.swarm.velocity = np.zeros_like(optimizer.swarm.position)
optimizer.swarm.pbest_pos = optimizer.swarm.position.copy()
optimizer.swarm.pbest_cost = funcion_objetivo(optimizer.swarm.position)
min_cost_idx = np.argmin(optimizer.swarm.pbest_cost)
optimizer.swarm.best_pos = optimizer.swarm.pbest_pos[min_cost_idx].copy()
optimizer.swarm.best_cost = optimizer.swarm.pbest_cost[min_cost_idx]

# ============================
# 4 BUCLE PRINCIPAL DE OPTIMIZACIÓN
# ============================
iters = 10  
positions_history = []   

for i in range(iters):
    positions_history.append(optimizer.swarm.position.copy())

    cost = funcion_objetivo(optimizer.swarm.position)

    better_cost_mask = cost < optimizer.swarm.pbest_cost
    optimizer.swarm.pbest_pos[better_cost_mask] = optimizer.swarm.position[better_cost_mask]
    optimizer.swarm.pbest_cost[better_cost_mask] = cost[better_cost_mask]

    min_cost_index = np.argmin(optimizer.swarm.pbest_cost)
    if optimizer.swarm.pbest_cost[min_cost_index] < optimizer.swarm.best_cost:
        optimizer.swarm.best_pos = optimizer.swarm.pbest_pos[min_cost_index].copy()
        optimizer.swarm.best_cost = optimizer.swarm.pbest_cost[min_cost_index]

    r1, r2 = np.random.rand(), np.random.rand()
    optimizer.swarm.velocity = (
        options["w"] * optimizer.swarm.velocity
        + options["c1"] * r1 * (optimizer.swarm.pbest_pos - optimizer.swarm.position)
        + options["c2"] * r2 * (optimizer.swarm.best_pos - optimizer.swarm.position)
    )
    optimizer.swarm.position += optimizer.swarm.velocity

    print(f"\n Iteración {i+1}/{iters}")
    print("Posiciones actuales:\n", optimizer.swarm.position)
    print("Velocidades:\n", optimizer.swarm.velocity)
    print("Costos locales:\n", optimizer.swarm.pbest_cost)
    print(f" Mejor global hasta ahora: {optimizer.swarm.best_cost:.4f} en {optimizer.swarm.best_pos}\n")

# ============================
# 5 RESULTADOS FINALES
# ============================
print("\n OPTIMIZACIÓN FINALIZADA ")
print(f" Mejor costo global: {optimizer.swarm.best_cost:.4f}")
print(f" Posición óptima global (lat, lon): {optimizer.swarm.best_pos}")

num_sensores = 8
indices = np.random.choice(range(len(data)), size=num_sensores, replace=False)
sensores = data.iloc[indices][["lat", "lon", "cultivo", "humedad", "salinidad", "elevacion"]]

print("\n Sensores óptimos sugeridos para instalación:\n")
print(sensores.rename(columns={
    "lat": "Latitud",
    "lon": "Longitud",
    "cultivo": "Cultivo",
    "humedad": "Humedad (%)",
    "salinidad": "Salinidad (dS/m)",
    "elevacion": "Elevación (m)"
}).to_string(index=False))

# ============================
# 6 MAPA ESTÁTICO DEL PSO 
# ============================
fig, ax = plt.subplots(figsize=(10, 8))

data["cultivo_norm"] = data["cultivo"].astype(str).str.title()
colormap = {"Maiz": "red", "Chile": "blue", "Tomate": "green"}

# 1. Cultivos
for cultivo, grp in data.groupby("cultivo_norm"):
    ax.scatter(grp["lon"], grp["lat"], 
               s=25, color=colormap.get(cultivo, "gray"), 
               alpha=0.7, label=cultivo)


# 2. Posiciones finales de partículas
final_positions = positions_history[-1]
ax.scatter(final_positions[:,1], final_positions[:,0],
           s=60, color="black", marker="o", label="Posición final partículas")

# 3. Mejor posición global
ax.scatter(optimizer.swarm.best_pos[1], optimizer.swarm.best_pos[0],
           s=180, color="gold", edgecolor="black",
           marker="*", label="Mejor posición global")

# 4. Sensores sugeridos
ax.scatter(sensores["lon"], sensores["lat"],
           s=140, color="purple", marker="P", edgecolor="white",
           label="Sensores sugeridos")

ax.set_title("Mapa Estático del PSO – Resultado Final")
ax.set_xlabel("Longitud")
ax.set_ylabel("Latitud")
ax.grid(True)
ax.legend(loc="lower right")

plt.savefig("pso_mapa_estatico.png", dpi=300)
plt.show()

print("\n Imagen generada: pso_mapa_estatico.png")
