import socket
import ssl

class URL : 
    def __init__(self, url):
        if url[0][:4] == "data" :
            directive = ' '.join(url)
            self.scheme, directive= directive.split(":", 1)
            directive, self.path = directive.split(",", 1)
            return
        schemes = ["http", "https", "file"]
        self.scheme, url = url.split("://", 1)
        assert self.scheme in schemes
        if self.scheme == "file" : 
            self.path = 'C:' + url
            return 
        if self.scheme == "http": 
            self.port = 80
        elif self.scheme == "https": 
            self.port = 443
        if '/' not in url : 
            url = url + '/'
        self.host, url = url.split('/', 1)
        self.path = '/' + url
        if ":" in self.host : 
            self.host, port = self.host.split(":", 1)
            self.port = int(port)
        

    def request(self) : 
        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto= socket.IPPROTO_TCP
        )
        s.connect((self.host, self.port))
        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)
        request = f"GET {self.path} HTTP/1.1\r\n"
        request += f"Host: {self.host}\r\n"
        request += "Connection: close\r\n"
        request += "User-Agent: something\r\n"
        request += "\r\n"
        s.send(request.encode('utf8'))
        response = s.makefile("r", encoding="utf8", newline="\r\n")
        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)
        response_headers = {}
        while True : 
            line = response.readline()
            if line == "\r\n" : break
            header, value = line.split(':', 1)
            response_headers[header.casefold()] = value.strip()

        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers
        content = response.read()
        s.close()

        return content


def show(body): 
    in_tag = False
    for c in body: 
        if c == "<" :
            in_tag = True
        elif c == ">" :
            in_tag = False
        elif not in_tag : 
            print(c, end="")


def load(url):
    if url.scheme in ["http", "https"]:
        body = url.request()
        show(body)
    elif url.scheme == "file" : 
        f = open(url.path, 'r')
        print(f.read())
    elif url.scheme == "data" :
        body = url.path 
        show(body)

if __name__ == "__main__":
    import sys
    path = "file:///Users/surfa/OneDrive/Bureau/git_repos/web_browser/file_to_open.txt"
    if len(sys.argv) < 2 : 
        load(URL(path))
    elif len(sys.argv) > 2 and sys.argv[1][:4]=="data": 
        new_url = []
        for el in sys.argv[1:] : 
            new_url.append(el)
        load(URL(new_url))
    else : 
        load(URL(sys.argv[1]))



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