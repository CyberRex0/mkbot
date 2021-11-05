import datetime

class User:
    def __init__(self, _state, json: dict):
        self.id = json['id']
        self.screen_name = json['name']
        self.username = json['username']
        self.host = json['host']
        self.avatar_url = json['avatarUrl']
        self.avatar_blurhash = json['avatarBlurhash']
        self.avatar_color = json['avatarColor']
        if json.get('instance'):
            self.instance = Instance(_state, json['instance'])
        else:
            self.instance = None
        self.emojis = [Emoji(_state, x) for x in json['emojis']]
        self.online_status = json['onlineStatus']
        self.remote = (_state.host != self.host)

class Instance:
    def __init__(self, _state, json: dict):
        self.name = json['name']
        self.software_name = json['softwareName']
        self.software_version = json['softwareVersion']
        self.icon_url = json['iconUrl']
        self.favicon_url = json['faviconUrl']
        self.theme_color = json['themeColor']

class Emoji:
    def __init__(self, _state, json: dict):
        self.name = json['name']
        self.url = json['url']

class File:
    def __init__(self, _state, json: dict):
        self.id = json['id']
        self.created_at = datetime.datetime.fromisoformat(json['createdAt'][:-1])
        self.name = json['name']
        self.url = json.get('url') or json.get('uri')
        self.thumbnail_url = json['thumbnailUrl']
        self.size = json['size']
        self.type = json['type']
        self.comment = json['comment']
        self.is_sensitive = json['isSensitive']
        self.blurhash = json['blurhash']
        self.properties = FileProperties(_state, json['properties'])
        self.folder_id = json['folderId']
        self.folder = json['folder']
        self.user_id = json['userId']
        self.user = None
        if json['user']:
            self.user = User(_state, json['user'])

class FileProperties:
    def __init__(self, _state, json: dict):
        self.width = json.get('width')
        self.height = json.get('height')

class Note:
    def __init__(self, _state, json: dict):
        self.id = json['id']
        self.created_at = datetime.datetime.fromisoformat(json['createdAt'][:-1])
        self.author = User(_state, json['user'])
        self.text = json.get('text')
        self.cw = json.get('cw')
        self.visibility = json['visibility']
        self.renote_count = json['renoteCount']
        self.replies_count = json['repliesCount']
        self.reactions = json['reactions']
        self.emojis = [Emoji(_state, x) for x in json['emojis']]
        self.files = [File(_state, x) for x in json['files']]
        self.file_ids = json['fileIds']
        self.reply_id = json['replyId']
        self.renote_id = json['renoteId']
        self.mentions = json.get('mentions') or []
        self.url = json.get('url') or json.get('uri')
        self._state = _state
    
    async def reply(self, *args, **kwargs):
        d = self._state.api.notes_create(reply_id=self.id, *args, **kwargs)
        return Note(self._state, d)
    
    async def renote(self):
        d = self._state.api.notes_create(renote_id=self.id)