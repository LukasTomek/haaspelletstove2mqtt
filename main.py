#!/usr/bin/python3
import configparser
import HaasPelletStove2MQTT as haas


def main():
    
    # Read Configuration from config.ini    
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    mqtt =haas.MqttClient()

    parser = HttpConection(config['MQTT_BROKER']['MQTT_BROKER'], config['MQTT_BROKER']['MQTT_PORT'], config['MQTT_BROKER']['MQTT_KEEPALIVE_INTERVAL']) 
    
    
    parser.pollDeviceStatus()
    print('Done!\n')
if __name__ == '__main__':
    main()
    