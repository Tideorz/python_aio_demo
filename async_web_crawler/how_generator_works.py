#!/usr/env/bin python

def func_test():
    print 'zhc'

def func_return():
    return 'zhc'

def gen_a():
    val_a = yield 'zhc'
    print val_a + '1993'
    val_b = yield 'abc'
    yield 'test'

def gen_c():
    val_a = yield func_test()
    print val_a

def gen_d():
    val_a = yield func_return()
    print val_a

def gen_e():
    val_b = yield 10
    val_c = val_b * 10

def gen_f():
    val_b = yield
    val_c = val_b * 10
    print val_c

def gen_g():
    a = yield "I don't want to continue to run next line"
    if a == "You must do it = =":
        yield "Fuck off"

if __name__ == '__main__':
    a = gen_a()
    import dis
    dis.dis(gen_a)
    next(a)
    print a.gi_frame.f_lasti
    a.send('zhn')
