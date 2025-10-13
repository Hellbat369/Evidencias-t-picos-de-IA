import pandas as pd
import folium

# Cargar el archivo Excel
ruta = "datos_distribucion_tiendas.xlsx"  
df = pd.read_excel(ruta)

# Crear el mapa centrado en el promedio de las coordenadas
centro_mapa = [df["Latitud_WGS84"].mean(), df["Longitud_WGS84"].mean()]
mapa = folium.Map(location=centro_mapa, zoom_start=10)

# Agregar los marcadores según el tipo
for _, fila in df.iterrows():
    # Si el tipo contiene la palabra 'Distribución', será rojo; si no, azul
    color = "red" if "Distribución" in fila["Tipo"] else "blue"

    folium.CircleMarker(
        location=[fila["Latitud_WGS84"], fila["Longitud_WGS84"]],
        radius=6,
        color=color,
        fill=True,
        fill_color=color,
        popup=fila["Nombre"]  # Se muestra al hacer clic en el punto
    ).add_to(mapa)

# Guardar el mapa en un archivo HTML interactivo
mapa.save("mapa_distribucion_tiendas.html")

print("Mapa generado correctamente: mapa_distribucion_tiendas.html")
