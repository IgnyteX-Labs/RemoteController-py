"""
Wired Connection to a device using two wires for two-way communication.
It uses a Half-Duplex communication method. This means that the connection can only send or receive data at a time.
One wire is used for sending data and the other for receiving data. (both wires are "one way lanes")
We send data at a predetermined interval and receive data as soon as it is available.
"""
from typing import Union, Callable

from ..base_connection import Connection, ConnectionDataFetchException, PacketSizeTooBigException


class WiredConnection(Connection):

    def __init__(self, interval: float, on_command_payload: Callable[[int, float], None],
                 on_binary_payload: Callable[[bin], None], send_pin: int,
                 recieve_pin: int, ack_payload: bytes):
        super().__init__(interval, on_command_payload, on_binary_payload)

    def _check(self) -> Union[bytes, None]:
        pass

    def _send_data(self, data: bytes) -> bool:
        pass
