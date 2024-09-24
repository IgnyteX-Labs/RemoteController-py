# RemoteController
Library to enable easy communication of basic commands or binary payloads. Intended for embedded systems. <br>
Written in python <br>

It is supposed to be very light and easy to understand. It is not intended for high performance applications.

## Implemented Connection types
- _(in development) A Half-Duplex wired connection using the RPi.GPIO library._
- _(in development) A RF24 connection using the RF24 library._
- _(planned) A websocket based connection_
- _**(soon) Your own connection type. Find out more below.**_

## Quick start
Here is how an example setup would look like in python. RemoteController uses asyncio.
```python
# Initialize a connection
import asyncio
from RemoteController.connections import WiredConnection


def handle_command(command: int, throttle: float):
    print(f"Recieved command: {command} with throttle: {throttle}")


def handle_binary_data(data: bytes):
    print(f"Recieved binary data: {data}")


async def main():
    connection = WiredConnection(
        0.001,  # Time to wait between checking for new data
        handle_command,  # Function to call when a command is recieved
        handle_binary_data,  # Function to call when binary data is recieved
        12,  # Pin that I will send data on
        16,  # Pin that I will recieve data on
        b'\x01\x02\x03\x04'  # Acknowledgement payload (example)
    )

    # Do something else, the connection will keep itself alive
    for _ in range(10):
        connection.send_command(1, 0.5)
        # Send a command
        await asyncio.sleep(1)
    # When finished
    connection.stop()

main()
# The connection will automatically start listening for data
```

## Lifecycle
1. Create a connection object and define what should happen on recieving connection data.
2. Send commands / data when needed
3. Close the connection when finished

### Implementing your own Connection
Is easy and requires minimal setup from your side.

```python
from RemoteController.base_connection import Connection, PacketSizeTooBigException, ConnectionDataFetchException
from typing import Union

class CustomConnection(Connection):
    def _send_data(self, data: bytes) -> bool:
        # Implement your own way of sending data here
        # Raise PacketSizeTooBigException if the packet is too big or split the packet into smaller packets
        pass

    def _check(self) -> Union[bytes, None]:
        # Implement your own way of checking for new data here
        # Return the data as a bytes object or None if no data is available
        # Raise ConnectionDataFetchException if an error occured
        pass
```

#### Protocol version
Currently Protocol version 1.0 is implemented.
