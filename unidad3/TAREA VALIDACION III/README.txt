 Algoritmo Genético - Optimización de Rutas (TSP)
 Descripción General

Este proyecto implementa un algoritmo genético (AG) en Python para resolver un problema de optimización de rutas —conocido comúnmente como el Problema del Viajero (TSP).

El objetivo es encontrar la ruta más corta que conecta un conjunto de municipios, visitando cada uno exactamente una vez y regresando al punto de partida.
El código fue desarrollado desde cero como parte de la materia Tópicos de Inteligencia Artificial, utilizando un enfoque modular y documentado.

El algoritmo combina selección natural, reproducción, cruce, mutación y elitismo para evolucionar progresivamente hacia una solución más óptima en cada generación.

⚙️ Dependencias

Antes de ejecutar el script, asegúrate de tener instaladas las siguientes bibliotecas de Python:

pip install numpy pandas matplotlib

Bibliotecas utilizadas:

random → generación aleatoria de rutas y eventos de mutación.

numpy → cálculos numéricos, distancias euclidianas y manejo de matrices.

pandas → manipulación de datos para la selección por ruleta.

matplotlib → visualización gráfica de la mejor ruta encontrada.

 Ejecución del Programa

Clona o descarga el proyecto en tu equipo.

Abre una terminal en la carpeta del proyecto.

Ejecuta el script principal:

python AG.py


El programa imprimirá la distancia inicial, el progreso de las generaciones y la mejor ruta final optimizada.
Al finalizar, mostrará un gráfico con la ruta óptima generada.

 Desglose del Funcionamiento
1. Inicialización de la Población 

Se genera una población inicial de rutas aleatorias.
Cada individuo es una permutación diferente de los municipios definidos.
Esto garantiza diversidad genética en la población inicial, esencial para explorar el espacio de soluciones.

def crearRuta(listaMunicipios):
    return random.sample(listaMunicipios, len(listaMunicipios))

2. Función de Aptitud 

Evalúa la calidad de cada individuo.
La aptitud se define como el inverso de la distancia total recorrida:

Fitness = 1 / distancia_total

Una menor distancia equivale a una mayor aptitud.
La función distanciaRuta() calcula la distancia total entre cada par de municipios consecutivos, cerrando el ciclo al final.

self.f_aptitud = 1 / float(self.distanciaRuta())

3. Selección 

Se realiza mediante una combinación de elitismo y selección por ruleta:

Elitismo: conserva un porcentaje de los mejores individuos sin modificarlos.

Ruleta: asigna probabilidades de selección proporcionales a la aptitud de cada ruta, manteniendo diversidad.

Esto garantiza un balance entre explotación (usar las mejores soluciones actuales) y exploración (buscar nuevas rutas prometedoras).

4. Crossover (Cruce) 

Se utiliza un método de Ordered Crossover (OX):

Se selecciona aleatoriamente un segmento de un padre.

Se completan las posiciones restantes con los municipios del otro padre que no aparecen en el segmento.

Esto produce un hijo válido (sin duplicados) que hereda características de ambos padres.

5. Mutación 

Para mantener la diversidad genética, se aplica una mutación por intercambio (swap mutation):
dos municipios intercambian posiciones con una pequeña probabilidad (razonMutacion).

Este proceso evita que la población caiga en óptimos locales y mejora la capacidad de búsqueda del algoritmo.

6. Nueva Generación 

Cada ciclo evolutivo repite las siguientes fases:

Evaluación de aptitud.

Selección de padres.

Cruce para generar descendencia.

Aplicación de mutación.

Sustitución de la población anterior.

El proceso se repite durante un número determinado de generaciones (generaciones=500).

7. Visualización Gráfica 

El script incluye una función graficarRuta() que genera una representación visual de la mejor ruta obtenida:

Puntos azules → municipios.

Línea verde → ruta optimizada.

Punto rojo → ciudad de inicio y fin.

Esta visualización permite verificar fácilmente la calidad de la solución final.

 Resultados

Durante la ejecución del programa se obtiene una salida similar a:

Distancia Inicial: 24.9513
Generación 50: Mejor distancia actual = 24.7624 | Mejor global = 24.7624
...
Distancia Final: 24.7624


Mejor ruta encontrada:

[(37.3891,-5.9845), (43.3623,-5.845), (41.6488,-0.8891), (41.3784,2.1925), (39.4699,-0.3763), (40.4168,-3.7038)]


La gráfica generada muestra el recorrido optimizado entre los municipios.

 Conclusiones

El algoritmo genético demostró una gran capacidad para encontrar soluciones eficientes a problemas de optimización combinatoria.
Gracias a su enfoque evolutivo y probabilístico, logró mejorar progresivamente las soluciones en cada generación.

La estructura modular del código y la documentación interna permiten su fácil modificación para otros problemas, como:

Rutas de entrega.

Diseño de redes logísticas.

Planificación de tareas o asignaciones.

El equilibrio entre diversidad genética y selección de élite fue clave para obtener una convergencia estable sin perder la exploración del espacio de búsqueda.

 Autores

García Sánchez Sergio Jesús
Darío Corrales Palazuelos
Carrera: Ingeniería en Sistemas Computacionales
Materia: Tópicos de Inteligencia Artificial
Docente: Zuriel Dathan Mora Félix
Fecha: Noviembre 2025