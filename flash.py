import os

DEST = "D:\\"


def copy_from(basedir, lib, subpath):
    src = os.path.join(basedir, lib, subpath)
    dest = os.path.abspath(os.path.join(DEST, subpath))
    if not os.path.exists(os.path.dirname(dest)):
        os.makedirs(os.path.dirname(dest))
    # Use with-structure to ensure flushing
    with open(src, "rb") as fhandle:
        with open(dest, "wb") as destfile:
            destfile.write(fhandle.read())
    print(f"Copied {lib} / {subpath} ({src} -> {dest}")


def copy_from_micropython_lib(lib, subpath):
    copy_from("micropython-lib", lib, subpath)


def copy_from_tobbad(lib, subpath):
    copy_from("tobbad", lib, subpath)


def copy_from_baserepo(lib, subpath):
    copy_from(".", lib, subpath)


def copy_from_picoweb(subpath):
    copy_from(".", "picoweb", "picoweb/" + subpath)


copy_from_micropython_lib("collections", "collections/__init__.py")
copy_from_micropython_lib("collections.deque", "collections/deque.py")

copy_from_micropython_lib("uasyncio", "uasyncio/__init__.py")
copy_from_micropython_lib("uasyncio.core", "uasyncio/core.py")
copy_from_micropython_lib("uasyncio.queues", "uasyncio/queues.py")
copy_from_micropython_lib("uasyncio.websocket.server", "uasyncio/websocket/server.py")
open(os.path.join(DEST, "uasyncio/websocket/__init__.py"), 'a').close()

copy_from_micropython_lib("pkg_resources", "pkg_resources.py")

copy_from_tobbad("lib", "i2cspi.py")
copy_from_tobbad("lib", "multibyte.py")
copy_from_tobbad("boards/pybd", "led36.py")
copy_from_tobbad("sensor", "lsm9ds1.py")
copy_from_tobbad("sensor", "lsm9ds1_const.py")

copy_from_picoweb("__init__.py")
copy_from_picoweb("utils.py")

copy_from_baserepo("root", "boot.py")
copy_from_baserepo("root", "main.py")
copy_from_baserepo("", "www/index.html")
