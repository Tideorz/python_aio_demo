#!/usr/bin/env python
def a():
    yield 1
    yield 2
    return 'hello'

g = a()

g.send(None)
g.send(None)

def b():
    try:
        g.send(None)        
    except StopIteration as e:
        print(e.value)

b()
