#!/bin/bash

echo
echo Installing LibreBeacon
echo

echo
echo Cloning repo...
echo
git clone LibreBeacon
mkdir /opt/LibreBeacon
mv LibreBeacon/* /opt/LibreBeacon

echo 
echo Making venv and installing packages...
echo 
python3 -m venv /opt/LibreBeacon/venv
source /opt/venv/bin/activate
pip install numpy scipy adafruit-circuitpython-dht adafruit-blinka

echo 
echo Setting up systemd service...
echo 
sudo cat > /etc/systemd/system/librebeacon.service << 'EOF'
[Unit]
Description=LibreBeacon Transmittion Service
After=network.target

[Service]
ExecStart=/opt/LibreBeacon/bin/python3 /opt/LibreBeacon/beacon.py
Restart=always
RestartSec=10
User=root

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl disable librebeacon
echo 
echo Systemd service ready.
echo 
deactivate
echo 
echo For first run, its recommended to edit the config in the python app, run 'sudo nano /opt/LibreBeacon/beacon.py' and edit:
echo BEACON_FREQ: Frequency of transmitter in kHz
echo BEACON_NAME: Name of beacon
echo BEACON_EMAIL: Beacon email or other contact
echo
echo When you are done you can try running 'systemctl enable librebeacon' or '/opt/LibreBeacon/bin/python3 /opt/LibreBeacon/beacon.py'
echo
echo Installation done.
echo 