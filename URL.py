from Cache import Cache
import socket
import ssl
import certifi
import gzip

class URL : 
    cache = Cache()

    def __init__(self, url):
        if url[0][:4] == "data" :
            directive = ' '.join(url)
            self.scheme, directive= directive.split(":", 1)
            directive, self.path = directive.split(",", 1)
            return
            
        schemes = ["http", "https", "file", "view-source:http", "view-source:https"]
        self.scheme, url = url.split("://", 1)
        assert self.scheme in schemes
        if self.scheme == "file" : 
            self.path = 'C:' + url
            return 
        if self.scheme == "http" or self.scheme == "view-source:http": 
            self.port = 80
        elif self.scheme == "https" or self.scheme == "view-source:https": 
            self.port = 443
        if '/' not in url : 
            url = url + '/'
        self.host, url = url.split('/', 1)
        self.path = '/' + url
        if ":" in self.host : 
            self.host, port = self.host.split(":", 1)
            self.port = int(port)
        self.socket = None
        
    def connect_socket(self):
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto= socket.IPPROTO_TCP
        )
        s.connect((self.host, self.port))
        if self.scheme == "https" or self.scheme == "view-source:https":
            ctx = ssl.create_default_context(cafile=certifi.where())
            s = ctx.wrap_socket(s, server_hostname=self.host)
        return s

    def request_form(self, path, host):
        request = f"GET {path} HTTP/1.1\r\n"
        request += f"Host: {host}\r\n"
        request += "Connection: keep-alive\r\n"
        request += "User-Agent: something\r\n"
        request += "Accept-Encoding: gzip\r\n"
        request += "\r\n"
        return request

    def define_headers(self, response):
        response_headers = {}
        while True : 
            line = response.readline().decode("utf8")
            if line == "\r\n" : break
            header, value = line.split(':', 1)
            response_headers[header.casefold()] = value.strip()
        return response_headers
    
    def is_cacheable(self, response_headers) :
        cache_control = response_headers.get('cache-control')
        if cache_control :
            directives = [d.strip() for d in cache_control.split(",")]
            for directive in directives :
                if directive == "no-store":
                    return None 
                if directive.startswith("max-age"):
                    _, max_age = directive.split('=')
                    return int(max_age)
        return None

    def read_chunked(self, response):
        body = b""
        while True:
            chunk_size_line = response.readline().strip()
            chunk_size = int(chunk_size_line, 16)
            if chunk_size == 0:
                break
            chunk = response.read(chunk_size)
            body += chunk
            response.readline()  # Read the trailing \r\n
        return body

    def request(self, max_redirects = 10) : 
        cached_content = URL.cache.get_cache(self.path)
        if cached_content : 
            return cached_content

        redirects_followed = 0 
        while redirects_followed < max_redirects : 
            if self.socket is None : 
                self.socket = self.connect_socket()
            request = self.request_form(self.path, self.host)
            self.socket.send(request.encode('utf8'))
            response = self.socket.makefile("rb", newline="\r\n")
            statusline = response.readline().decode('utf8')
            version, status, explanation = statusline.split(" ", 2)
            response_headers = self.define_headers(response) 
            status = int(status)

            if status >= 300 and status < 400 :
                location = response_headers.get("location")
                if location.startswith('/'):
                    self.path = location
                else : 
                    self.__init__(location)
                    self.socket = self.connect_socket()
                redirects_followed += 1               
                continue
            if response_headers.get('transfer-encoding') == 'chunked':
                content = self.read_chunked(response)
            else : 
                content_length = int(response_headers.get("content-length", 0))
                content = response.read(content_length)
            
            if response_headers.get("content-encoding") == "gzip":
                content = gzip.decompress(content)


            max_age = self.is_cacheable(response_headers)
            if max_age is not None :
                URL.cache.set_cache(self.path, max_age, content) 
            return content
        raise Exception("too many redirects")