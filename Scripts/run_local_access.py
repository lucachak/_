import subprocess
import socket
import time
import sys 

def run_django_server():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    port = 8000
    command = [
            sys.executable, 'manage.py', 'runserver', f"{local_ip}:{port}"
            ]

    print(f"Iniciando Django...\nLink => http://{local_ip}:{port}")

    processo = subprocess.Popen( 
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
            )

    return processo

if __name__ == "__main__":

    try : 
        processo = run_django_server()
        print(f"Servidor PID=> {processo.pid}")
        time.sleep(1)
        if processo.pid is None:
            print("server is running...")
        else:
            stdout, stderr = processo.communicate()
            print(f"Erro: {stderr}")
    except:
        print("\nClosing server...")
