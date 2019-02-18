#!/usr/env/bin python
import socket
import re

from selectors import DefaultSelector, EVENT_WRITE, EVENT_READ

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

selector = DefaultSelector() # Linux system will use epoll()


class Task():
    def __init__(self, gen):
        self.gen = gen
        f = Future()
        f.set_result(None)
        self.step(f)

    def step(self, future):
        try:
            f = self.gen.send(future.result)
        except StopIteration:
            return
        f.add_done_callback(self.step)


class Future():
    def __init__(self):
        self.result = None
        self._callback = [] 

    def set_result(self, result):
        self.result = result
        for func in self._callback: 
            func(self)

    def add_done_callback(self, func):
        self._callback.append(func)


class Fetcher(object):
    def __init__(self, url, web_crawler):
        self.url = url
        self.response = b''
        # set socket as non-blocking 
        self.sock = socket.socket()
        self.sock.setblocking(False)
        self.web_crawler = web_crawler
        
    def connect(self):
        # parse url
        parse_result = urlparse(self.url)
        self.hostname = parse_result.netloc.split(':')[0]
        try:
            self.sock.connect((self.hostname, 80))
        except BlockingIOError:
            pass
        # bind socket with EVENT_WRITE, means we're checking
        # when the socket is writable
        f = Future() 

        def connect_callback():
            f.set_result(None) 
        selector.register(self.sock.fileno(), EVENT_WRITE, connect_callback)

        yield f 

        selector.unregister(self.sock.fileno()) # Done connecting
        # send GET request
        request = 'GET {0} HTTP/1.0\r\nHost: {1}\r\n\r\n'.format(self.url, self.hostname)
        request = bytearray(request, 'utf8')
        self.sock.send(request)
    
        # get response, set chunk buffer as 4KB
        while True:
            f = Future()
            def read_response_callback():
                f.set_result(self.sock.recv(4096))
            selector.register(self.sock.fileno(), EVENT_READ, read_response_callback)
            chunk = yield f    
            selector.unregister(self.sock.fileno())  # Done reading.
            if chunk:
                self.response += chunk
            else: 
                # parse respones 
                self.parse_response()
                break

    def parse_response(self):
        self.web_crawler.links_visited.append(self.url)
        # remove url for links_to_visit
        if self.url in self.web_crawler.links_to_visit:
            self.web_crawler.links_to_visit.remove(self.url)
        for url in re.findall('<a href="([^"]+)">', str(self.response)):
            if url[0] == '/':
                url = self.url + url
            url = url.rstrip('/')
            pattern = re.compile('https?')
            if pattern.match(url) and url not in self.web_crawler.links_visited:
                self.web_crawler.links_to_visit.append(url)
        # log current link
        print(self.url)
        if len(self.web_crawler.links_visited) < self.web_crawler.max_requests:
            left_requests = self.web_crawler.max_requests - len(self.web_crawler.links_visited)
            for i in range(0, left_requests):
                try:
                    new_url = self.web_crawler.links_to_visit.pop()
                    fetcher = Fetcher(new_url, self.web_crawler)
                    gen = fetcher.connect()
                    Task(gen)
                except IndexError:
                    break
        else:
            self.web_crawler.stop_event_loop = True

class WebCrawler(object):
    def __init__(self, url, max_requests):
        self.url = url
        self.max_requests = max_requests
        self.links_to_visit = [self.url]
        self.links_visited = []
        self.stop_event_loop = False

    def web_crawler(self):
        # connect to the initial url, and start event loop
        fetcher = Fetcher(self.url, self)
        gen = fetcher.connect()
        Task(gen)
        while True:
            if self.stop_event_loop:
                break
            events = selector.select()
            for event_key, event_mask in events:
                callback = event_key.data
                callback()

if __name__ == '__main__':
    link = 'http://www.baidu.com'
    wc = WebCrawler(link, 30)
    wc.web_crawler() 
