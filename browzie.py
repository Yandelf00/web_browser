import socket
import ssl
import certifi
import time
import gzip
import tkinter

WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18
NLINE = 22
SCROLL_STEP = 100


class Cache : 
    def __init__(self) :
        self.cache = {}  
    
    def set_cache(self, url, max_age, content):
        self.cache[url] = {
            "content" : content,
            "expires" : time.time() + float(max_age)
        }
    
    def get_cache(self, url) :
        entry = self.cache.get(url)
        if entry and entry['expires'] > time.time():
            return entry['content'] 
        return None

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

def lex(body): 
    if type(body)!= str:
        body = body.decode("utf8")
    
    text = ""
    in_tag = False
    is_entity =  False
    the_entity = ""
    for c in body: 
        if c == "<" :
            in_tag = True
        elif c == ">" :
            in_tag = False
        elif is_entity :
            the_entity+= c
            if len(the_entity) == 4:
                if the_entity== "&lt;":
                    text += "<"
                    is_entity = False
                    the_entity = ""
                elif the_entity == "&gt;":
                    text += ">"
                    is_entity = False
                    the_entity = ""
                else : 
                    text += the_entity
                    is_entity= False
                    the_entity= ""
        elif not in_tag and not is_entity: 
            if c == "&":
                is_entity = True
                the_entity = "&"
            else :
                text += c
    if len(the_entity)>0:
        text += the_entity

    return text


def layout(text):
    display_list = []
    cursor_x, cursor_y = HSTEP, VSTEP
    for c in text : 
        display_list.append((cursor_x, cursor_y, c))
        cursor_x += HSTEP
        if cursor_x > WIDTH - HSTEP:
            cursor_y += VSTEP 
            cursor_x = HSTEP
        if c == '\n' : 
            cursor_x = HSTEP
            cursor_y += NLINE 
    return display_list 

class Browser : 
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window,
            width=WIDTH,
            height=HEIGHT
        )
        self.canvas.pack()
        self.scroll = 0
        self.window.bind("<Down>", self.scrolldown)

    def load(self, url):
        if url.scheme in ["http", "https"]:
            body = url.request()
            if body is not None :
                text = lex(body)
                self.display_list = layout(text)
                self.draw()
            else : 
                print("there is no body to show")
        elif url.scheme in ["view-source:http","view-source:https"]:
            body = url.request()
            if body is not None:
                print(body.decode("utf8"))
            else:
                print("there is no body to show")
        elif url.scheme == "file" : 
            f = open(url.path, 'r')
            body = f.read()
            if body is not None:
                print(lex(body))
            else:
                print("there is no body to show")
        elif url.scheme == "data" :
            body = url.path 
            if body is not None:
                print(lex(body))
            else:
                print("there is no body to show")
    
    def draw(self):
        self.canvas.delete("all")
        for x, y, c in self.display_list:
            if y > self.scroll + HEIGHT : continue
            if y + VSTEP < self.scroll : continue
            self.canvas.create_text(x, y - self.scroll, text=c)

    def scrolldown(self, e) : 
        self.scroll += SCROLL_STEP
        self.draw()


if __name__ == "__main__":
    import sys
    path = "file:///Users/surfa/OneDrive/Bureau/git_repos/web_browser/file_to_open.txt"
    if len(sys.argv) < 2 : 
        Browser().load(URL(path))
    elif len(sys.argv) > 2 and sys.argv[1][:4]=="data": 
        new_url = []
        for el in sys.argv[1:]: 
            new_url.append(el)
        Browser().load(URL(new_url))
    else : 
        Browser().load(URL(sys.argv[1]))

    tkinter.mainloop()




"""
    content_length = int(response_headers.get("content-length", 0))
    content = response.read(content_length)
    if response_headers.get('content-encoding')=='gzip':
        content = gzip.decompress(content)

    max_age = self.is_cacheable(response_headers)
    if max_age is not None :
        URL.cache.set_cache(self.path, max_age, content) 

    return content
"""




"""
    form of the URL : 
    http://example.org/index.html
    http = Scheme (how to get the into)
    example.org = Hostname (where to get the info)
    /index.html = path (what info to get)

___________________________________________________

    form of a GET request : 
    GET /index.html HTTP/1.0
    Host: example.org

    GET = method
    /index.html = path
    HTTP/1.0 = http version 
    Host = header 
    example.org = value

_____________________________________________________

    form of a server response : 
    HTTP/1.0 200 OK 

    Age: 545933
    Cache-Control: max-age=604800
    Content-Type: text/html; charset=UTF-8
    Date: Mon, 25 Feb 2019 16:49:28 GMT
    Etag: "1541025663+gzip+ident"
    Expires: Mon, 04 Mar 2019 16:49:28 GMT
    Last-Modified: Fri, 09 Aug 2013 23:54:35 GMT
    Server: ECS (sec/96EC)
    Vary: Accept-Encoding
    X-Cache: HIT
    Content-Length: 1270
    Connection: close

    HTTP/1.0 = HTTP version
    200 = response code
    OK = response description
"""