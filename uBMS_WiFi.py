import config
import network
import utime
import gc
import machine
import ntptime
from machine import Pin, SoftI2C
import ssd1306

ssid = config.ssid
password = config.password

sta = network.WLAN(network.STA_IF)
ap = network.WLAN(network.AP_IF)
ap.active(False)

led_pin = 2
led = machine.Pin(led_pin, machine.Pin.OUT)

i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

def wifi_connect():
    while True:
        try:
            CONNECT_TIMEOUT = 20
            print("Connecting to WiFi", end="")
            print(ssid, password)
            sta.active(True)
            utime.sleep(1)
            sta.connect(ssid, password)
            oled.fill(0)
            oled.text('Connecting WiFi', 0, 0)
            oled.show()
            while not sta.isconnected() and CONNECT_TIMEOUT > 0:
                print(".", end="")
                led.value(not led.value())
                utime.sleep(0.5)
                CONNECT_TIMEOUT -= 1
            if sta.isconnected():
                print("\nWiFi Connected!")
                oled.fill(0)
                oled.text('WiFi Connected', 0, 0)
                oled.show()
                led.value(1)
                ntptime.timeout = 3     # increase timeout
                ntptime.settime()
                break  # Exit the loop if connected
            else:
                print("\nFailed to connect to WiFi.")
                oled.fill(0)
                oled.text('WiFi Failed', 0, 0)
                oled.show()
                sta.active(False)
                utime.sleep(1)
                gc.collect()
        except OSError as e:
            print(f"\nOSError: {e}")
            oled.fill(0)
            oled.text('WiFi Error', 0, 0)
            oled.show()
            sta.active(False)
            utime.sleep(1)
            gc.collect()
