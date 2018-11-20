# PyOclock 

Une horloge connectée faite avec un raspberry et un peu d'huile de coude 

Dépendances : 
- node-red
- rgbMatrix python librairie 


Installation 

Ajouter node-red au démarrage du raspberry : 

sudo systemctl enable nodered.service

Ajouter le script de démarrage du serveur tcp interne : 

Lancer le server python : 

from server folder : 

"sudo python3 main.py --led-gpio-mapping=adafruit-hat --led-rows=16 --led-cols=32 --led-brightness 50"

//commande script TODO 

A desactiver en production : 
 
- syncthing

TCP Server message structure 

- &display&&option_set&&option_name&&option_value&
- &display&&scrolling&&image_path&&message&
- &alarm&&option_set&&option_name&&option_value&

TODO : 

- Add watchdog 
- Use time or dateTime ?? 