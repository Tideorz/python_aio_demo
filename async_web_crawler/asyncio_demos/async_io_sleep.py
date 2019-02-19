#!/usr/bin/env python

import asyncio

#loop = asyncio.get_event_loop()

async def hello():
    print('hello')
    await asyncio.sleep(3)
    print('world')

async def main():
    await hello()

async def mul_hello():
    workers = [asyncio.Task(hello()) for _ in range(10)]
    # "task" can now be used to cancel or
    # can simply be awaited to wait until it is complete:
    for worker in workers:
        await worker

if __name__ == '__main__':
    #loop.run_until_complete(main())
    #loop.run_until_complete(mul_hello())
    asyncio.run(main())
    asyncio.run(mul_hello())
