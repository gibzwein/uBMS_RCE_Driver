import network
# import credentials
import urequests as requests
import machine
# import utime
import ntptime
import json
import time
import time_utils
import config
import gc
import ssd1306
from machine import Pin, SoftI2C
import uBMS_modbus
import uBMS_WiFi
import uBMS_Web

# LED Config
led_pin = 23
led = machine.Pin(led_pin, machine.Pin.OUT)

# Relays config
r1_pin = 32
r2_pin = 33
r3_pin = 25
r4_pin = 26
relay1 = machine.Pin(r1_pin, machine.Pin.OUT)
relay2 = machine.Pin(r2_pin, machine.Pin.OUT)
relay3 = machine.Pin(r3_pin, machine.Pin.OUT)
relay4 = machine.Pin(r4_pin, machine.Pin.OUT)

# LCD/OLED config
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
oled_width = 128
oled_height = 64

i2c_devices = i2c.scan()
print(i2c_devices)
if len(i2c_devices) != 0:
    oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

# Define the pin for the button
button_pin = 0  # For example, GPIO0 for ESP8266
button = machine.Pin(button_pin, machine.Pin.IN, machine.Pin.PULL_UP)

def button_handler(pin):
    print("Button pressed")
    oled.fill(0)
    oled.text('AP Mode', 0, 0)
    oled.show()
    uBMS_Web.AP_start()

button.irq(trigger=machine.Pin.IRQ_FALLING, handler=button_handler)

# Golbal variables
rce_prices = None
rce_prices_stats = None
lowest_entries = None
last_time = (0,0,0,0,0,0,0,0)
current_price = None

uBMS_WiFi.wifi_connect()

def get_data():
    max_retries = 3
    retry_count = 0
    led.value(1)
    
    while retry_count < max_retries:
        try:
            date_string = time_utils.get_api_date()

            url = f"https://api.raporty.pse.pl/api/rce-pln?$filter=doba eq '{date_string}'&$select=rce_pln,udtczas"
            oled.fill(0)
            oled.text('Getting PSE data', 0, 0)
            oled.show()
            print("Requesting URL:", url)
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout = 10)
            if response.status_code == 200:
                print('Data fetched')
                led.value(0)
                gc.collect()
                try:
                    return json.loads(response.text)
                except ValueError:
                    print("Error decoding JSON response")
                    return None
            else:
                print(f"Error while retrieving data. Response code: {response.status_code}")
                oled.fill(0)
                oled.text(f'HTTP: {response.status_code}', 0, 0)
                oled.show()
                retry_count += 1
                if retry_count < max_retries:
                    print(f"Retrying to fetch data in {5 * retry_count} seconds...")
                    time.sleep(5 * retry_count)
                else:
                    print("Exceeded maximum number of data retrieval attempts.")
                    return None
        except Exception as e:
            print(f"An error occurred while retrieving data: {e}")
            retry_count += 1
            if retry_count < max_retries:
                print(f"Retrying to fetch data in {5 * retry_count} seconds...")
                time.sleep(5 * retry_count)
            else:
                print("Exceeded maximum number of data retrieval attempts.")
                return None
    return None

def parse_data(json_data):
    parsed_data = []
    for row in json_data['value']:
        date_str = row['udtczas']
        unix_timestamp_to = time_utils.get_timestamp_from_datestring(row['udtczas'])
        unix_timestamp_from = unix_timestamp_to - 15*60 # Move start 15 minutes before
        
        # Append to list
        parsed_data.append({
            'datetime': date_str,
            'timestamp_from': unix_timestamp_from,
            'timestamp_to': unix_timestamp_to,
            'price': row['rce_pln']
        })
    print('Data parsed')
    print(len(parsed_data))
    gc.collect()
    return parsed_data

def calculate_average(data):
    total = sum(entry['price'] for entry in data)
    min_price = min(entry['price'] for entry in data)
    max_price = max(entry['price'] for entry in data)
    print('Calculated averages')
    gc.collect()
    return {'average': total / len(data), 'min': min_price, 'max': max_price}

def display_data(price_data, price):
    if not isinstance(price_data, dict):
        print("Invalid price_data format")
        return
    print(f"Current price: {price}")
    oled.fill_rect(0, 0, 128, 8, 0)
    oled.text(f"RCEg: {price}", 0, 0)
    oled.show()
    range_price = price_data['max'] - price_data['min']
    low = price_data['min'] + range_price * config.LOWER_THRESHOLD/100
    high = price_data['min'] + range_price * config.UPPER_THRESHOLD/100
    print(range_price, low, high)
    if price < config.MINIMUM_SALE_PRICE:
        print("Price lower than 0")
        oled.text('B', 119, 0)
        oled.show()
        relay1.value(0)
        relay2.value(0)
        relay3.value(0)
        relay4.value(1)
        print("Relay 4 ON")
    elif price < low:
        print("Green")
        oled.text('G', 119, 0)
        oled.show()
        relay1.value(1)
        relay2.value(0)
        relay3.value(0)
        relay4.value(0)
        print("Relay 1 ON")
    elif price < high:
        print("Yellow")
        oled.text('Y', 119, 0)
        oled.show()
        relay1.value(0)
        relay2.value(1)
        relay3.value(0)
        relay4.value(0)
        print("Relay 2 ON")
    else:
        print("Red")
        oled.text('R', 119, 0)
        oled.show()
        relay1.value(0)
        relay2.value(0)
        relay3.value(1)
        relay4.value(0)
        print("Relay 3 ON")
    # np.write()
    gc.collect()

def get_rce_prices():
    global rce_prices
    global rce_prices_stats
    global lowest_entries
    rce_prices = None
    rce_prices_stats = None
    lowest_entries = None
    data = get_data()
    rce_prices = parse_data(data)
    rce_prices_stats = calculate_average(rce_prices)
    lowest_entries = get_lowest_entries(rce_prices)
    print(len(rce_prices), len(rce_prices_stats), len(lowest_entries))

def get_current_price(now_timestamp):
    if rce_prices is None:
        return None

    if not isinstance(rce_prices, list):
        print("Error: rce_prices is not a list.")
        return None

    for row in rce_prices:
        if not isinstance(row, dict):
            print("Error: row is not a dictionary.")
            return None

        if now_timestamp >= row['timestamp_from'] and now_timestamp < row['timestamp_to']:
            print(row['price'], now_timestamp, row)
            led.value(not led.value())
            return row['price']

    gc.collect()
    return None


def get_lowest_entries(parsed_data):
    # Sort the data by price in ascending order and get the first NUM entries
    sorted_data = sorted(parsed_data, key=lambda x: x['price'])
    lowest_entries = sorted_data[:config.NUM_ENTRIES]
    return lowest_entries

def is_time_in_range(start_timestamp, end_timestamp):
    now_timestamp = time_utils.get_current_time()
    return start_timestamp <= now_timestamp <= end_timestamp

def check_and_send_modbus_command():
    if lowest_entries:
        for entry in lowest_entries:
            if is_time_in_range(entry['timestamp_from'], entry['timestamp_to']):
                uBMS_modbus.send_modbus_command_charge()
            else:
                uBMS_modbus.send_modbus_command_discharge()
                break

while True:
    if not uBMS_WiFi.sta.isconnected():
        uBMS_WiFi.wifi_connect()

    if rce_prices == None:
        rce_prices = get_rce_prices()

    now = time_utils.get_current_time()
    now_time = time.localtime(now)

    if last_time is None or last_time[4] != now_time[4]:
        print('Day changed, fetching new data')
        get_rce_prices()

        last_time = now_time

    current_price = get_current_price(now)
    if current_price is not None and rce_prices is not None:
        averages = calculate_average(rce_prices)
        display_data(averages, current_price)

    check_and_send_modbus_command()
 
    print(last_time)
    print(now_time)
    print(len(rce_prices))

    gc.collect()
    print("Free memory: ", gc.mem_free())
    time.sleep(1)