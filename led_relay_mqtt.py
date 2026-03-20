import network
import time
import json
from machine import Pin
from umqtt.simple import MQTTClient

# ---------------- CONFIG ----------------
SSID = 'Wokwi-GUEST'
PASS = ''

MQTT_BROKER = "broker.hivemq.com"
CLIENT_ID = "esp32_device1"

TOPIC_SUB = b"factory/device1/relay1/set"
TOPIC_PUB = b"factory/device1/digital1/status"

# LED pin
led = Pin(2, Pin.OUT)

# ---------------- WIFI ----------------
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASS)

    print("Connecting to WiFi...")
    while not wlan.isconnected():
        time.sleep(0.5)
        print(".", end="")

    print("\nConnected:", wlan.ifconfig())

# ---------------- MQTT CALLBACK ----------------
def on_message(topic, msg):
    print("Received:", msg)

    try:
        data = json.loads(msg)

        state = data.get("state")

        if state == "on":
            led.value(1)
            client.publish(TOPIC_PUB, b"on")

        elif state == "off":
            led.value(0)
            client.publish(TOPIC_PUB, b"off")

    except Exception as e:
        print("Error:", e)

# ---------------- MQTT CONNECT ----------------
def connect_mqtt():
    global client
    client = MQTTClient(CLIENT_ID, MQTT_BROKER)
    client.set_callback(on_message)
    client.connect()
    client.subscribe(TOPIC_SUB)

    print("Connected to MQTT")

# ---------------- MAIN ----------------
connect_wifi()
connect_mqtt()

while True:
    try:
        client.check_msg()
        time.sleep(0.1)

    except Exception as e:
        print("MQTT Error:", e)
        time.sleep(2)
        connect_mqtt()