#!/usr/env/bin python
import socket
import re

from selectors import DefaultSelector, EVENT_WRITE, EVENT_READ

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

selector = DefaultSelector() # Linux system will use epoll()


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
        selector.register(self.sock.fileno(), EVENT_WRITE, self.connect_callback)

    def connect_callback(self, event_key, event_mask):
        selector.unregister(event_key.fd) # Done connecting
        # send GET request
        request = 'GET {0} HTTP/1.0\r\nHost: {1}\r\n\r\n'.format(self.url, self.hostname)
        request = bytearray(request, 'utf8')
        self.sock.send(request)  
        selector.register(self.sock.fileno(), EVENT_READ, self.read_response_callback)

    def read_response_callback(self, event_key, event_mask):
        # get response, set chunk buffer as 4KB
        chunk = self.sock.recv(4096)    
        if chunk:
            self.response += chunk
        else: 
            selector.unregister(event_key.fd)  # Done reading.
            # parse respones 
            self.parse_response()

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
                    fetcher.connect()
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
        fetcher.connect()
        while True:
            if self.stop_event_loop:
                break
            events = selector.select()
            for event_key, event_mask in events:
                callback = event_key.data
                callback(event_key, event_mask)

if __name__ == '__main__':
    link = 'http://www.baidu.com'
    wc = WebCrawler(link, 30)
    wc.web_crawler() 
