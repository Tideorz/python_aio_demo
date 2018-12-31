#!/usr/env/bin python
import concurrent.futures
import socket
import re

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

class WebCrawler(object):
    def __init__(self, url, max_requests=10, pool_size=5):
        self.url = url
        self.max_requests = max_requests
        self.links_to_visit = [self.url]
        self.links_visited = []
        self.pool_size = pool_size

    def fetch(self, url):
        # parse url
        parse_result = urlparse(url)
        hostname = parse_result.netloc
        # create socket
        sock = socket.socket()
        # generate a connection
        sock.connect((hostname, 80))
        # send GET request
        request = 'GET {0} HTTP/1.0\r\nHost: {1}\r\n\r\n'.format(url, hostname)
        request = bytearray(request, 'utf8')
        sock.send(request)
        # get response, set chunk buffer as 4KB
        response = b''
        chunk = sock.recv(4096)
        while chunk:
            response += chunk
            chunk = sock.recv(4096)
        return response 

    def parse_response(self, response, current_link):
        self.links_visited.append(current_link)
        for url in re.findall('<a href="([^"]+)">', str(response)):
            if url[0] == '/':
                url = current_link + url
            url = url.rstrip('/')
            pattern = re.compile('https?')
            if pattern.match(url) and url not in self.links_visited:
                self.links_to_visit.append(url)
        # log current link
        print(current_link)

    def web_crawler(self):
        # python3 future multi-processing
        with concurrent.futures.ProcessPoolExecutor(self.pool_size) as executor:
            while len(self.links_to_visit) > 0 and len(self.links_visited) < self.max_requests:
                # limit the requests
                left_requests = self.max_requests - len(self.links_visited)
                future_to_url = {
                    executor.submit(self.fetch, url): url for url in self.links_to_visit[:left_requests]
                }
                for future in concurrent.futures.as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        response = future.result()
                    except Exception as exc:
                        print('%r generated an exception: %s' % (url, exc))
                    else:
                        self.parse_response(response, url)

if __name__ == '__main__':
    link = 'http://www.baidu.com'
    wc = WebCrawler(link, 10, 5)
    wc.web_crawler() 
