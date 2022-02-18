#!/usr/bin/env python3
import os
import logging
import asyncio
import time

async def acquire_cores_lambda(reader, writer, number_cores, rpc):
    message = str(number_cores) + ",A," + rpc
    writer.write(message.encode())
    await writer.drain()
    await reader.read(100)
    writer.close()

async def relinquish_cores_lambda(reader, writer, number_cores):
    message = str(number_cores) + ",R"
    writer.write(message.encode())
    await writer.drain()
    data = await reader.read(1)
    message = data.decode()
    writer.close()


def acquire_cores(number_cores, rpc):
    evloop = asyncio.new_event_loop()
    try:
        reader, writer = evloop.run_until_complete(asyncio.open_connection('127.0.0.1', 8888))
    except Exception as e:
        log.warning("admission control nonfunctional, unable to connect to server: %s", e)
        traceback.print_exc(file=sys.stdout)
        traceback.print_exc(file=sys.stderr)
        quit(1)
    evloop.run_until_complete(acquire_cores_lambda(reader, writer, number_cores, rpc))
    evloop.stop()
    evloop.close()


def relinquish_cores(number_cores):
    evloop = asyncio.new_event_loop()
    try:
        reader, writer = evloop.run_until_complete(asyncio.open_connection('127.0.0.1', 8888))
    except Exception as e:
        log.warning("admission control nonfunctional, unable to connect to server: %s", e)
        traceback.print_exc(file=sys.stdout)
        traceback.print_exc(file=sys.stderr)
        quit(1)
    evloop.run_until_complete(relinquish_cores_lambda(reader, writer, number_cores))
    evloop.stop()
    evloop.close()


acquire_cores(1,"egg")
relinquish_cores(3)