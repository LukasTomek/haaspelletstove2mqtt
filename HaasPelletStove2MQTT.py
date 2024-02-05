#!/usr/bin/python3
import configparser
import HaasPelletStove as uart
import HaasPelletStoveHTTP as http
import json
import paho.mqtt.client as mqtt
import time


config = configparser.ConfigParser()
config.read('config.ini')

#### USER MQTT CONFIG ####
MQTT_BROKER = config['MQTT_BROKER']['MQTT_BROKER']
MQTT_PORT = int(config['MQTT_BROKER']['MQTT_PORT'])
MQTT_KEEPALIVE_INTERVAL = int(config['MQTT_BROKER']['MQTT_KEEPALIVE_INTERVAL'])

HASS_TOPIC_PREFIX = "homeassistant" # Default 'homeassistant'
HASS_ENTITY_NAME = "mypelletstove"  # Used for topics + sensor prefix
HASS_CONFIG_SUFFIX = "config"       # Should not be changed
HASS_STATE_SUFFIX = "state"         # Should not be changed

USERNAME = config['MQTT_LOGIN']['USERNAME']
PASSWORD = config['MQTT_LOGIN']['PASSWORD']

SECONDS_BETWEEN_REFRESH = 10

#### MAPPINGS TO HOME ASSISTANT ####
def getHassComponentTypeFor(key):
    if key in KNOWN_KEYS:
        config = KNOWN_KEYS[key]
        if CONFIG_SENSOR_TYPE in config: return config[CONFIG_SENSOR_TYPE]
    return "sensor" #Fallback

def getBaseTopic(key):
    return HASS_TOPIC_PREFIX + "/" + getHassComponentTypeFor(key) + "/" + HASS_ENTITY_NAME + "_" + key

def getStateTopic(key):
    return getBaseTopic(key) + "/" + HASS_STATE_SUFFIX

def getConfigTopic(key):
    return getBaseTopic(key) + "/" + HASS_CONFIG_SUFFIX

def getConfigInfo(key):
    configInfo = {}
    configInfo["state_topic"] = getStateTopic(key)
    configInfo["name"] = key
    if key in KNOWN_KEYS:
        config = KNOWN_KEYS[key]
        for ck in INCLUDED_CONFIG_KEYS:
            if ck in config: configInfo[ck] = config[ck]
    return str(json.dumps(configInfo))

#### KNOWN KEYS ####
#Index vs configuration
CONFIG_UNIT_OF_MEASUREMENT = "unit_of_measurement"
CONFIG_NAME = "name"
CONFIG_SENSOR_TYPE = "sensor_type"
CONFIG_DEVICE_CLASS = "device_class"
CONFIG_PAYLOAD_ON = "payload_on"
CONFIG_PAYLOAD_OFF = "payload_off"
CONFIG_STATE_TOPIC = 'state_topic'
CONFIG_COMMAND_TOPIC = 'command_topic'

INCLUDED_CONFIG_KEYS = [CONFIG_UNIT_OF_MEASUREMENT, CONFIG_DEVICE_CLASS, CONFIG_PAYLOAD_ON, CONFIG_PAYLOAD_OFF, CONFIG_COMMAND_TOPIC] #, CONFIG_NAME]

KNOWN_KEYS = {
    "switch_stove": { CONFIG_COMMAND_TOPIC: "homeassistant/switch/mypelletstove_switch_stove", CONFIG_SENSOR_TYPE: "switch", CONFIG_PAYLOAD_ON: "true", CONFIG_PAYLOAD_OFF: "false"},
    "mode": { CONFIG_UNIT_OF_MEASUREMENT: "", CONFIG_NAME: "Mode", CONFIG_SENSOR_TYPE: "sensor" },
    "unknown_0": { CONFIG_UNIT_OF_MEASUREMENT: "", CONFIG_NAME: "Seconds in stage", CONFIG_SENSOR_TYPE: "sensor" },
    "status": { CONFIG_UNIT_OF_MEASUREMENT: "", CONFIG_NAME: "Seconds in stage", CONFIG_SENSOR_TYPE: "sensor" },
    "unknown_4": { CONFIG_UNIT_OF_MEASUREMENT: "", CONFIG_NAME: "Seconds in stage", CONFIG_SENSOR_TYPE: "sensor" },
    "unknown_10": { CONFIG_UNIT_OF_MEASUREMENT: "", CONFIG_NAME: "Seconds in stage", CONFIG_SENSOR_TYPE: "sensor" },
    "unknown_21": { CONFIG_UNIT_OF_MEASUREMENT: "", CONFIG_NAME: "Seconds in stage", CONFIG_SENSOR_TYPE: "sensor" },
    "unknown_23": { CONFIG_UNIT_OF_MEASUREMENT: "", CONFIG_NAME: "Seconds in stage", CONFIG_SENSOR_TYPE: "sensor" },
    "bitmask_26": { CONFIG_UNIT_OF_MEASUREMENT: "", CONFIG_NAME: "Seconds in stage", CONFIG_SENSOR_TYPE: "sensor" },
    "bitmask_27": { CONFIG_UNIT_OF_MEASUREMENT: "", CONFIG_NAME: "Seconds in stage", CONFIG_SENSOR_TYPE: "sensor" },
    "bitmask_28": { CONFIG_UNIT_OF_MEASUREMENT: "", CONFIG_NAME: "Seconds in stage", CONFIG_SENSOR_TYPE: "sensor" },
    "bitmask_29": { CONFIG_UNIT_OF_MEASUREMENT: "", CONFIG_NAME: "Seconds in stage", CONFIG_SENSOR_TYPE: "sensor" },
    "bitmask_30": { CONFIG_UNIT_OF_MEASUREMENT: "", CONFIG_NAME: "Seconds in stage", CONFIG_SENSOR_TYPE: "sensor" },
    "bitmask_31": { CONFIG_UNIT_OF_MEASUREMENT: "", CONFIG_NAME: "Seconds in stage", CONFIG_SENSOR_TYPE: "sensor" },
    "bitmask_32": { CONFIG_UNIT_OF_MEASUREMENT: "", CONFIG_NAME: "Seconds in stage", CONFIG_SENSOR_TYPE: "sensor" },
    "bitmask_33": { CONFIG_UNIT_OF_MEASUREMENT: "", CONFIG_NAME: "Seconds in stage", CONFIG_SENSOR_TYPE: "sensor" },
    "desired_water_temp": { CONFIG_UNIT_OF_MEASUREMENT: "°C", CONFIG_NAME: "Water (desired)", CONFIG_SENSOR_TYPE: "sensor" },
    "current_water_temp": { CONFIG_UNIT_OF_MEASUREMENT: "°C", CONFIG_NAME: "Water", CONFIG_SENSOR_TYPE: "sensor" },
    "current_flue_gas_temp": { CONFIG_UNIT_OF_MEASUREMENT: "°C", CONFIG_NAME: "Flue gas", CONFIG_SENSOR_TYPE: "sensor" },
    "current_room_temp": { CONFIG_UNIT_OF_MEASUREMENT: "°C", CONFIG_NAME: "Room", CONFIG_SENSOR_TYPE: "sensor" },
    "desired_room_temp": { CONFIG_UNIT_OF_MEASUREMENT: "°C", CONFIG_NAME: "Room (target)", CONFIG_SENSOR_TYPE: "sensor" },
    "desired_flue_gas_temp": { CONFIG_UNIT_OF_MEASUREMENT: "°C", CONFIG_NAME: "Flue gas (target)", CONFIG_SENSOR_TYPE: "sensor" },
    "mat_soll_reg": { CONFIG_UNIT_OF_MEASUREMENT: "%", CONFIG_NAME: "mat_soll_reg", CONFIG_SENSOR_TYPE: "sensor" },
    "sz_soll_reg": { CONFIG_UNIT_OF_MEASUREMENT: "%", CONFIG_NAME: "sz_soll_reg", CONFIG_SENSOR_TYPE: "sensor" },
    "correction_fan_percent": { CONFIG_UNIT_OF_MEASUREMENT: "%", CONFIG_NAME: "Fan correction", CONFIG_SENSOR_TYPE: "sensor" },
    "desired_fan_percent": { CONFIG_UNIT_OF_MEASUREMENT: "%", CONFIG_NAME: "Fan (target)", CONFIG_SENSOR_TYPE: "sensor" },
    "desired_fan_rpm": { CONFIG_UNIT_OF_MEASUREMENT: "rpm", CONFIG_NAME: "Fan (target)", CONFIG_SENSOR_TYPE: "sensor" },
    "current_fan_rpm": { CONFIG_UNIT_OF_MEASUREMENT: "rpm", CONFIG_NAME: "Fan", CONFIG_SENSOR_TYPE: "sensor" },
    "desired_material_percent": { CONFIG_UNIT_OF_MEASUREMENT: "%", CONFIG_NAME: "Pellet feed", CONFIG_SENSOR_TYPE: "sensor" },
    "material_consumed_kg": { CONFIG_UNIT_OF_MEASUREMENT: "kg", CONFIG_NAME: "Pellets consumed", CONFIG_SENSOR_TYPE: "sensor" },
    "burning_time_hours": { CONFIG_UNIT_OF_MEASUREMENT: "h", CONFIG_NAME: "Total burning time", CONFIG_SENSOR_TYPE: "sensor" },
    "desired_chamber_temp": { CONFIG_UNIT_OF_MEASUREMENT: "°C", CONFIG_NAME: "Chamber (desired)", CONFIG_SENSOR_TYPE: "sensor" },
    "current_chamber_temp": { CONFIG_UNIT_OF_MEASUREMENT: "°C", CONFIG_NAME: "Chamber", CONFIG_SENSOR_TYPE: "sensor" },
    "current_chamber2_temp": { CONFIG_UNIT_OF_MEASUREMENT: "°C", CONFIG_NAME: "Chamber 2", CONFIG_SENSOR_TYPE: "sensor" },
    "seconds_in_current_stage": { CONFIG_UNIT_OF_MEASUREMENT: "s", CONFIG_NAME: "Seconds in stage", CONFIG_SENSOR_TYPE: "sensor" },
    "door_is_closed": { CONFIG_DEVICE_CLASS: "door", CONFIG_NAME: "Door", CONFIG_SENSOR_TYPE: "binary_sensor", CONFIG_PAYLOAD_ON: "True", CONFIG_PAYLOAD_OFF: "False" },
    "pelletfeed_is_on": { CONFIG_DEVICE_CLASS: "moving", CONFIG_NAME: "Pellet feed", CONFIG_SENSOR_TYPE: "binary_sensor", CONFIG_PAYLOAD_ON: "True", CONFIG_PAYLOAD_OFF: "False" },
    "igniter_is_on": { CONFIG_DEVICE_CLASS: "heat", CONFIG_NAME: "Igniter", CONFIG_SENSOR_TYPE: "binary_sensor", CONFIG_PAYLOAD_ON: "True", CONFIG_PAYLOAD_OFF: "False" },
    "stove_is_heating": { CONFIG_NAME: "Heating", CONFIG_SENSOR_TYPE: "binary_sensor", CONFIG_PAYLOAD_ON: "True", CONFIG_PAYLOAD_OFF: "False" },
    "pump_is_on": { CONFIG_NAME: "Pump", CONFIG_SENSOR_TYPE: "binary_sensor", CONFIG_PAYLOAD_ON: "True", CONFIG_PAYLOAD_OFF: "False" }
    #"": { CONFIG_UNIT_OF_MEASUREMENT: "°C", CONFIG_NAME: "", CONFIG_SENSOR_TYPE: "sensor" },
    #"": { CONFIG_DEVICE_CLASS: "", CONFIG_NAME: "", CONFIG_SENSOR_TYPE: "binary_sensor" },
}
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code {}\n".format(rc))
# Initiate MQTT Client
mqttc = mqtt.Client()
mqttc.username_pw_set(USERNAME, PASSWORD)
mqttc.on_connect = on_connect
mqttc.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)

print('Configuring topics...')
#Configure HASS MQTT topics
for k in KNOWN_KEYS:
    configTopic = getConfigTopic(k)
    configInfo = getConfigInfo(k)
    mqttc.publish(configTopic, configInfo, retain=True)
    print('{}, {}'.format(configTopic, configInfo))
loops = 0
parser = http.HttpConection(config['HAASPELLETSTOVE']['IP'])

#### RUN ####
while True:
    if(config['UART']['PORT'] != ''):
        print('Fetching stove info...')
        haasJson = uart.getHaasPelletStoveInfo(config['UART']['PORT'])
        haasInfo = json.loads(haasJson)
    
        for k in haasInfo:
            if not k in KNOWN_KEYS: continue
            stateTopic = getStateTopic(k)
            mqttc.publish(stateTopic, haasInfo[k])
            print('{}, {}'.format(stateTopic, haasInfo[k]))
        
    if(config['HAASPELLETSTOVE']['IP'] != ''):
        parser.pollDeviceStatus()
        if parser.disableAdapter == False:
            stateTopic = getStateTopic('mode')
            mqttc.publish(stateTopic, parser.mode)
            print('{}, {}'.format(stateTopic, parser.mode))

    mqttc.loop()
    time.sleep(SECONDS_BETWEEN_REFRESH)
    loops += 1
