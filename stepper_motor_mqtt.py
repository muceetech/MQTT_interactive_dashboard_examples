import time
import network
import json
from machine import Pin
from umqtt.simple import MQTTClient

# ---------------- WIFI + MQTT ----------------
SSID = 'Wokwi-GUEST'
PASSWORD = ''
MQTT_BROKER = 'broker.hivemq.com'
MQTT_CLIENT_ID = 'esp32-stepper'

TOPIC_MOTOR = b'factory/device1/motor1/set'

# ---------------- STEPPER DRIVER PINS ----------------
DIR_PIN = Pin(5, Pin.OUT)     # DIR
STEP_PIN = Pin(18, Pin.OUT)   # STEP

# ---------------- STATE ----------------
running = False
direction = "clockwise"
last_direction = None

step_delay_us = 800   # speed control (lower = faster)

# ---------------- WIFI ----------------
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    while not wlan.isconnected():
        time.sleep(0.1)

    print("WiFi Connected")

# ---------------- MQTT CALLBACK ----------------
def mqtt_callback(topic, msg):
    global running, direction

    print("Received:", msg)

    try:
        data = json.loads(msg)

        direction = data.get("direction", "cw")
        running = data.get("running", False)

        print("Direction:", direction, "Running:", running)

    except Exception as e:
        print("Error:", e)

# ---------------- SET DIRECTION ----------------
def set_direction(dir_value):
    global last_direction

    if dir_value != last_direction:

        if dir_value == "clockwise":
            DIR_PIN.value(1)
        else:
            DIR_PIN.value(0)

        # IMPORTANT: allow driver to latch direction
        time.sleep_ms(2)

        last_direction = dir_value

# ---------------- STEP MOTOR ----------------
def step_motor():
    STEP_PIN.value(1)
    time.sleep_us(step_delay_us)
    STEP_PIN.value(0)
    time.sleep_us(step_delay_us)

# ---------------- MAIN ----------------
connect_wifi()

client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
client.set_callback(mqtt_callback)
client.connect()
client.subscribe(TOPIC_MOTOR)

print("MQTT Connected & Subscribed")

while True:
    try:
        client.check_msg()

        if running:
            set_direction(direction)   # update direction safely
            step_motor()              # continuous stepping
        else:
            time.sleep_ms(10)

    except Exception as e:
        print("Error:", e)
        time.sleep(2)

        connect_wifi()
        client.connect()
        client.subscribe(TOPIC_MOTOR)