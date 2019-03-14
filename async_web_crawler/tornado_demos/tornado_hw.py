#!/usr/bin/env python

import tornado.ioloop
import tornado.web

from tornado.template import Template
from tornado.web import url, HTTPError


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
            #handler.render()


class CheckPasswordMiddleware(MiddleWare):
    def process_request(self, handler):
        self.exist_password(handler)
    
    def exist_password(self, handler):
        pwd = handler.get_argument("pwd", "")
        if not pwd:
            raise Exception("No password")
        return True


class BaseHandler(tornado.web.RequestHandler):
    def initialize(self, db=None, middleware_list=[]):
        self.db = db
        self.middleware_list = middleware_list

    def prepare(self):
        for middleware in self.middleware_list:
            middleware.process_request(self)


class HelloWorldHandler(BaseHandler):
    def get(self):
        self.write("<a href=%s>story</a>" % self.reverse_url("story", 1))


class StoryHandler(BaseHandler):
    def get(self, id):
        self.write('story_id is %s, db = %s ' % (id, self.db)) 

    def write_error(self, status_code, **kwargs):
        exc_cls, exc_instance, trace = kwargs.get("exc_info")
        if status_code != 200:
            self.set_status(status_code)
            self.write({"msg": str(exc_instance)})


class LoginErrorHandler(tornado.web.RequestHandler):
    def get(self):
        pass


def get_middleware_list():
    return [CheckPasswordMiddleware(), CheckLoginMiddleware(), ]


def url_patterns():
    return [
       url(r"/", HelloWorldHandler),
       url(r"/story/([0-9]+)", StoryHandler, dict(db='test_db', middleware_list=get_middleware_list()), name="story"),
       url(r"/login_error", LoginErrorHandler, name="login_error")
    ]


def make_app():
    return tornado.web.Application(url_patterns())


if __name__ == '__main__':
    app = make_app()
    app.listen(12345)
    tornado.ioloop.IOLoop.current().start()
