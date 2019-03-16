#!/usr/bin/env python

import tornado.ioloop
import tornado.template
import tornado.web

from tornado.web import url, HTTPError
from derpconf.config import Config


class MiddleWare(object):
    def process_request(self, handler):
        pass

    def process_response(self, handler):
        pass

class CheckLoginMiddleware(MiddleWare):
    def process_request(self, handler):
        self.is_login(handler)

    def is_login(self, handler):
        is_login = handler.get_argument("login", None)
        if not is_login:
            handler.set_status(403)
            handler.render('403.html')


class CheckPasswordMiddleware(MiddleWare):
    def process_request(self, handler):
        self.exist_password(handler)
    
    def exist_password(self, handler):
        pwd = handler.get_argument("pwd", "")
        if not pwd:
            raise Exception("No pwd param, please add ?pwd=1 in your URL")
        return True


class BaseHandler(tornado.web.RequestHandler):
    def initialize(self, conf, middleware_list=[]):
        self.conf = conf
        self.middleware_list = middleware_list

    def prepare(self):
        for middleware in self.middleware_list:
            middleware.process_request(self)

    def write_error(self, status_code, **kwargs):
        exc_cls, exc_instance, trace = kwargs.get("exc_info")
        if status_code != 200:
            self.set_status(status_code)
            self.write({"msg": str(exc_instance)})



class HelloTornadoHandler(BaseHandler):
    def get(self):
        self.write("<a href=%s>story</a>" % self.reverse_url("story", 1))


class StoryHandler(BaseHandler):
    def get(self, id):
        self.write('story_id is %s, db = %s ' % (id, self.conf.DATABASE)) 


class LoginErrorHandler(tornado.web.RequestHandler):
    def get(self):
        pass


def get_middleware_list():
    return [CheckPasswordMiddleware(), CheckLoginMiddleware(), ]


def get_handlers(conf):
    DEFAULT_CONF = {'conf': conf, 'middleware_list': get_middleware_list()}

    return [
        url(r"/", HelloTornadoHandler, DEFAULT_CONF),
        url(r"/story/([0-9]+)", StoryHandler, DEFAULT_CONF, name="story"),
        url(r"/login_error", LoginErrorHandler, DEFAULT_CONF, name="login_error"),
    ]


class HelloTornadoApplication(tornado.web.Application):
    def __init__(self, handlers, settings):
        super(HelloTornadoApplication, self).__init__(handlers, settings)


def make_app(conf, handlers):
    return HelloTornadoApplication(
        handlers=handlers,
        settings={'template_path': conf.TEMPLATE_DIR},
    )


if __name__ == '__main__':
    conf = Config.load('settings.conf')
    app = make_app(conf, get_handlers(conf))
    app.listen(conf.PORT)
    tornado.ioloop.IOLoop.current().start()
