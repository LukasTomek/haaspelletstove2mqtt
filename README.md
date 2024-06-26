# haaspelletstove2mqtt
Decode the serial output from a Haas & Sohn Pellet Stove and send it to MQTT (incl. Home Assistant auto discovery).

Modify original code from [vandenberghev/haaspelletstove2mqtt](https://github.com/vandenberghev/haaspelletstove2mqtt), to use with Haas & Sohn Hydronic Pelletstove HSP 6-WT 537.08 RLU (V7.11)

This script requires changing the `ser. Ausgabe` (serial output) parameter on the stove to `DAQ`.
To do this, press `Menu`, hold `+` and press `-` 6 times. This enables the `Service:` menu item.
Go to `Service:` > `Par. general` > `ser. Ausgabe` and choose `DAQ`.

pip install paho-mqtt serial

This script can be run as a service with systemd.

EXAMPLE /lib/systemd/system/haaspelletstove2mqtt.service:

    [Unit]
    Description=haaspelletstove2mqtt
    After=network-online.target

    [Service]
    ExecStart=/usr/bin/python3 /home/someuser/HaasPelletStove2MQTT.py
    Restart=on-failure
    Type=idle

    [Install]
    WantedBy=multi-user.target


Steps:

  1. Create the .service file as described above in `/lib/systemd/system/`
  2. `sudo systemctl daemon-reload`
  3. `sudo systemctl enable haaspelletstove2mqtt.service`
  4. `sudo service haaspelletstove2mqtt start`
  5. `sudo service haaspelletstove2mqtt status`
