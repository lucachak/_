import webbrowser
import webbrowser
import subprocess
import socket
import signal
import time
import sys
import os

"""
ideia:
    basicamente eu quero criar uma classe, na qual vai, de 30 em 30 segundos
    re run o codigo, que, em si vai pegar o IP, e assinar ele pra mim


"""

class DjangoServerRunner:


    def __init__(self) -> None:
        pass


    def assing_ip(self)-> str:
        hostname:str = socket.gethostname()
        ip:str = socket.gethostbyname(hostname)

        return ip

    def create_host(self, port:int= 8000) -> list[str]: 
        ip:str = self.assing_ip()
        command:list[str] = [
            sys.executable, 
            'manage.py', 
            'runserver', 
            f"{ip}:{port}",
            '--noreload'
        ]
        print(f"http://{command[-2]}")
        return command

    def create_connection(self) -> int|None:

        host_command:list[str] = self.create_host()
        
        try:

            process:Popen[bytes] = subprocess.Popen(
                host_command,
                stdout=subprocess.DEVNULL,  # Ignorar stdout
                stderr=subprocess.DEVNULL,  # Ignorar stderr
                stdin=subprocess.DEVNULL,
                start_new_session=True 
            )
            pid:int = process.pid
            return pid
            

        except Exception as e:
            print(f"Error {e}")


    def kill_connection(self, pid:int) -> None:
        try:
            os.kill(pid, signal.SIGTERM)
            time.sleep(2)
            os.kill(pid, signal.SIGKILL)
        except Exception as e:
            print(f"Fuck {e}")

    
    def run(self) ->int| None:
        pid:int | None = self.create_connection()
        return pid 




def main()-> Never:

    while True:
        pid = 0
        ip_check = None
        try : 
            monitor = DjangoServerRunner()
            ip:str = monitor.assing_ip()
            pid:int|None = monitor.run()

            if ip_check == None: 
                ip_check:str = ip

            if (ip_check is not None) and (ip_check != ip):
                browser_path = {
                    'linux': "usr/bin/zen-browser %s"
                }
                try:
                    print(f"opening here => http://{ip}:8000/")
                    webbrowser.get(browser_path['linux']).open(f"http://{ip}:8000/")
                except webbrowser.Error:
                    webbrowser.open(f"http://{ip}:8000")

            time.sleep(60)
        except Exception as e:
            if pid is not None:
                monitor.kill_connection(pid)
            print(f"Killing process {e}")
            break
        except KeyboardInterrupt:
            print("\r\ncleaning... ")
            monitor.kill_connection(pid)
            break


if __name__ == "__main__":
    main()
