import aiohttp

class WebSocket:
    
    def __init__(self, url:str):
        self.cls = aiohttp.ClientSession()
        self.url = url
    
    def create_connection(self):
        return self.cls.ws_connect(self.url)