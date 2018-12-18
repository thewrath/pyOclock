# PyOclock 

![logo](https://raw.githubusercontent.com/thewrath/pyOclock/master/credentials/logo.png=100x20)

Une horloge connectée faite avec un Raspberry et un peu de Python.  

## Dépendances :

### Dépendances logiciels : 

- node-red
- rgbMatrix python librairie 

### Dépendances matériels : 

- Carte RPI (Zéro ou B)
- Matrix led Bonnet de adafruit 
- Matrix led de adafruit (16x32)

## Installation :

### Lancer le server python : 

`sudo python3 main.py --led-gpio-mapping=adafruit-hat --led-rows=16 --led-cols=32 --led-brightness 50"`

### Lancer Node-red : 

Si Node-red n'est pas installer sur votre RPI : [Installer Node-red sur RPI](https://nodered.org/docs/hardware/raspberrypi)

Une fois l'installation terminé, vous pouvez importer le contenu du fichier `node-red/flow.json` dans un nouveau flow Node-red.

## Faire fonctionner le système au démarrage du RPI : 

### Ajouter node-red au démarrage du raspberry : 

`sudo systemctl enable nodered.service`

### Ajouter le script de démarrage du serveur tcp interne : 

Placer le service dans `/etc/systemd/system` :

`sudo cp systemctl/pyOclock.service /etc/systemd/system/pyOclock.service`

Mettre à jour les services de systemctl : 

`systemctl --system daemon-reload`

Activer le service pyOclock : 

`systemctl enable pyOclock.service`

Démarrer le service pyOclock :

`systemctl start pyOclock.service`

## Pour les développeur : 

La logique du système réside au coeur de node-red qui envoie des message sur un serveur TCP (présent sur le RPI).
Vous pouvez facilement modifier et adapter selon vos besoins le système node-red pour qu'il commande le serveur TCP et affiche ce que vous voulez. 

### Serveur node-red : 

Node-red possède une page d'administration et de configuration sur `127.0.0.1:1880`

### Serveur TCP interne :

Ce serveur est la pour commander la matrice de led et prochainement l'audio du RPI. 
Il écoute sur le port 16666, biensur vous pouvez modifier ça dans le code. 

#### Liste des commandes du serveur TCP interne  

- &display&&option_set&&option_name&&option_value&
- &display&&type&&image_path&&message&
- &alarm&&option_set&&option_name&&option_value&

### TODO : 

- Add watchdog, un thread capable d'en reanimer d'autre lorsque ceci ne répondent plus 
- Add stop function  
- log -> fichier et rendre le fichier accéssible depuis l'api node RED 
- supprimer la partie image_path pour l'envoie d'un msg 
- Faire un fichier de conf modifiable depuis node-red 
- Gestion du chemin absolue pour gérer les assets 
