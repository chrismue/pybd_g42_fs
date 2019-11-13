import pyb
import network

import led36
from lsm9ds1 import LSM9DS1

import uasyncio
from uasyncio.websocket.server import WSReader, WSWriter
from uasyncio.queues import Queue

import picoweb

import os

measurement_queue = Queue()


if pyb.SDCard().present():
    os.mount(pyb.SDCard(), '/sd')
    print("Mounted SD Card")
else:
    print("No SD Card present!")


def init_led_tile():
    led36.brightness(100)
    led36.illu(0, 0, 0)


def init_inertia_module():
    i2c_y = pyb.I2C(2, pyb.I2C.MASTER, baudrate=100000)
    lsm9d1 = LSM9DS1(i2c_y, dev_acc_sel=0x6A, dev_gyr_sel=0x6A, dev_mag_sel=0x1C)
    return lsm9d1


@uasyncio.coroutine
def measure(inertia_module):
    while 1:
        acc = inertia_module.accel.xyz()
        r = min(int(acc[1] * 512), 255) if acc[1] > 0 else 0  # scale to 0 .. 255
        g = min(int(-acc[1] * 512), 255) if acc[1] < 0 else 0
        led36.illu(r, g, 0)  # set color on LED tile
        x = min(max(acc[0] * 180, -90), 90)  # scale to -90.0 .. +90.0 degrees
        y = min(max(acc[1] * 180, -90), 90)
        z = min(max(acc[2] * 180, -90), 90)
        if measurement_queue.empty():
            yield from measurement_queue.put((r,g,x,y,z))
        yield


class AccessPoint(network.WLAN):
    SSID = "Guild42Mp"

    def __init__(self):
        super().__init__(1)
        self.config(essid=self.SSID)  # set AP SSID
        self.config(channel=4)  # set AP channel
        self.active(1)  # enable the AP
        print("Started Access point: %s" % self.SSID)


@uasyncio.coroutine
def serve_websocket(reader, writer):
    # Consume GET line
    yield from reader.readline()

    reader = yield from WSReader(reader, writer)
    writer = WSWriter(reader, writer)

    try:
        while 1:
            if not measurement_queue.empty():
                # print("NotEmpty")
                r,g,x,y,z = yield from measurement_queue.get()
                await writer.awrite("%d,%d;%f,%f,%f" % (r,g,x,y,z))
            yield
    except Exception as e:
        print("Exception in websocket: " + str(e))


ROUTES = [
    # basic sample html at root
    ("/", lambda req, resp: (yield from app.sendfile(resp, "./www/index.html"))),
]


if __name__ == "__main__":
    init_led_tile()
    inertia_module = init_inertia_module()
    ap = AccessPoint()

    app = picoweb.WebApp(__name__, ROUTES)
    app.debug = -1  # disable all logging

    loop = uasyncio.get_event_loop()
    loop.call_soon(uasyncio.start_server(serve_websocket, "192.168.4.1", 500))
    loop.create_task(measure(inertia_module))
    app.serve(loop, "192.168.4.1", 80)

    # never reaches here: picoweb call run_forever of uasyncio loop
