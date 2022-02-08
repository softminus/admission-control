#!/usr/bin/env python3

import asyncio
import time


# Known defect: if a client is in the "waiting for cores to be released" loop
# it cannot relinquish any cores it has requested. this is OK because our current
# test suite runs the commands in sequential order and so there's nothing to be
# gained from allowing command parsing to happen when we're in the loop.

class CoreCounter:
    def __init__(self, total_cores):
        self.total_cores = total_cores
        self.current_cores = 0


    async def handle_echo(self, reader, writer):
        total_requested_by_this_endpoint = 0
        rpc_type = ""
        start_time = 0
        while True:
            data = await reader.read(128)
            message = data.decode()
            addr = writer.get_extra_info('peername')[1]

            if(message == ''):
                self.current_cores = self.current_cores - total_requested_by_this_endpoint
                print (addr, ": connection lost; relinquishing", total_requested_by_this_endpoint, "cores back to the scheduler")
                return


            #print(f"Received {message!r} from {addr!r}")
            if (message[-1] == '\n'):
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
                writer.write(str(str(numcores) + ",R\n").encode())
                end_time = time.time()
                print(addr, "releases", numcores, "cores for", rpc_type, self.current_cores, "are in use")
                print(rpc_type, "took", end_time - start_time)


            if (message_type == "A"): # acquire some cores
                rpc_type = parsed[2]

                while (numcores + self.current_cores > self.total_cores):
                    print(addr, "requests", numcores, "but only", self.total_cores - self.current_cores, "are available")
                    try:
                        data = await asyncio.wait_for(reader.read(128),timeout=1)
                        message = data.decode()

                        if(message == ''):
                            self.current_cores = self.current_cores - total_requested_by_this_endpoint
                            print (addr, ": connection lost; relinquishing", total_requested_by_this_endpoint, "cores back to the scheduler")
                            return
                    except (asyncio.exceptions.CancelledError, asyncio.exceptions.TimeoutError):
                        print (addr, "connection active, still holding")
                        pass

                self.current_cores = self.current_cores + numcores
                total_requested_by_this_endpoint += numcores
                print(addr, "granted", numcores, "core[s]; now for", rpc_type, self.current_cores, "cores are in use")
                writer.write(str(str(numcores) + ",G\n").encode())
                start_time = time.time()

            await writer.drain()

#    print("Close the connection")
#    writer.close()



async def main():
    ctx = CoreCounter(total_cores=1024)
    server = await asyncio.start_server(ctx.handle_echo, '127.0.0.1', 8888)

    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    #print(f'Serving on {addrs}')

    async with server:
        await server.serve_forever()

asyncio.run(main())