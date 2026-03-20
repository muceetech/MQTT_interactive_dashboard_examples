import network
import time
import json
from machine import Pin, PWM
from umqtt.simple import MQTTClient

# ---------------- CONFIG ----------------
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASS = ""

MQTT_BROKER = "broker.hivemq.com"
CLIENT_ID = "esp32_rgb"

TOPIC_RGB = b"factory/device1/rgb1/set"

# ---------------- RGB SETUP ----------------
# Change pins if needed
red   = PWM(Pin(21))
green = PWM(Pin(22))
blue  = PWM(Pin(23))

for led in (red, green, blue):
    led.freq(1000)   # 1kHz PWM

# ---------------- HELPER ----------------
def set_rgb(r, g, b):
    # Clamp values
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))

    # Convert 0–255 → 0–1023
    red.duty(int(r * 4))
    green.duty(int(g * 4))
    blue.duty(int(b * 4))

# ---------------- WIFI ----------------
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASS)

    print("Connecting WiFi...")
    while not wlan.isconnected():
        time.sleep(0.5)
        print(".", end="")

    print("\nConnected:", wlan.ifconfig())

# ---------------- MQTT CALLBACK ----------------
def on_message(topic, msg):
    print("Received:", msg)

    try:
        data = json.loads(msg)

        r = data.get("r", 0)
        g = data.get("g", 0)
        b = data.get("b", 0)

        set_rgb(r, g, b)

        print("RGB:", r, g, b)

    except Exception as e:
        print("Error:", e)

# ---------------- MQTT ----------------
def connect_mqtt():
    global client

    client = MQTTClient(CLIENT_ID, MQTT_BROKER)
    client.set_callback(on_message)
    client.connect()
    client.subscribe(TOPIC_RGB)

    print("MQTT Connected")

# ---------------- MAIN ----------------
connect_wifi()
connect_mqtt()

while True:
    try:
        client.check_msg()
        time.sleep(0.1)

    except Exception as e:
        print("Reconnect...", e)
        time.sleep(2)
        connect_wifi()
        connect_mqtt()