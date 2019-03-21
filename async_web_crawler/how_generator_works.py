#!/usr/env/bin python
import dis

def func_test():
    print('zhc')

def func_return():
    return 'zhc'

def gen_a():
    val_a = yield 'zhc'
    print(val_a + '1993')
    val_b = yield 'abc'
    yield 'test'

def gen_c():
    val_a = yield func_test()
    print(val_a)

def gen_d():
    val_a = yield func_return()
    print(val_a)

def gen_e():
    val_b = yield
    val_c = val_b * 10
    print(val_c)

class CancelError(Exception):
    pass

def gen_f():
    try:
        a = yield "I don't want to continue to run next line, jump out of gen_f()!!!"
        if a == "= =":
            yield "Fuck off!!! (jump into gen_f() again)"
    except CancelError:
        print("you throw a CancelError exception into generator")  

def dis_method(f):
    dis.dis(gen_f)

if __name__ == '__main__':
    try:
        a = gen_f()
        dis_method(gen_f)
        print(next(a))
        print(a.gi_frame.f_lasti)
        tell_gen_f = input('What you to tell to the method gen_f(): ')
        if tell_gen_f == 'cancel':
            a.throw(CancelError('test'))
            print(a.gi_frame.f_lasti)
        return_value = a.send(tell_gen_f)
        print(a.gi_frame.f_lasti)
        print(return_value)
        #next(a)
    except StopIteration as e:
        print("hit the end of generator and raise StopIteration")
        print(a.gi_frame.f_lasti)
