import network
import time
from machine import ADC, Pin
from umqtt.simple import MQTTClient

# ---------------- CONFIG ----------------
WIFI_SSID = "Wokwi-GUEST"
WIFI_PASS = ""

MQTT_BROKER = "broker.hivemq.com"
CLIENT_ID = "esp32_voltmeter"

TOPIC_VOLT = b"factory/device1/voltage1"

# ---------------- ADC SETUP ----------------
adc = ADC(Pin(34))          # GPIO 34 (input only)
adc.atten(ADC.ATTN_11DB)    # Full range ~0–3.3V

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

# ---------------- MAIN ----------------
connect_wifi()
connect_mqtt()

while True:
    try:
        raw = adc.read()   # 0–4095

        # Convert to voltage (0–3.3V)
        voltage = (raw / 4095) * 3.3

        # Round for display
        voltage_str = str(round(voltage, 2))

        print("Voltage:", voltage_str)

        client.publish(TOPIC_VOLT, voltage_str)

        time.sleep(1)

    except Exception as e:
        print("Error:", e)
        time.sleep(2)
        connect_wifi()
        connect_mqtt()