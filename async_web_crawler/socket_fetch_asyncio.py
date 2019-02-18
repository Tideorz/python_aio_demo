#!/usr/env/bin python
import socket
import re
import aiohttp
import asyncio

from selectors import DefaultSelector, EVENT_WRITE, EVENT_READ
try:
    from asyncio import JoinableQueue as Queue
except ImportError:
    # In Python 3.5, asyncio.JoinableQueue is
    # merged into Queue.
    from asyncio import Queue
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse


class Fetcher(object):
    def __init__(self, url, web_crawler):
        self.url = url
        self.response = b''
        self.web_crawler = web_crawler

    @asyncio.coroutine
    def connect(self):
        response_coro = yield from self.web_crawler.session.get(self.url, allow_redirects=False)
        self.response = yield from response_coro.text()
        self.parse_response()

        yield from response_coro.release()

    def parse_response(self):
        self.web_crawler.links_visited.add(self.url)
        for url in re.findall('<a href="([^"]+).+">', str(self.response)):
            if url[0] == '/':
                url = self.url + url
            url = url.rstrip('/')
            pattern = re.compile('https?')
            if pattern.match(url) and url not in self.web_crawler.links_visited:
                #and len(self.web_crawler.links_visited) < self.web_crawler.max_requests):
                self.web_crawler.queue.put_nowait(url)
        # log current link
        print(self.url)

        
class WebCrawler(object):
    def __init__(self, url, max_requests, loop, max_coroutines=100):
        self.url = url
        self.max_requests = max_requests
        self.links_visited = set() 
        self.max_coroutines = max_coroutines
        self.queue = Queue()
        self.loop = loop

    @asyncio.coroutine
    def work(self):
        while True:
            url = yield from self.queue.get()
            fetcher = Fetcher(url, self)
            yield from fetcher.connect()
            self.queue.task_done()

    @asyncio.coroutine
    def web_crawler(self):
        self.queue.put_nowait(self.url)
        self.session = aiohttp.ClientSession(loop=self.loop)
        workers = [asyncio.Task(self.work()) for _ in range(self.max_coroutines)]
        yield from self.queue.join()
        for worker in workers:
            worker.cancel()
        yield from self.session.close()


if __name__ == '__main__':
    link = 'http://www.baidu.com'
    event_loop = asyncio.get_event_loop()
    wc = WebCrawler(link, 30, event_loop)
    event_loop.run_until_complete(wc.web_crawler())
