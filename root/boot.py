# boot.py -- run on boot-up
# can run arbitrary Python, but best to keep it minimal

import pyb
import time
pyb.country('DE')  # ISO 3166-1 Alpha-2 code, eg US, GB, DE, AU

# Enable 3.3V Output for external sensors
pyb.Pin('PULL_SCL', pyb.Pin.OUT, value=1) # enable 5.6kOhm X9/SCL pull-up
pyb.Pin('PULL_SDA', pyb.Pin.OUT, value=1) # enable 5.6kOhm X10/SDA pull-up
pyb.Pin("EN_3V3").on()
time.sleep_ms(20)

pyb.main('main.py')  # main script to run after this one

# pyb.usb_mode('VCP+MSC') # act as a serial and a storage device
# pyb.usb_mode('VCP+HID') # act as a serial device and a mouse
