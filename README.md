1. Led_relay_mqtt.py --> for relay widget
  MQTT_BROKER = "broker.hivemq.com"  (dont change this in program)  
  CLIENT_ID = "esp32_device1"         (optional)  

       change the topic "factory/device1" only.  other values shouldnot be changed which will affect the widget values
       # Topics
       TOPIC_RELAY_SET = b"factory/device1/relay1/set"   -->  get relay widget button value "ON/OFF"
       TOPIC_RELAY_STATUS = b"factory/device1/relay1/status"  --> get relay widget status
       TOPIC_DIGITAL_STATUS = b"factory/device1/di1/status"   --> set digital widget status "0/1" 0 - RED / 1 - GREEN
