from uModBus.serial import Serial
from uModBus.tcp import TCP
from network import WLAN
import machine
import utime
import config

uart_id = 0x01
modbus_obj = Serial(uart_id, baudrate=config.BAUDRATE, pins=(16, 17))

slave_addr = config.SLAVE_ADDR
starting_address=0x13A0
register_quantity = 1
register_address = config.REGISTER_ADDR
register_value_d = config.DISCHARGE_REGISTER_VALUE
register_value_c = config.CHARGE_REGISTER_VALUE
signed = False

def send_modbus_command_charge():
    try:
        return_flag = modbus_obj.write_single_register(slave_addr, register_address, register_value_c, signed)
        output_flag = 'CHARGE' if return_flag else 'Failure'
        print('Changing mode to: ' + output_flag)
    except OSError as e:
        print(f'Error during register write: {e}. No data received from slave.')
    except Exception as e:
        print(f'Unexpected error during register write: {e}')

def send_modbus_command_discharge():
    try:
        return_flag = modbus_obj.write_single_register(slave_addr, register_address, register_value_d, signed)
        output_flag = 'DISCHARGE' if return_flag else 'Failure'
        print('Changing mode to: ' + output_flag)
    except OSError as e:
        print(f'Error during register write: {e}. No data received from slave.')
    except Exception as e:
        print(f'Unexpected error during register write: {e}')