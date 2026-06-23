# LibreBeacon
LibreBeacon is a free to use python app made to  make making RF beacons easier to make.<br>

Currently only supports Raspberry pi's with RPiTX v2 or RpiTX-UI installed, These generate signals from 0Hz to 1GHz on GPIO pin 4 what can be then filtered and fed into a amplifier to transmit for long distances.<br>
DISCLAIMER: This app is curently in early beta so some parts of code could be left from the prototype made by AI.<br>


The app is pre set to use 433.8MHz as a default as its a ISM band, and a mostly clean spot.<br>
The modulation is preset is USB, but can be sometimes heard on LSB weakly too.<br>


## Installation 

Simply run:
```
curl -fsSL https://raw.githubusercontent.com/Simonko-912/LibreBeacon/main/install.sh | bash
```
Or manualy download and run install.sh<br>
The app should install by itself, and tell you what to do, if theres a error, make a issue.<br>

## Purpose

This tool was made to help with making beacons specifically with the RPiTX-UI app and raspberry pi's<br>
Its a inexpensive way to make beacons (a pi zero 2w costs 15$, but i recommend a pi 4, since the compiling process uses a lot of ram and cpu).<br>
A single pi zero in a rough terrain can have a range of around 100m, and in perfect conditions up to 800m, but its recommended to add a filtera and a power amplifier.<br>
You can also plug in a DHT11 temp sensor and transmit data from it.

## Future planned features 

1. Live audio streaming to a audio output (for example you could just transmit the raw audio over aux to a transceiver)
2. A config.json so its easier to edit values
3. Better installer