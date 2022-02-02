#!/usr/bin/env python3


import asyncio

async def acquire_cores(number_cores):
    reader, writer = await asyncio.open_connection(
        '127.0.0.1', 8888)

    message = str(number_cores) + ",A"

    writer.write(message.encode())
    await writer.drain()

    data = await reader.read(100)
    print(f'Received: {data.decode()!r}')

    print('Close the connection')
    writer.close()
    await writer.wait_closed()

asyncio.run(acquire_cores(3))
