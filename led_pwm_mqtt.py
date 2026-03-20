import network
import time
import json
from machine import Pin,PWM
from umqtt.simple import MQTTClient

# ---------------- CONFIG ----------------
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASS = ""

MQTT_BROKER = "broker.hivemq.com"
CLIENT_ID = "esp32_brightness"

# Topic
TOPIC_BRIGHTNESS = b"factory/device1/led1/brightness"

# ---------------- LED PWM ----------------
led = PWM(Pin(2))   # GPIO 2
led.freq(1000)      # 1kHz PWM

# ---------------- WIFI ----------------
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASS)

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
        value = data.get("value", 0)

        # Clamp value (0–255)
        if value < 0: value = 0
        if value > 255: value = 255

        # Convert to PWM (0–1023)
        duty = int((value / 255) * 1023)
        led.duty(duty)

        print("Brightness set to:", value)

    except Exception as e:
        print("Error:", e)

# ---------------- MQTT CONNECT ----------------
def connect_mqtt():
    global client

    client = MQTTClient(CLIENT_ID, MQTT_BROKER)
    client.set_callback(on_message)
    client.connect()
    client.subscribe(TOPIC_BRIGHTNESS)

    print("MQTT Connected")

# ---------------- MAIN ----------------
connect_wifi()
connect_mqtt()

while True:
    try:
        client.check_msg()
        time.sleep(0.1)

    except Exception as e:
        print("Reconnecting...", e)
        time.sleep(2)
        connect_wifi()
        connect_mqtt()