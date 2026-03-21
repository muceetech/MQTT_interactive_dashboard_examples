from machine import Pin
import network
import time
from umqtt.simple import MQTTClient
import ujson

# ---------- WIFI ----------
SSID = "Wokwi-GUEST"
PASSWORD = ""

# ---------- MQTT ----------
BROKER = "broker.hivemq.com"
TOPIC = b"traffic/system"

# ---------- LED SETUP ----------

roads = {
    "road1": {
        "red": Pin(33, Pin.OUT),
        "yellow": Pin(4, Pin.OUT),
        "green": Pin(32, Pin.OUT)
    },
    "road2": {
        "red": Pin(25, Pin.OUT),
        "yellow": Pin(26, Pin.OUT),
        "green": Pin(27, Pin.OUT)
    },
    "road4": {
        "red": Pin(0, Pin.OUT),
        "yellow": Pin(2, Pin.OUT),
        "green": Pin(15, Pin.OUT)
    },
    "road3": {
        "red": Pin(23, Pin.OUT),
        "yellow": Pin(22, Pin.OUT),
        "green": Pin(21, Pin.OUT)
    }
}

# ---------- FUNCTIONS ----------

def set_all_off():
    for road in roads:
        for color in roads[road]:
            roads[road][color].value(0)

def set_light(road, color):
    for c in roads[road]:
        roads[road][c].value(0)
    roads[road][color].value(1)

def update_lights(data):
    for road in roads:
        set_light(road, data[road])

# ---------- WIFI CONNECT ----------

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)

print("Connecting WiFi...")
while not wifi.isconnected():
    time.sleep(0.5)

print("Connected:", wifi.ifconfig())

# ---------- MQTT CALLBACK ----------

def mqtt_callback(topic, msg):
    print("MQTT:", msg)
    try:
        data = ujson.loads(msg)
        update_lights(data)
    except:
        print("Invalid JSON")

# ---------- MQTT SETUP ----------

client = MQTTClient("esp32_traffic", BROKER)
client.set_callback(mqtt_callback)
client.connect()
client.subscribe(TOPIC)

print("MQTT Connected")

# ---------- DEFAULT STATE ----------
update_lights({
    "road1": "red",
    "road2": "red",
    "road3": "red",
    "road4": "red"
})

# ---------- LOOP ----------

while True:
    try:
        client.check_msg()
        time.sleep(0.1)
    except:
        print("Reconnecting MQTT...")
        try:
            client.connect()
            client.subscribe(TOPIC)
        except:
            pass