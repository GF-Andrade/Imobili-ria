import sys
import os
import multiprocessing
from threading import Thread
import time
import webview  # A biblioteca mágica

# --- AJUSTE DE CAMINHOS ---
if getattr(sys, 'frozen', False):
    current_dir = sys._MEIPASS
else:
    current_dir = os.path.dirname(os.path.abspath(__file__))

if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def run_backend():
    try:
        import uvicorn
        from main import app
        uvicorn.run(app, host="127.0.0.1", port=8001, log_level="error", reload=False)
    except Exception as e:
        with open("erro_backend.txt", "w") as f:
            f.write(str(e))

if __name__ == '__main__':
    multiprocessing.freeze_support()
    
    # 1. Inicia o servidor Python
    t = Thread(target=run_backend, daemon=True)
    t.start()

    # 2. Aguarda o servidor ligar
    time.sleep(2) 
    
    # 3. Cria a janela do sistema SEM BARRA DE NAVEGAÇÃO
    # maximized=True faz abrir em tela cheia respeitando a barra de tarefas
    window = webview.create_window(
        'Andrade Tech Imóveis', 
        'http://127.0.0.1:8001',
        width=1200,          # Largura inicial (será ignorada pelo maximize)
        height=800,          # Altura inicial (será ignorada pelo maximize)
        resizable=True,      # Permite redimensionar
        fullscreen=False     # IMPORTANTE: Deixe False para a barra de tarefas aparecer
    )

    
    # Inicia a janela (maximized=True garante que abra preenchendo a tela)
    webview.start(gui='edgechrome', debug=False)