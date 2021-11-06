from types import FunctionType
import aiohttp, asyncio
from .websocket import WebSocket
from .object import Note, ClientUser
from misskey import Misskey

class Client:

    def __init__(self, host:str = 'misskey.io', timeline:str = 'homeTimeline'):
        self.host:str = host
        self.timeline:str = timeline
        self._ws_cls = None
        self.token:str = None
        self._listeners:list = []
        self._listener_counter:int = 0
        self.loop = asyncio.get_event_loop()
        self.api:Misskey = Misskey(address=self.host, i=self.token)
        self.user:ClientUser = None

    async def change_timeline(self, t:str):
        await self.ws.send_json({
            'type': 'disconnect',
            'body': {
                'id': self.timeline
            }
        })
        await self.ws.send_json({
            'type': 'connect',
            'body': {
                'channel': t
            }
        })
        self.timeline = t

    def run(self, token: str):
        self._ws_cls = WebSocket(url=f'https://{self.host}/streaming?i=' + token)
        self.token = token
        self.api.token = token
        self.loop.run_until_complete(self._ws_process())
    
    async def _ws_process(self):
        async with self._ws_cls.create_connection() as ws:
            self.ws = ws
            await ws.send_json({
                'type': 'connect',
                'body': {
                    'channel': self.timeline,
                    'id': self.timeline
                }
            })
            self.user = ClientUser(self, self.api.i())
            self.dispatch('ready')
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = msg.json()
                    print(data)
                    if data['type'] == 'channel':
                        if data['body']['id'] == self.timeline:
                            if data['body'].get('type') == 'note':
                                note_json = data['body']['body']
                                try:
                                    note = Note(self, note_json)
                                    self.dispatch('note', note)
                                except Exception as e:
                                    print(e)

                    

    def dispatch(self, event_name:str, *args):
        listeners = [fn for fn in self._listeners if fn['event'] == event_name]
        for l in listeners:
            asyncio.create_task(l['func'](*args))
    
    def register_event(self, event_name:str, listener_id:str = None, func:FunctionType = None):
        if not asyncio.iscoroutinefunction(func):
            raise TypeError('function is not coroutine')
        self._listeners.append({
            'event': event_name,
            'listener_id':  listener_id if listener_id else f'EVL{self._listener_counter:09}',
            'func': func
        })
        self._listener_counter+=1
    
    def unregister_event(self, listener_id:str):
        li = [x for x in self._listeners if x['listener_id']==listener_id]
        if li:
            for l in li:
                self._listeners.remove(l)