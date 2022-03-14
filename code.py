# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import board
import busio
import digitalio
from digitalio import DigitalInOut
import adafruit_debouncer
from adafruit_wiznet5k.adafruit_wiznet5k import WIZNET5K
import adafruit_wiznet5k.adafruit_wiznet5k_socket as socket
import adafruit_requests as requests
import json
import neopixel
from config import *



def main():
    # Status LED
    led = neopixel.NeoPixel(board.NEOPIXEL, 1)
    led.brightness = 0.3
    led[0] = BLUE

    button_pin = DigitalInOut(board.D9)
    button_pin.switch_to_input(digitalio.Pull.UP)
    button = adafruit_debouncer.Debouncer(button_pin)

    # PoE-FeatherWing connections
    cs = DigitalInOut(board.D10)
    spi_bus = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
    i2c = busio.I2C(board.SCL, board.SDA)

    # Read the MAC from the 24AA02E48 chip
    mac = get_mac(i2c)

    # Initialize ethernet interface with DHCP and the MAC we have from the 24AA02E48
    eth = WIZNET5K(spi_bus, cs, mac=mac, hostname="PoE-FeatherWing-{}")

    # Initialize a requests object with a socket and ethernet interface
    requests.set_socket(socket, eth)

    print("Chip:", eth.chip)
    print("".join([f"{i:x}" for i in eth.mac_address]))
    print(eth.pretty_ip(eth.ip_address))

    led[0] = GREEN

    send_success = None
    while True:
        button.update()

        if button.fell:
            led[0] = GREEN
            send_success = send_button_state("on")
        elif button.rose:
            led[0] = RED
            send_success = send_button_state("off")

        if button.fell or button.rose:
            led[0] = OFF if send_success else WHITE



def send_button_state(state):
    try:
        r = requests.post(
            f"http://{home_assistant_ip}:8123/api/states/{sensor_name}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            data=json.dumps(
                {
                    "state": state,
                    "attributes": {
                        "friendly_name": sensor_friendly_name,
                    },
                }
            ),
        )
        r.close()
        return True
    except Exception as e:
        print(f"Post failed: {repr(e)}")
        return False


def get_mac(i2c):
    "Read MAC from 24AA02E48 chip and return it"
    mac = bytearray(6)
    while not i2c.try_lock():
        pass
    i2c.writeto(0x50, bytearray((0xFA,)))
    i2c.readfrom_into(0x50, mac, start=0, end=6)
    i2c.unlock()
    return mac


RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
OFF = (0, 0, 0)

main()
