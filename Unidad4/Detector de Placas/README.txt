SISTEMA DE CONTROL VEHICULAR INTELIGENTE
CONTROL VEHICULAR AUTOMATIZADO CON PYTHON, OCR Y OPENCV

Descripción general
Este proyecto implementa un sistema inteligente de reconocimiento de matrículas capaz de detectar placas mediante la cámara en tiempo real, extraer el texto con OCR avanzado, consultar una base de datos local SQLite y mostrar la información del vehículo y su propietario en una interfaz gráfica. El sistema funciona completamente local y no requiere conexión a internet.

Características principales

OCR en tiempo real

Captura y procesamiento de video con OpenCV

Base de datos SQLite reconstruida automáticamente

Interfaz gráfica con Tkinter

Preprocesamiento de imágenes para mejorar precisión

Consultas inmediatas del propietario del vehículo

Sistema ligero, sin dependencias de servidores externos

Tecnologías utilizadas
OpenCV
PaddleOCR
SQLite3
Tkinter
OS
Logging

JUSTIFICACIÓN DEL USO DE CADA LIBRERÍA

OpenCV (cv2)
Se utiliza para capturar imágenes desde la cámara, definir la región de interés, convertir la imagen a escala de grises, mejorar contraste, reducir ruido y procesar los fotogramas antes de enviarlos al motor OCR. Es indispensable para la operación del sistema, ya que permite trabajar con la imagen de la matrícula en tiempo real.

PaddleOCR
Permite realizar reconocimiento óptico de caracteres con alta precisión. Fue elegida debido a que ofrece resultados superiores a Tesseract en placas reales y funciona sin GPU, pudiendo ejecutarse totalmente en CPU. Es el componente responsable de leer y reconocer los caracteres de las placas vehiculares.

SQLite3
Se usa como sistema de base de datos local. No requiere instalación de servidores y es perfecto para aplicaciones de escritorio. Permite almacenar información de propietarios y vehículos y realizar consultas rápidas al detectar una placa. La base de datos se reconstruye automáticamente con los datos ya incluidos.

Tkinter
Proporciona la interfaz gráfica del sistema. Permite mostrar los resultados de manera visual, organizada y comprensible para el usuario final. Se utiliza para crear botones, etiquetas y paneles en los que se muestran los datos del vehículo detectado.

OS
Se utiliza para la gestión de archivos, verificar si la base de datos existe y eliminarla en caso necesario para volver a crearla. Permite que el sistema cargue siempre la base de datos más reciente.

Logging
Sirve para controlar y silenciar mensajes extensos generados por PaddleOCR, limpiando la salida en consola y evitando que el usuario vea mensajes innecesarios.

Estructura básica del proyecto

reconocimiento_placas.py: archivo principal del sistema

control_vehicular.db: base de datos generada automáticamente

estructura_base.sql: archivo SQL en el que se basa la creación de la base de datos

Carpeta media: contiene videos o capturas del funcionamiento

Instalación

Crear un entorno virtual
python -m venv .venv

Activar el entorno
..venv\Scripts\activate

Instalar dependencias necesarias
pip install paddleocr opencv-python pillow

Ejecución del sistema

python reconocimiento_placas.py

El sistema cargará el OCR, reconstruirá la base de datos y abrirá la interfaz gráfica. Desde la ventana principal, el usuario puede presionar el botón para iniciar el escaneo. La cámara se abrirá, se buscará una matrícula dentro del cuadro de lectura, y si se detecta correctamente, se mostrará toda la información del vehículo y del propietario.

Funcionamiento del OCR
El sistema realiza un preprocesamiento de imagen que incluye:

Recorte del área de lectura

Conversión a escala de grises

Aumento de contraste

Reducción de ruido

OCR en múltiples líneas

Filtrado de resultados con confianza mayor a 0.5

Base de datos incluida
Se incluyen dos tablas: Propietarios y Vehiculos. Estas tablas se llenan automáticamente con datos de prueba cada vez que se ejecuta el programa, garantizando que el sistema funcione sin configuraciones externas.

Solución de problemas

El OCR no reconoce la placa:

Aumentar iluminación

Centrar mejor la matrícula

Acercar el vehículo a la cámara

La cámara no abre:
Cerrar cualquier programa que esté usando la cámara (Zoom, Teams, etc.)

Error “No module named paddle”:
Instalar PaddlePaddle con:
pip install paddlepaddle==2.6.1