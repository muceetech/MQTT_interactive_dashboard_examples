import network
import time
import json
from machine import Pin, PWM
from umqtt.simple import MQTTClient

# Wi-Fi credentials
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASS = ""

MQTT_BROKER = "broker.hivemq.com"
CLIENT_ID = "esp32_servo"

TOPIC_SERVO = b"factory/device1/servo1/set"

# ---------------- SERVO SETUP ----------------
servo = PWM(Pin(21))     # GPIO 2 (change if needed)
servo.freq(50)          # Servo uses 50Hz

# Convert angle (0–180) → duty (40–115 approx)
def angle_to_duty(angle):
    angle = max(0, min(180, angle))

    min_duty = 25    # for 0°
    max_duty = 128   # for 180°

    duty = int(min_duty + (angle / 180) * (max_duty - min_duty))
    return duty

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
        angle = data.get("angle", 90)

        duty = angle_to_duty(angle)
        servo.duty(duty)

        print("Servo angle:", angle)

    except Exception as e:
        print("Error:", e)

# ---------------- MQTT CONNECT ----------------
def connect_mqtt():
    global client

    client = MQTTClient(CLIENT_ID, MQTT_BROKER)
    client.set_callback(on_message)
    client.connect()
    client.subscribe(TOPIC_SERVO)

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