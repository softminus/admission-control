#!/usr/bin/env python3

import asyncio

class CoreCounter:
    def __init__(self, total_cores):
        self.total_cores = total_cores
        self.current_cores = 0


    async def handle_echo(self, reader, writer):
        total_requested_by_this_endpoint = 0

        while True:

            data = await reader.read(128)
            message = data.decode()

            if(message == ''):
                self.current_cores = self.current_cores - total_requested_by_this_endpoint
                print (addr, ": connection lost to; relinquishing", total_requested_by_this_endpoint, "cores back to the scheduler")
                return


            addr = writer.get_extra_info('peername')[1]
            #print(f"Received {message!r} from {addr!r}")
            message=message[:-1]

            parsed = message.split(",")
            #print(parsed)
            try:
                numcores = int(parsed[0])
            except ValueError:
                print("value error parsing\"" + data.decode() + "\"")
                continue

            message_type = parsed[1]

            if (message_type == "R"): # relinquish some cores
                if (numcores > total_requested_by_this_endpoint):
                    numcores = total_requested_by_this_endpoint
                self.current_cores = self.current_cores - numcores
                total_requested_by_this_endpoint -= numcores
                print(addr, "releases", numcores, "cores; now", self.current_cores, "are in use")


            if (message_type == "A"): # acquire some cores
                while (numcores + self.current_cores > self.total_cores):
                    print(addr, "requests", numcores, "but only", self.total_cores - self.current_cores, "are available")
                    try:
                        data = await asyncio.wait_for(reader.read(128),timeout=1)
                        message = data.decode()

                        if(message == ''):
                            self.current_cores = self.current_cores - total_requested_by_this_endpoint
                            print (addr, ": connection lost to; relinquishing", total_requested_by_this_endpoint, "cores back to the scheduler")
                            return
                    except (asyncio.exceptions.CancelledError, asyncio.exceptions.TimeoutError):
                        print (addr, "timed out normally, still holding")
                        pass

                self.current_cores = self.current_cores + numcores
                total_requested_by_this_endpoint += numcores
                print(addr, "granted", numcores, "core[s]; now", self.current_cores, "cores are in use")
                writer.write(str(str(numcores) + ",G\n").encode())

            await writer.drain()

#    print("Close the connection")
#    writer.close()



async def main():
    ctx = CoreCounter(total_cores=16)
    server = await asyncio.start_server(ctx.handle_echo, '127.0.0.1', 8888)

    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    #print(f'Serving on {addrs}')

    async with server:
        await server.serve_forever()

asyncio.run(main())