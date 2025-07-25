# API to serve JSON data for a web dashboard y servir frontend
from flask import Flask, jsonify, send_from_directory
import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.database import obtener_conexion, guardar_producto
from datetime import datetime

FRONTEND_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
app = Flask(__name__, static_folder=FRONTEND_FOLDER, static_url_path="")
# Endpoint to get the list of products with metadata
@app.route("/data/results.json")
def obtener_resultados():
    try:
        conn = obtener_conexion()
        cur = conn.cursor()
        cur.execute("SELECT titulo, precio, url_imagen FROM productos ORDER BY id DESC;")
        filas = cur.fetchall()
        cur.close()
        conn.close()
        resultados = []
        for i, fila in enumerate(filas):
            resultados.append({
                "id": i + 1,
                "titulo": fila[0],
                "descripcion": f"Precio: {fila[1]}",
                "url_imagen": fila[2]
            })
        return jsonify(resultados)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint para eventos (lee el archivo events.json)
@app.route("/data/events.json")
def obtener_eventos():
    try:
        events_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'events.json'))
        with open(events_path, 'r', encoding='utf-8') as f:
            eventos = json.load(f)
        return jsonify(eventos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# Endpoint to get the list of downloaded files with metadata
@app.route("/data/files.json")
def obtener_archivos():
    try:
        conn = obtener_conexion()
        cur = conn.cursor()
        cur.execute("SELECT nombre_archivo, url FROM archivos_descargados ORDER BY id DESC;")
        filas = cur.fetchall()
        cur.close()
        conn.close()
        archivos = []
        for i, fila in enumerate(filas):
            nombre_archivo = fila[0]
            ext = nombre_archivo.split('.')[-1].upper()
            archivos.append({
                "id": i + 1,
                "nombre_archivo": nombre_archivo,
                "tipo": ext,
                "url": fila[1]
            })
        return jsonify(archivos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# Endpoint to check if the server is running

# Servir index.html y archivos estáticos del frontend
@app.route("/")
def root():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == "__main__":
    app.run(port=5500, debug=True)