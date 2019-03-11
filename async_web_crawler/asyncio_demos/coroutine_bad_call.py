#!/usr/bin/env python
import asyncio

async def divide_async(x, y):
    return x/y

async def good_call_async():
    await divide_async(1, 0)

def divide_yield(x, y):
    yield from x/y

def good_call_yield():
    yield from divide_yield(1, 0)

def bad_call_by_non_coroutine():
    a = yield from divide_yield(1, 0)
    yield a

if __name__ == '__main__':
    #asyncio.run(good_call_async())
    #asyncio.run(good_call_yield())
    bad_call_by_non_coroutine()
