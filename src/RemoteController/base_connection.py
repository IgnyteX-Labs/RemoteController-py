import asyncio
import struct

from abc import ABC, abstractmethod
from typing import Callable, List, Union


class Connection(ABC):
    _queue: List[bytes]

    def __init__(self, interval: float, on_command_payload: Callable[[int, float], None],
                 on_binary_payload: Callable[[bytes], None]):
        """
        Initialize a new generic connection. This class is meant to be inherited by a specific connection type.
        :param interval: The interval in seconds to poll the connection for new data.
        :param on_command_payload: The action that should be performed when a command payload is received.
        :param on_binary_payload: The action that should be performed when a binary payload is received.
        :raises ConnectionDataFetchException: If the connection could not process data.
        """
        self.interval = interval
        self.on_command_payload = on_command_payload
        self.on_binary_payload = on_binary_payload
        self._task: asyncio.Task = asyncio.create_task(self._run(), name=self.__class__.__name__ + " Connection Task")

    async def _run(self):
        """
        The continuous loop that will check the connection for new data.
        You can override this if you want to add additional functionality.
        :return:
        :raises ConnectionDataFetchException: If the connection could not process data.
        """
        try:
            while True:
                await asyncio.sleep(self.interval)
                # Handle data if the result is None (false) or else work the queue.
                self._handle_data(result) if (result := self._check()) else self._send_data(self._queue.pop(0))
                # We don't want to process data in the same tick as we send data as this could take up too much time
        except asyncio.CancelledError:
            pass
        except Exception as e:
            raise ConnectionDataFetchException(e, self.__class__.__name__ + " connection could not process data")

    def send_command(self, command: int, throttle: float = 0.0, send_immediately: bool = False):
        """
        Send a command to the connection.
        This method won't return anything about the status of the command as this is handled at the next tick.
        :param command: Command to send as unsigned integer (!)
        :param throttle: Throttle value to send with the command
        :param send_immediately: Send the command asap
        :return:
        """
        # Add the command identifier bits as per protocol to the start of the payload
        # Then add the command as an unsigned 8-bit integer bytes
        # Then add the throttle as a 32-bit float bytes
        payload = struct.pack(">H B f", 0xEEAF, command, throttle)
        self._queue.insert(0, payload) if send_immediately else self._queue.append(payload)

    def send_binary_payload(self, binary_payload: bytes, send_immediately: bool = False):
        """
        Send a binary payload to the connection.
        This method won't return anything about the status of the command as this is handled at the next tick.
        :param binary_payload: The binary payload to send.
        :param send_immediately: Send the payload asap
        :return:
        """
        # Add the binary payload identifier bits as per protocol to the start of the payload
        # Then add the payload
        payload = struct.pack(">H", 0xEEAE) + binary_payload
        self._queue.insert(0, payload) if send_immediately else self._queue.append(payload)

    def _handle_data(self, payload: bytes):
        """
        Handle incoming data
        :param payload: Incoming data
        :return:
        """
        # Check if the data is a command or a binary payload
        # If it is a command, unpack the data and call the on_command_payload callback
        # If it is a binary payload, call the on_binary_payload callback
        header, = struct.unpack('>H', payload[:2])
        match header:
            case 0xEEAF:
                _, command, throttle = struct.unpack('>H B f', payload)
                self.on_command_payload(command, throttle)
            case 0xEEAE:
                self.on_binary_payload(payload[2:])

    def stop(self):
        """
        Stop the connection.
        """
        if self._task:
            self._task.cancel()

    @abstractmethod
    def _check(self) -> Union[bytes, None]:
        """
        Check the connection for new data. Return data if there is any or return None if there is no data.
        :return: The data that was received or None
        """

    @abstractmethod
    def _send_data(self, data: bytes) -> bool:
        """
        Send data to the connection. Check if the payload is too big before sending.
        :param data: The data to be sent.
        :return: Weather or not the data was sent.
        :raises PacketSizeTooBigException: If the packet is too big to be sent.
        """


class PacketSizeTooBigException(Exception):
    pass


class ConnectionDataFetchException(Exception):
    pass
