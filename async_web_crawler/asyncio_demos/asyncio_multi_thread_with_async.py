#/usr/bin/env python

import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def blocking_io():
    with open('/dev/urandom', 'rb') as fobj:
        return fobj.read(100)

async def main():
    loop = asyncio.get_running_loop()
    # execute blocking_io in event loop thread
    result = await loop.run_in_executor(None, blocking_io)
    print("main thread pool: ", result)

    with ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, blocking_io)
        print("custom thread pool: ", result)

if __name__ == '__main__':
    asyncio.run(main())
