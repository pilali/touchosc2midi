#!/usr/bin/env python
"""
Announce touchSCO-MIDI bridge via zeroconf.
"""
import socket
from time import sleep
from zeroconf import Zeroconf, ServiceInfo
import logging
log = logging.getLogger(__name__)

TOUCHOSC_BRIDGE = '_touchoscbridge._udp.local.'
PORT = 12101


def default_route_interface():
    """
    Determine the IPv4 address of the interface used for the default route.

    Opens a UDP socket "connected" to a public address (no packets are
    actually sent) and reads back the local address the OS would use to
    reach it. This avoids depending on the unmaintained `netifaces`.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        log.debug("found '{}' as default route.".format(ip))
        return ip
    except OSError:
        raise RuntimeError("default interface not found. Check your network or use --ip switch.")
    finally:
        s.close()


def build_service_info(ip):
    """Create a zeroconf ServiceInfo for touchoscbridge
    on for `ip` or the guessed default route interface's IP.
    """
    return ServiceInfo(type_=TOUCHOSC_BRIDGE,
                       name="{}.{}".format(
                           socket.gethostname(),
                           TOUCHOSC_BRIDGE
                       ),
                       addresses=[socket.inet_aton(ip)],
                       port=PORT,
                       properties=dict(),
                       server=socket.gethostname() + '.local.')


class Advertisement(object):
    def __init__(self, ip=None):
        """
        :ip: if string `ip` given, register on given IP
             (if None: default route's IP).
        """
        self.zeroconf = Zeroconf()
        self.info = build_service_info(ip=ip or default_route_interface())

    def register(self):
        """Registers the service on the network.
        """
        self.zeroconf.register_service(self.info)
        log.debug("Registered {} on {}:{}".format(
            self.info.name,
            self.ip,
            self.info.port
        ))

    def unregister(self):
        """Unregisters the service.
        """
        self.zeroconf.unregister_service(self.info)
        log.debug("Unregistered touchoscbridge.")

    def update(self, ip=None):
        """Re-register the the service on the network.

        :ip: if string `ip` is given, use given IP when registering.
        """
        self.unregister()
        self.info = build_service_info(ip=ip or default_route_interface())
        self.register()

    def close(self):
        """Free resources.
        Advertisement.unregister() should be called before closing.
        """
        self.zeroconf.close()

    def get_ip(self):
        """:return: the service's IP as a string.
        """
        return socket.inet_ntoa(self.info.addresses[0])

    ip = property(get_ip)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    service = Advertisement()
    try:
        service.register()
        while True:
            sleep(0.1)
    except KeyboardInterrupt:
        service.unregister()
        service.close()
