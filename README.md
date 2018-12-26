# PyOclock 
<img src="https://img.shields.io/badge/coverage-50%25-yellowgreen.svg" alt="drawing" width="200"/>

<img src="https://raw.githubusercontent.com/thewrath/pyOclock/master/credentials/logo.png" alt="drawing" width="200"/>

## **V0.7b**  *Cogsworth prototype*

## A connected clock made with a Raspberry and a little Python  

## Dependencies :

### Softwares dependencies : 

- node-red
- rgbMatrix python librairie 

### Hardware dependencies : 

- RPI card (Zero or B or other)
- Matrix LED Beanie of adafruit 
- Matrix LED adafruit LED (16x32)

## Installation :

### Launch internal TCP server (write in Python) : 

`sudo python3 main.py --led-gpio-mapping=adafruit-hat --led-rows=16 --led-cols=32 --led-brightness 50`

### Launch Node-red : 

If Node-red is not installed on your RPI : [Node-red installation](https://nodered.org/docs/hardware/raspberrypi)

Once the installation is finished, you can import the contents of the file `node-red/flow.json` into a new Node-red flow.

## Run the system at RPI startup : 

### Add node-red when starting the Raspberry : 

`sudo systemctl enable nodered.service`

### Add the start script of the internal tcp server : 

Place the service in `/etc/systemd/system` :

`sudo cp systemctl/pyOclock.service /etc/systemd/system/pyOclock.service`

Update systemctl services : 

`systemctl --system daemon-reload`

Enable pyOclock service : 

`systemctl enable pyOclock.service`

Start the pyOclock service :

`systemctl start pyOclock.service`

## For developers : 

The system logic lies at the heart of node-red, which sends messages to a TCP server (present on the RPI).
You can easily modify and adapt the node-red system to your needs so that it can control the TCP server and display what you want. 

### Node-red server : 

Node-red has an administration and configuration page on `127.0.0.1:1880`

### Internal TCP server :

This server is there to control the LED matrix and soon the RPI audio. 
He listens on port 16666, of course you can change that in the code.

#### List of commands for the internal TCP server  

- &display&&option_set&&option_name&&option_value&
- &display&&type&&image_path&&message&
- &alarm&&option_set&&option_name&&option_value&


### Contribute :

All contributions are welcome, whether it is a bug in the code or to add features.
Of course you are free to use the software as you wish, as long as you comply with the license. 

You can contact me on github or by email 

### TODO : 

- Add watchdog, a thread capable of resuscitating others when this no longer responds 
- Add stop function  
- log -> file and make the file accessible from the RED api node 
- delete the image_path part to send an msg 
- Make a conf file editable from node-red 
- Management of the absolute path to manage assets 
- Add more configurable variables directly from the command 
- Add compatibility with all matrix sizes 
- Add compatibility with LCD screens 
