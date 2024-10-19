import time


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