#!/usr/bin/env python3


import asyncio


async def NewScheduler():
    scheduler_client = SchedulerClient()
    await scheduler_client.connect()
    return scheduler_client

class SchedulerClient:
    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(
          '127.0.0.1', 8888)


    async def acquire_cores(self, number_cores):
        reader = self.reader
        writer = self.writer 

        message = str(number_cores) + ",A"

        writer.write(message.encode())
        await writer.drain()

        data = await reader.read(100)
        print(f'Received: {data.decode()!r}')

        print('Close the connection')
        writer.close()
        await writer.wait_closed()



    async def relinquish_cores(number_cores):
        reader, writer = await asyncio.open_connection(
            '127.0.0.1', 8888)

        message = str(number_cores) + ",R"

        writer.write(message.encode())
        await writer.drain()

        data = await reader.read(100)
        print(f'Received: {data.decode()!r}')

        print('Close the connection')
        writer.close()
        await writer.wait_closed()



egg = asyncio.run(NewScheduler())

egg.acquire_cores(3)
