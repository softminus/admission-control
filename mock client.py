#!/usr/bin/env python3


import asyncio




async def acquire_cores(reader, writer, number_cores):
    message = str(number_cores) + ",A"
    writer.write(message.encode())
    await writer.drain()
    await reader.read(100)





async def relinquish_cores(reader, writer, number_cores):

    message = str(number_cores) + ",R"

    writer.write(message.encode())
    await writer.drain()
    await reader.read(100)



loope = asyncio.new_event_loop()
reader, writer = loope.run_until_complete(asyncio.open_connection('127.0.0.1', 8888))
loope.run_until_complete(acquire_cores(reader, writer, 1))