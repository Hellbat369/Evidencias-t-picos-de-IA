import cv2
import sqlite3
import logging
import tkinter as tk
from tkinter import messagebox, ttk
from paddleocr import PaddleOCR
import os

# ==========================================
# 1. CONFIGURACIÓN E INICIALIZACIÓN
# ==========================================
logging.getLogger('ppocr').setLevel(logging.ERROR)

print("🚀 CARGANDO MOTORES DE IA...")
try:
    ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False, show_log=False, det_db_thresh=0.3)
except Exception as e:
    print(f"❌ Error fatal iniciando OCR: {e}")
    exit()

DB_NAME = 'control_vehicular.db'

# ==========================================
# 2. GESTIÓN DE BASE DE DATOS (IMPORTACIÓN AUTOMÁTICA)
# ==========================================
def preparar_base_datos():
    """
    Recrea la base de datos basándose EXACTAMENTE en tu archivo SQL subido.
    Traduce la sintaxis MySQL a SQLite.
    """
    try:
        # Borramos el archivo viejo para asegurar que se carguen tus datos nuevos
        if os.path.exists(DB_NAME):
            os.remove(DB_NAME)
            print("♻️ Base de datos antigua eliminada para actualización.")

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # 1. TABLA PROPIETARIOS
        cursor.execute("""
            CREATE TABLE Propietarios (
                id_propietario INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                telefono TEXT,
                correo TEXT UNIQUE
            )
        """)
        
        # 2. TABLA VEHICULOS (Placa es PK, id_propietario es FK)
        cursor.execute("""
            CREATE TABLE Vehiculos (
                placa TEXT PRIMARY KEY,
                marca TEXT NOT NULL,
                modelo TEXT NOT NULL,
                anio INTEGER NOT NULL,
                id_propietario INTEGER,
                FOREIGN KEY(id_propietario) REFERENCES Propietarios(id_propietario)
            )
        """)

        # 3. INSERTAR DATOS: PROPIETARIOS (Según tu archivo)
        datos_propietarios = [
            ('Roberto Sánchez', '667-123-4567', 'roberto.sanchez@email.com'),
            ('Laura Fernández', '667-987-6543', 'laura.fer@webmail.com'),
            ('Miguel Ángel Torres', '667-555-8888', 'miguel.torres@corp.net'),
            ('Diana Ruiz', '667-444-1111', 'diana.ruiz@social.org')
        ]
        cursor.executemany("INSERT INTO Propietarios (nombre, telefono, correo) VALUES (?, ?, ?)", datos_propietarios)
        
        # 4. INSERTAR DATOS: VEHICULOS (Según tu archivo)
        # Nota: Ajusté los IDs manualmente para que coincidan con el orden de inserción de arriba
        datos_vehiculos = [
            ('VSF-82-88', 'Chevrolet', 'Corsa', 2007, 1),
            ('ZJS-512-A', 'Toyota', 'Tacoma', 2001, 2),
            ('VLT-632-R', 'Toyota', 'Camry', 2006, 2),
            ('VTB-82-62', 'Dodge', 'Altitude', 2012, 3),
            ('VTB-82-63', 'Dodge', 'Journey', 2015, 3),
            ('VGN-264-D', 'Hyundai', 'Tucson', 2024, 4)
        ]
        cursor.executemany("INSERT INTO Vehiculos (placa, marca, modelo, anio, id_propietario) VALUES (?, ?, ?, ?, ?)", datos_vehiculos)
        
        conn.commit()
        conn.close()
        print("✅ Base de datos actualizada con los datos del archivo SQL.")
        return True
    except Exception as e:
        messagebox.showerror("Error BD", f"Error creando base de datos: {e}")
        return False

def buscar_dueno_sql(texto_placa):
    if not texto_placa or len(texto_placa) < 3: return None
    
    # Limpieza: Quitamos guiones para buscar, pero la BD tiene guiones en algunos casos.
    # Estrategia: Buscar 'LIKE' flexible.
    placa_limpia = "".join(c for c in texto_placa if c.isalnum()).upper()

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Consulta actualizada con tus nuevos campos (ANIO y CORREO)
        query = """
            SELECT v.placa, v.marca, v.modelo, v.anio, p.nombre, p.telefono, p.correo
            FROM Vehiculos v 
            JOIN Propietarios p ON v.id_propietario = p.id_propietario
            WHERE replace(v.placa, '-', '') = ? OR ? LIKE '%' || replace(v.placa, '-', '') || '%'
        """
        cursor.execute(query, (placa_limpia, placa_limpia))
        resultado = cursor.fetchone()
        conn.close()
        return resultado
    except Exception as e:
        print(f"Error DB: {e}")
        return None

# ==========================================
# 3. LÓGICA DE ESCANEO (OPENCV)
# ==========================================
def preprocesar_imagen(img):
    try:
        gris = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gris = cv2.convertScaleAbs(gris, alpha=1.5, beta=0) 
        gris = cv2.GaussianBlur(gris, (3, 3), 0)
        return gris
    except:
        return img

def ejecutar_camara():
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)
    
    ancho_roi, alto_roi = 600, 150
    frame_count = 0
    SKIP_FRAMES = 5
    
    datos_encontrados = None

    while True:
        ret, frame = cap.read()
        if not ret: break
        
        frame_count += 1
        h, w, _ = frame.shape
        x1, y1 = (w - ancho_roi) // 2, (h - alto_roi) // 2
        x2, y2 = x1 + ancho_roi, y1 + alto_roi

        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 100, 0), 2)
        cv2.putText(frame, "Presione 'q' para cancelar", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)

        if frame_count % SKIP_FRAMES == 0:
            roi = frame[y1:y2, x1:x2]
            roi_procesada = preprocesar_imagen(roi)
            
            try:
                resultado = ocr.ocr(roi_procesada, cls=False)
                if resultado and resultado[0]:
                    for linea in resultado[0]:
                        texto = linea[1][0]
                        confianza = linea[1][1]
                        
                        if confianza > 0.5:
                            print(f"Leyendo: {texto}")
                            info = buscar_dueno_sql(texto)
                            if info:
                                datos_encontrados = info
                                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 5)
                                cv2.putText(frame, f"PLACA: {info[0]}", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
                                cv2.imshow("ESCANER ACTIVO", frame)
                                cv2.waitKey(1000) # 1 segundo para ver resultado
                                cap.release()
                                cv2.destroyAllWindows()
                                return datos_encontrados
            except Exception as e:
                pass

        cv2.imshow("ESCANER ACTIVO", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()
    return None

# ==========================================
# 4. INTERFAZ GRÁFICA (TKINTER)
# ==========================================
def iniciar_gui():
    ventana = tk.Tk()
    ventana.title("Sistema de Control Vehicular Inteligente")
    ventana.geometry("600x600") # Un poco más alto
    ventana.configure(bg="#f0f0f0")

    style = ttk.Style()
    style.configure("Title.TLabel", font=("Arial", 16, "bold"), background="#f0f0f0", foreground="#333")

    lbl_titulo = ttk.Label(ventana, text="🚔 DETECTOR DE MATRÍCULAS", style="Title.TLabel")
    lbl_titulo.pack(pady=20)

    frame_resultados = tk.Frame(ventana, bg="white", bd=2, relief="groove")
    frame_resultados.pack(fill="both", expand=True, padx=20, pady=10)

    # --- VARIABLES ACTUALIZADAS SEGÚN TU SQL ---
    v_placa = tk.StringVar(value="---")
    v_marca = tk.StringVar(value="---")
    v_modelo = tk.StringVar(value="---")
    v_anio = tk.StringVar(value="---")     # Antes Color
    v_propietario = tk.StringVar(value="---")
    v_telefono = tk.StringVar(value="---")
    v_correo = tk.StringVar(value="---")   # Antes Dirección
    v_estado = tk.StringVar(value="Esperando escaneo...")

    def crear_fila(padre, etiqueta, variable):
        f = tk.Frame(padre, bg="white")
        f.pack(fill="x", padx=10, pady=5)
        tk.Label(f, text=etiqueta, font=("Arial", 10, "bold"), width=15, anchor="w", bg="white").pack(side="left")
        tk.Label(f, textvariable=variable, font=("Arial", 11), fg="#333", bg="#e8f0fe", width=30, anchor="w", padx=5).pack(side="left", fill="x", expand=True)

    # SECCIÓN VEHÍCULO
    tk.Label(frame_resultados, text="DATOS DEL VEHÍCULO", bg="#333", fg="white", font=("Arial", 10, "bold")).pack(fill="x")
    crear_fila(frame_resultados, "Placa:", v_placa)
    crear_fila(frame_resultados, "Marca:", v_marca)
    crear_fila(frame_resultados, "Modelo:", v_modelo)
    crear_fila(frame_resultados, "Año:", v_anio) # Cambiado

    tk.Label(frame_resultados, text="", bg="white").pack()

    # SECCIÓN PROPIETARIO
    tk.Label(frame_resultados, text="DATOS DEL PROPIETARIO", bg="#333", fg="white", font=("Arial", 10, "bold")).pack(fill="x")
    crear_fila(frame_resultados, "Nombre:", v_propietario)
    crear_fila(frame_resultados, "Teléfono:", v_telefono)
    crear_fila(frame_resultados, "Correo:", v_correo) # Cambiado

    lbl_estado = tk.Label(ventana, textvariable=v_estado, bg="#f0f0f0", fg="gray", font=("Arial", 9, "italic"))
    lbl_estado.pack(pady=5)

    def accion_escanear():
        v_estado.set("Iniciando cámara...")
        ventana.update()
        datos = ejecutar_camara()
        
        if datos:
            # Desempaquetado según la nueva consulta SQL
            # placa, marca, modelo, ANIO, nombre, telefono, CORREO
            v_placa.set(datos[0])
            v_marca.set(datos[1])
            v_modelo.set(datos[2])
            v_anio.set(str(datos[3]))     # Es int, convertir a str
            v_propietario.set(datos[4])
            v_telefono.set(datos[5])
            v_correo.set(datos[6])
            
            v_estado.set("✅ Vehículo identificado.")
            messagebox.showinfo("Éxito", f"Vehículo detectado: {datos[0]}")
        else:
            v_estado.set("Escaneo cancelado.")

    btn_scan = tk.Button(ventana, text="📷 INICIAR ESCANEO", font=("Arial", 14, "bold"), 
                         bg="#0055aa", fg="white", activebackground="#004488", 
                         cursor="hand2", command=accion_escanear)
    btn_scan.pack(pady=20, ipadx=20, ipady=10)

    ventana.mainloop()

if __name__ == "__main__":
    # Esto asegura que se cargue tu archivo SQL la primera vez
    if preparar_base_datos():
        iniciar_gui()