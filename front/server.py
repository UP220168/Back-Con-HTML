#!/usr/bin/env python3
"""
Servidor HTTP simple para servir el frontend del cinema
"""
import http.server
import socketserver
import os
import sys

# Configuración
PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class HTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # Agregar headers CORS
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()
    
    def do_OPTIONS(self):
        # Manejar preflight requests
        self.send_response(200)
        self.end_headers()

def main():
    print(f"Iniciando servidor en http://localhost:{PORT}")
    print(f"Sirviendo archivos desde: {DIRECTORY}")
    print("Presiona Ctrl+C para detener el servidor")
    
    try:
        with socketserver.TCPServer(("", PORT), HTTPRequestHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
