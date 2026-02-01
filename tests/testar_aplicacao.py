#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import time
import webbrowser

def testar_aplicacao():
    print("🧪 Testando aplicação...")
    
    try:
        process = subprocess.Popen(['python', 'app.py'])
        time.sleep(3)
        webbrowser.open('http://127.0.0.1:5000/home')
        print("✅ Aplicação iniciada")
        input("Pressione Enter para parar...")
        process.terminate()
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    testar_aplicacao()
