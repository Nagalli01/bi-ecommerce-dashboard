#!/usr/bin/env python3
"""
Launch Dashboard Web — Streamlit + Ngrok
Gera um link publico para acessar o dashboard de qualquer lugar.
"""

import os
import sys
import threading
import subprocess
import time
import webbrowser

def start_streamlit():
    script = os.path.join(os.path.dirname(__file__), "dashboard_app.py")
    root = os.path.dirname(os.path.dirname(__file__))
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", script,
        "--server.port", "8501",
        "--server.headless", "true",
        "--server.fileWatcherType", "none",
    ], cwd=root)

def start_ngrok():
    from pyngrok import ngrok
    time.sleep(3)
    tunnel = ngrok.connect(8501)
    url = tunnel.public_url
    print(f"\n{'='*60}")
    print(f"  DASHBOARD PUBLICADO!")
    print(f"  Acesse: {url}")
    print(f"{'='*60}")
    print(f"\n  Compartilhe este link com qualquer pessoa.")
    print(f"  Pressione Ctrl+C para encerrar.\n")
    webbrowser.open(url)

if __name__ == "__main__":
    print("Iniciando Dashboard Streamlit + Ngrok...")
    print("Abrindo navegador automaticamente...\n")
    
    t1 = threading.Thread(target=start_streamlit, daemon=True)
    t2 = threading.Thread(target=start_ngrok, daemon=True)
    
    t1.start()
    t2.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nEncerrando...")
