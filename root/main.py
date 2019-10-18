import pyb
import time

import network

from led36 import led36
from lsm9ds1 import LSM9DS1

import micropython
import uasyncio
from uasyncio.websocket.server import WSReader, WSWriter
from uasyncio.queues import Queue

import os

import ure as re

q = Queue()

if pyb.SDCard().present():
    os.mount(pyb.SDCard(), '/sd')
    print("Mounted SD Card:")
    print(os.listdir("/sd/"))
    print(os.listdir("/sd/web"))


class LedTile:
    def __init__(self):
        self._tile = led36()
        self._tile.brightness(100)
        self._tile.illu(0, 0, 0)

    def set_color(self, r, g, b):
        self._tile.illu(r, g, b)


class ThreadedMeasuring:
    def __init__(self, led_tile):
        # Initialize internal variables
        self._r = 0
        self._g = 0
        self._led_tile = led_tile

        # Initialize Inertial Module
        i2c_y = pyb.I2C(2, pyb.I2C.MASTER, baudrate=100000)
        self._lsm9d1 = LSM9DS1(i2c_y, dev_acc_sel=0x6A, dev_gyr_sel=0x6A, dev_mag_sel=0x1C)


@uasyncio.coroutine
def measure(meas):
    while 1:
        # print("Measuring...")
        acc = meas._lsm9d1.accel.xyz()
        r = min(int(acc[1] * 512), 255) if acc[1] > 0 else 0
        g = min(int(-acc[1] * 512), 255) if acc[1] < 0 else 0
        meas._led_tile.set_color(r, g, 0)
        x = min(max(acc[0] * 180, -90), 90)
        y = min(max(acc[1] * 180, -90), 90)
        z = min(max(acc[2] * 180, -90), 90)
        # print("Measured.")
        if q.empty():
            yield from q.put((r,g,x,y,z))
            # print("Put In Queue")
        yield



class AccessPoint(network.WLAN):
    SSID = "Guild42Mp"

    def __init__(self):
        super().__init__(1)
        self.config(essid=self.SSID)  # set AP SSID
        self.config(channel=4)  # set AP channel
        self.active(1)  # enable the AP
        print("Started Access point: %s" % self.SSID)

"""
def echo(reader, writer):
    # Consume GET line
    yield from reader.readline()

    reader = yield from WSReader(reader, writer)
    writer = WSWriter(reader, writer)

    while 1:
        l = yield from reader.read(256)
        print(l)
        if l == b"\r":
            await writer.awrite(b"\r\n")
        else:
            await writer.awrite(l)
"""

@uasyncio.coroutine
def serve(reader, writer):
    print(reader, writer)
    print("================")
    print((yield from reader.read()))
    with open('www/index.html', 'r') as f:
        yield from writer.awrite("HTTP/1.0 200 OK\r\n\r\n" + f.read())
    print("After response write")
    yield from writer.aclose()
    print("Finished processing request")


@uasyncio.coroutine
def serve_websocket(reader, writer):
    # Consume GET line
    yield from reader.readline()

    reader = yield from WSReader(reader, writer)
    writer = WSWriter(reader, writer)

    try:
        while 1:
            if not q.empty():
                # print("NotEmpty")
                r,g,x,y,z = yield from q.get()
                await writer.awrite("%d,%d;%f,%f,%f" % (r,g,x,y,z))
            yield
    except Exception as e:
        print("Exception in websocket: " + str(e))

#
# This is a picoweb example showing a centralized web page route
# specification (classical Django style).
#
# import ure as re
import picoweb


def index(req, resp):
    # You can construct an HTTP response completely yourself, having
    # a full control of headers sent...
    yield from resp.awrite("HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n")
    yield from resp.awrite('<html><meta http-equiv="refresh", content="0;URL=/static/index.html" /></html>')


ROUTES = [
    # You can specify exact URI string matches...
    ("/", lambda req, resp: (yield from app.sendfile(resp, "static/index.html"))),
]


if __name__ == "__main__":
    tile = LedTile()
    meas = ThreadedMeasuring(tile)
    ap = AccessPoint()

    app = picoweb.WebApp(__name__, ROUTES)
    # debug values:
    # -1 disable all logging
    # 0 (False) normal logging: requests and errors
    # 1 (True) debug logging
    # 2 extra debug logging
    app.debug = -1

    # print("My loop :-)")
    loop = uasyncio.get_event_loop()
    # loop.call_soon(uasyncio.start_server(serve, "192.168.4.1", 80))

    loop.call_soon(uasyncio.start_server(serve_websocket, "192.168.4.1", 500))
    loop.create_task(measure(meas))
    app.serve(loop, "192.168.4.1", 80)
    loop.run_forever()
    loop.close()

    """

    serve(self, loop, host, port):
    # Actually serve client connections. Subclasses may override this
    # to e.g. catch and handle exceptions when dealing with server socket
    # (which are otherwise unhandled and will terminate a Picoweb app).
    # Note: name and signature of this method may change.
    loop.create_task(asyncio.start_server(self._handle, host, port))
    loop.run_forever()


def run(self, host="127.0.0.1", port=8081, debug=False, lazy_init=False, log=None):
    if log is None and debug >= 0:
        import ulogging
        log = ulogging.getLogger("picoweb")
        if debug > 0:
            log.setLevel(ulogging.DEBUG)
    self.log = log
    gc.collect()
    self.debug = int(debug)
    self.init()
    if not lazy_init:
        for app in self.mounts:
            app.init()
    loop = asyncio.get_event_loop()
    if debug > 0:
        print("* Running on http://%s:%s/" % (host, port))
    self.serve(loop, host, port)
    loop.close()



    app.run(host="192.168.4.1", port=80, debug=-1)

"""