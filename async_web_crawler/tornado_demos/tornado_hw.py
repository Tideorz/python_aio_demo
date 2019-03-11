#!/usr/bin/env python

import tornado.web
from tornado.web import url
import tornado.ioloop


class MiddleWare(object):
    def process_request(self, handler):
        pass

    def process_response(self, handler):
        pass


class CheckLoginMiddleware(MiddleWare):
    def process_request(self, handler):
        self.is_login(handler)
    
    def is_login(self, handler):
        pwd = handler.get_arguments("pwd", None)
        if not pwd:
            raise Exception("No password")
        return True


class BaseHandler(tornado.web.RequestHandler):
    def initialize(self, db, middleware_list):
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
        self.write('use reverse_url to find Content in StoryHandler, story_id is %s, db = %s ' % (id, self.db)) 


def get_middleware_list():
    return [CheckLoginMiddleware, ]


def make_app():
    return tornado.web.Application([
       url(r"/", HelloWorldHandler),
       url(r"/story/([0-9]+)", StoryHandler, dict(db='test_db', middleware_list=get_middleware_list()), name="story"),
    ])


if __name__ == '__main__':
    app = make_app()
    app.listen(12345)
    tornado.ioloop.IOLoop.current().start()
