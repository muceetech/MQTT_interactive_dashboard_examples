import network
import time
import json
from machine import Pin, time_pulse_us
from umqtt.simple import MQTTClient

# Wi-Fi and MQTT config
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASS = ""

MQTT_BROKER = "broker.hivemq.com"
CLIENT_ID = "esp32_ultrasonic"

TOPIC_SENSOR = b"factory/device1/sensor1"

# ---------------- PINS ----------------
TRIG = Pin(5, Pin.OUT)
ECHO = Pin(18, Pin.IN)

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

# ---------------- MQTT ----------------
def connect_mqtt():
    global client

    client = MQTTClient(CLIENT_ID, MQTT_BROKER)
    client.connect()

    print("MQTT Connected")

# ---------------- DISTANCE FUNCTION ----------------
def get_distance():
    # Send trigger pulse
    TRIG.value(0)
    time.sleep_us(2)
    TRIG.value(1)
    time.sleep_us(10)
    TRIG.value(0)

    # Measure echo time
    try:
        duration = time_pulse_us(ECHO, 1, 30000)  # timeout 30ms
    except:
        return None

    # Convert to distance (cm)
    distance = (duration * 0.0343) / 2
    return round(distance, 2)

# ---------------- MAIN ----------------
connect_wifi()
connect_mqtt()

while True:
    try:
        dist = get_distance()

        if dist is not None:
            print("Distance:", dist, "cm")

            payload = json.dumps({
                "name": "Ultrasonic Distance sensor",
                "value": dist,
                "unit": "cm"
            })

            client.publish(TOPIC_SENSOR, payload)

        time.sleep(1)

    except Exception as e:
        print("Error:", e)
        time.sleep(2)
        connect_wifi()
        connect_mqtt()