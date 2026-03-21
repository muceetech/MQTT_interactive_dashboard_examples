import network
import time
import json
from machine import Pin, ADC, I2C
from umqtt.simple import MQTTClient
import math
import dht
import bmp180   # BMP180 library required

# ===== MODEL CONSTANTS =====
GAMMA = 0.7
RL10 = 50  # LDR resistance at 10 lux (kΩ)

R_FIXED = 10000  # Your resistor (10k)


# ---------------- WIFI ----------------
SSID = "Wokwi-GUEST"
PASSWORD = ""

MQTT_BROKER = "broker.hivemq.com"
CLIENT_ID = "esp32_sensors"

TOPIC_LCD = b"factory/device1/lcd1/text"

# ---------------- PINS ----------------
# LDR
ldr = ADC(Pin(35))
ldr.atten(ADC.ATTN_11DB)
ldr.width(ADC.WIDTH_12BIT)

# DHT
dht_sensor = dht.DHT22(Pin(2))  # or DHT22

# I2C (BMP180)
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
bmp = bmp180.BMP180(i2c)

# ---------------- ADC to LUX conversion -------------

# ===== LUX FUNCTION =====
def calculate_lux(adc_val):

    # Prevent division errors
    if adc_val <= 0:
        adc_val = 1
    if adc_val >= 4095:
        adc_val = 4094

    # Voltage
    voltage = (adc_val / 4095) * 3.3

    # Resistance (voltage divider)
    ldr_resistance = R_FIXED * voltage / (3.3 - voltage)

    # Lux calculation (Wokwi model)
    lux = ((RL10 * 1000) / ldr_resistance) ** (1 / GAMMA)

    return round(lux, 2)


# ---------------- WIFI ----------------
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

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

# ---------------- READ SENSORS ----------------
def read_sensors():
    # LDR
    adc_val = ldr.read()
    lux = calculate_lux(adc_val)
    lux =lux*10

    # DHT
    try:
        dht_sensor.measure()
        dht_temp = dht_sensor.temperature()
        dht_hum = dht_sensor.humidity()
    except:
        dht_temp = 0
        dht_hum = 0

    # BMP180
    try:
        bmp_temp = round(bmp.temperature, 1)
        pressure = round(bmp.pressure / 100, 1)  # hPa
    except:
        bmp_temp = 0
        pressure = 0

    return lux, dht_temp, dht_hum, bmp_temp, pressure

# ---------------- FORMAT LCD ----------------
def format_lcd(ldr, dht_t, dht_h, bmp_t, pres):

    line1 = "Temp:{}C Hum:{}%".format(dht_t, dht_h)
    line2 = "BMP180 Temp:{}C".format(bmp_t)
    line3 = "Pressure:{}hPa".format(pres)
    line4 = "Light:{}".format(ldr)

    lines = [line1, line2, line3, line4]

    formatted = []

    for l in lines:
        l = str(l)           # ensure string
        l = l[:20]           # trim
        l = l + " " * (20 - len(l))   # manual padding
        formatted.append(l)

    return "\n".join(formatted)

# ---------------- MAIN ----------------
connect_wifi()
connect_mqtt()

while True:
    try:
        lux, dht_t, dht_h, bmp_t, pres = read_sensors()

        lcd_text = format_lcd(lux, dht_t, dht_h, bmp_t, pres)

        print(lcd_text)

        client.publish(TOPIC_LCD, lcd_text)

        time.sleep(2)

    except Exception as e:
        print("Error:", e)
        time.sleep(2)
        connect_wifi()
        connect_mqtt()